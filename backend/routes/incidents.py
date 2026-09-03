from fastapi import APIRouter, HTTPException

from ai.classifier import classify_incident
from ai.duplicate import is_duplicate
from ai.priority import priority_for_severity
from ai.recommendation import recommend_action
from ai.severity import estimate_severity
from database import get_connection, utc_now
from models import Incident, IncidentAnalysis, IncidentCreate, IncidentUpdate


router = APIRouter()


def missing(incident_id: int) -> HTTPException:
	return HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Incident with id {incident_id} does not exist"})


@router.post("", status_code=201)
def create_incident(incident: IncidentCreate):
	values = incident.model_dump()
	with get_connection() as connection:
		existing_rows = connection.execute("SELECT * FROM incidents").fetchall()
		for existing_row in existing_rows:
			if is_duplicate(values, dict(existing_row)):
				return {"duplicate": True, "message": "Similar incident already exists", "incident_id": existing_row["id"]}
		severity = estimate_severity(values)
		priority = priority_for_severity(severity)
		values["severity"] = severity
		values["priority"] = priority
		cursor = connection.execute(
			"INSERT INTO incidents (type, description, latitude, longitude, severity, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
			(*values.values(), utc_now()),
		)
		row = connection.execute("SELECT * FROM incidents WHERE id = ?", (cursor.lastrowid,)).fetchone()
	result = dict(row)
	result["classification"] = classify_incident(values["type"], values.get("description") or "")
	result["recommendation"] = recommend_action(result)
	return result


@router.get("", response_model=list[Incident])
def list_incidents():
	with get_connection() as connection:
		rows = connection.execute("SELECT * FROM incidents ORDER BY id").fetchall()
	return [dict(row) for row in rows]


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
	if row is None:
		raise missing(incident_id)
	return dict(row)


@router.put("/{incident_id}", response_model=Incident)
def update_incident(incident_id: int, incident: IncidentUpdate):
	values = incident.model_dump(exclude_unset=True)
	with get_connection() as connection:
		if connection.execute("SELECT id FROM incidents WHERE id = ?", (incident_id,)).fetchone() is None:
			raise missing(incident_id)
		if values:
			assignments = ", ".join(f"{key} = ?" for key in values)
			connection.execute(f"UPDATE incidents SET {assignments} WHERE id = ?", (*values.values(), incident_id))
		row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
	return dict(row)


@router.post("/{incident_id}/analyze", response_model=IncidentAnalysis)
def analyze_incident(incident_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
	if row is None:
		raise missing(incident_id)
	incident_data = dict(row)
	severity = estimate_severity(incident_data)
	return {
		"incident_id": incident_id,
		"classification": classify_incident(incident_data["type"], incident_data.get("description") or ""),
		"severity": severity,
		"priority": priority_for_severity(severity),
		"recommendation": recommend_action({**incident_data, "severity": severity}),
	}
