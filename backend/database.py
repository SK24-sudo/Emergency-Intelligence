import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("emergency.db")


def get_connection() -> sqlite3.Connection:
	connection = sqlite3.connect(DATABASE_PATH)
	connection.row_factory = sqlite3.Row
	connection.execute("PRAGMA foreign_keys = ON")
	return connection


def utc_now() -> str:
	return datetime.now(timezone.utc).isoformat()


def init_database() -> None:
	with get_connection() as connection:
		connection.executescript(
			"""
			CREATE TABLE IF NOT EXISTS incidents (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				type TEXT NOT NULL,
				description TEXT,
				latitude REAL,
				longitude REAL,
				severity TEXT,
				priority TEXT,
				status TEXT,
				created_at TEXT NOT NULL
			);
			CREATE TABLE IF NOT EXISTS alerts (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				incident_id INTEGER NOT NULL,
				message TEXT NOT NULL,
				severity TEXT,
				created_at TEXT NOT NULL,
				FOREIGN KEY (incident_id) REFERENCES incidents(id)
			);
			CREATE TABLE IF NOT EXISTS assets (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				type TEXT NOT NULL,
				status TEXT NOT NULL,
				latitude REAL,
				longitude REAL
			);
			CREATE TABLE IF NOT EXISTS missions (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				incident_id INTEGER NOT NULL,
				asset_id INTEGER NOT NULL,
				status TEXT NOT NULL,
				created_at TEXT NOT NULL,
				FOREIGN KEY (incident_id) REFERENCES incidents(id),
				FOREIGN KEY (asset_id) REFERENCES assets(id)
			);
			CREATE TABLE IF NOT EXISTS persons (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				incident_id INTEGER NOT NULL,
				name TEXT,
				status TEXT,
				latitude REAL,
				longitude REAL,
				created_at TEXT NOT NULL,
				FOREIGN KEY (incident_id) REFERENCES incidents(id)
			);
			"""
		)
