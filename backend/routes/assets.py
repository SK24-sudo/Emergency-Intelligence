from fastapi import APIRouter, HTTPException

from database import get_connection
from models import Asset, AssetCreate, AssetUpdate


router = APIRouter()


def missing(asset_id: int) -> HTTPException:
	return HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Asset with id {asset_id} does not exist"})


@router.post("", response_model=Asset, status_code=201)
def create_asset(asset: AssetCreate):
	values = asset.model_dump()
	with get_connection() as connection:
		cursor = connection.execute("INSERT INTO assets (name, type, status, latitude, longitude) VALUES (?, ?, ?, ?, ?)", tuple(values.values()))
		row = connection.execute("SELECT * FROM assets WHERE id = ?", (cursor.lastrowid,)).fetchone()
	return dict(row)


@router.get("", response_model=list[Asset])
def list_assets():
	with get_connection() as connection:
		rows = connection.execute("SELECT * FROM assets ORDER BY id").fetchall()
	return [dict(row) for row in rows]


@router.get("/{asset_id}", response_model=Asset)
def get_asset(asset_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
	if row is None:
		raise missing(asset_id)
	return dict(row)


@router.put("/{asset_id}", response_model=Asset)
def update_asset(asset_id: int, asset: AssetUpdate):
	values = asset.model_dump(exclude_unset=True)
	with get_connection() as connection:
		if connection.execute("SELECT id FROM assets WHERE id = ?", (asset_id,)).fetchone() is None:
			raise missing(asset_id)
		if values:
			assignments = ", ".join(f"{key} = ?" for key in values)
			connection.execute(f"UPDATE assets SET {assignments} WHERE id = ?", (*values.values(), asset_id))
		row = connection.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
	return dict(row)
