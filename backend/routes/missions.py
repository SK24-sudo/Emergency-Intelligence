import sqlite3

from fastapi import APIRouter, HTTPException

from database import get_connection, utc_now
from models import Mission, MissionCreate, MissionStatusUpdate, MissionUpdate


router = APIRouter()


def missing(mission_id: int) -> HTTPException:
	return HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Mission with id {mission_id} does not exist"})


@router.post("", response_model=Mission, status_code=201)
def create_mission(mission: MissionCreate):
	try:
		with get_connection() as connection:
			cursor = connection.execute("INSERT INTO missions (incident_id, asset_id, status, created_at) VALUES (?, ?, ?, ?)", (*mission.model_dump().values(), utc_now()))
			row = connection.execute("SELECT * FROM missions WHERE id = ?", (cursor.lastrowid,)).fetchone()
	except sqlite3.IntegrityError:
		raise HTTPException(status_code=400, detail="incident_id and asset_id must reference existing resources")
	return dict(row)


@router.get("", response_model=list[Mission])
def list_missions():
	with get_connection() as connection:
		rows = connection.execute("SELECT * FROM missions ORDER BY id").fetchall()
	return [dict(row) for row in rows]


@router.get("/{mission_id}", response_model=Mission)
def get_mission(mission_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
	if row is None:
		raise missing(mission_id)
	return dict(row)


@router.put("/{mission_id}", response_model=Mission)
def update_mission(mission_id: int, mission: MissionUpdate):
	values = mission.model_dump(exclude_unset=True)
	with get_connection() as connection:
		if connection.execute("SELECT id FROM missions WHERE id = ?", (mission_id,)).fetchone() is None:
			raise missing(mission_id)
		try:
			if values:
				assignments = ", ".join(f"{key} = ?" for key in values)
				connection.execute(f"UPDATE missions SET {assignments} WHERE id = ?", (*values.values(), mission_id))
		except sqlite3.IntegrityError:
			raise HTTPException(status_code=400, detail="incident_id and asset_id must reference existing resources")
		row = connection.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
	return dict(row)


@router.post("/{mission_id}/status")
def update_mission_status(mission_id: int, update: MissionStatusUpdate):
	with get_connection() as connection:
		mission_row = connection.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
		if mission_row is None:
			raise missing(mission_id)
		connection.execute("UPDATE missions SET status = ? WHERE id = ?", (update.status, mission_id))
		if update.latitude is not None or update.longitude is not None:
			asset = connection.execute("SELECT latitude, longitude FROM assets WHERE id = ?", (mission_row["asset_id"],)).fetchone()
			latitude = update.latitude if update.latitude is not None else asset["latitude"]
			longitude = update.longitude if update.longitude is not None else asset["longitude"]
			connection.execute("UPDATE assets SET latitude = ?, longitude = ? WHERE id = ?", (latitude, longitude, mission_row["asset_id"]))
		updated = connection.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
	return {"mission": dict(updated), "latitude": update.latitude, "longitude": update.longitude}
