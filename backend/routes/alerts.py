import sqlite3

from fastapi import APIRouter, HTTPException

from database import get_connection, utc_now
from models import Alert, AlertCreate


router = APIRouter()


def not_found(alert_id: int) -> HTTPException:
	return HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Alert with id {alert_id} does not exist"})


@router.post("", response_model=Alert, status_code=201)
def create_alert(alert: AlertCreate):
	try:
		with get_connection() as connection:
			cursor = connection.execute("INSERT INTO alerts (incident_id, message, severity, created_at) VALUES (?, ?, ?, ?)", (*alert.model_dump().values(), utc_now()))
			row = connection.execute("SELECT * FROM alerts WHERE id = ?", (cursor.lastrowid,)).fetchone()
	except sqlite3.IntegrityError:
		raise HTTPException(status_code=400, detail="incident_id does not reference an existing incident")
	return dict(row)


@router.get("", response_model=list[Alert])
def list_alerts():
	with get_connection() as connection:
		rows = connection.execute("SELECT * FROM alerts ORDER BY id").fetchall()
	return [dict(row) for row in rows]


@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
	if row is None:
		raise not_found(alert_id)
	return dict(row)
