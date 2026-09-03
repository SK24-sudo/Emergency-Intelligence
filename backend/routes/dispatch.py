import sqlite3

from fastapi import APIRouter, HTTPException

from database import get_connection, utc_now
from models import DispatchRequest


router = APIRouter()


@router.post("", status_code=201)
def dispatch_asset(request: DispatchRequest):
	with get_connection() as connection:
		incident = connection.execute("SELECT id FROM incidents WHERE id = ?", (request.incident_id,)).fetchone()
		if incident is None:
			raise HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Incident with id {request.incident_id} does not exist"})
		asset = connection.execute("SELECT * FROM assets WHERE id = ?", (request.asset_id,)).fetchone()
		if asset is None:
			raise HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Asset with id {request.asset_id} does not exist"})
		if asset["status"].lower() != "available":
			raise HTTPException(status_code=400, detail={"error": "Asset unavailable", "detail": f"Asset with id {request.asset_id} is currently {asset['status']}"})
		try:
			cursor = connection.execute(
				"INSERT INTO missions (incident_id, asset_id, status, created_at) VALUES (?, ?, ?, ?)",
				(request.incident_id, request.asset_id, "assigned", utc_now()),
			)
		except sqlite3.IntegrityError:
			raise HTTPException(status_code=400, detail="Unable to create dispatch mission")
		connection.execute("UPDATE assets SET status = ? WHERE id = ?", ("deployed", request.asset_id))
		mission = connection.execute("SELECT * FROM missions WHERE id = ?", (cursor.lastrowid,)).fetchone()
	return {"message": "Asset dispatched successfully", "mission": dict(mission), "asset_id": request.asset_id, "incident_id": request.incident_id}