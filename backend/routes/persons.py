import sqlite3

from fastapi import APIRouter, HTTPException

from database import get_connection, utc_now
from models import Person, PersonCreate


router = APIRouter()


def missing(person_id: int) -> HTTPException:
	return HTTPException(status_code=404, detail={"error": "Resource not found", "detail": f"Person with id {person_id} does not exist"})


@router.post("", response_model=Person, status_code=201)
def create_person(person: PersonCreate):
	try:
		values = person.model_dump()
		with get_connection() as connection:
			cursor = connection.execute("INSERT INTO persons (incident_id, name, status, latitude, longitude, created_at) VALUES (?, ?, ?, ?, ?, ?)", (*values.values(), utc_now()))
			row = connection.execute("SELECT * FROM persons WHERE id = ?", (cursor.lastrowid,)).fetchone()
	except sqlite3.IntegrityError:
		raise HTTPException(status_code=400, detail="incident_id does not reference an existing incident")
	return dict(row)


@router.get("", response_model=list[Person])
def list_persons():
	with get_connection() as connection:
		rows = connection.execute("SELECT * FROM persons ORDER BY id").fetchall()
	return [dict(row) for row in rows]


@router.get("/{person_id}", response_model=Person)
def get_person(person_id: int):
	with get_connection() as connection:
		row = connection.execute("SELECT * FROM persons WHERE id = ?", (person_id,)).fetchone()
	if row is None:
		raise missing(person_id)
	return dict(row)
