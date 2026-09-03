from typing import Optional

from pydantic import BaseModel


class IncidentBase(BaseModel):
	type: str
	description: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	severity: Optional[str] = None
	priority: Optional[str] = None
	status: Optional[str] = None


class IncidentCreate(IncidentBase):
	pass


class IncidentUpdate(BaseModel):
	type: Optional[str] = None
	description: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	severity: Optional[str] = None
	priority: Optional[str] = None
	status: Optional[str] = None


class Incident(IncidentBase):
	id: int
	created_at: str


class IncidentAnalysis(BaseModel):
	incident_id: int
	classification: str
	severity: str
	priority: str
	recommendation: str


class AlertCreate(BaseModel):
	incident_id: int
	message: str
	severity: Optional[str] = None


class Alert(AlertCreate):
	id: int
	created_at: str


class AssetBase(BaseModel):
	name: str
	type: str
	status: str
	latitude: Optional[float] = None
	longitude: Optional[float] = None


class AssetCreate(AssetBase):
	pass


class AssetUpdate(BaseModel):
	name: Optional[str] = None
	type: Optional[str] = None
	status: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None


class Asset(AssetBase):
	id: int


class MissionCreate(BaseModel):
	incident_id: int
	asset_id: int
	status: str


class MissionUpdate(BaseModel):
	incident_id: Optional[int] = None
	asset_id: Optional[int] = None
	status: Optional[str] = None


class MissionStatusUpdate(BaseModel):
	status: str
	latitude: Optional[float] = None
	longitude: Optional[float] = None


class DispatchRequest(BaseModel):
	incident_id: int
	asset_id: int


class Mission(MissionCreate):
	id: int
	created_at: str


class PersonCreate(BaseModel):
	incident_id: int
	name: Optional[str] = None
	status: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None


class Person(PersonCreate):
	id: int
	created_at: str
