# SafeZone

## Emergency intelligence and response coordination prototype

SafeZone reduces the coordination gap between emergency reporting and response. A citizen reports an incident, deterministic intelligence assesses it, and an authorized Control Centre operator decides whether to dispatch an available response asset.

> A citizen reports. SafeZone assesses. The Control Centre decides. The response asset acts.

## Quick Access

Start both processes before opening the application: run the frontend with `npm run dev` from `frontend/`, and run the backend with Uvicorn from `backend/` using `python -m uvicorn main:app --reload`.

| Area | URL |
|---|---|
| Frontend | [http://localhost:5173](http://localhost:5173) |
| Citizen Portal | [http://localhost:5173/](http://localhost:5173/) |
| Control Centre | [http://localhost:5173/control](http://localhost:5173/control) |
| Backend API | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| Swagger documentation | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |

This repository contains a working React + FastAPI + SQLite prototype. Drone, camera, robot, external emergency feeds, and computer vision are represented as deterministic software simulations or future integration points where noted below. This is not a physical rescue system or a production emergency service.

## What Is Implemented

- Citizen Portal for submitting an emergency type, description, latitude, and longitude.
- Control Centre for filtering incidents, reviewing details, viewing severity and priority, and displaying recommendations.
- REST communication between the React frontend and FastAPI backend using JSON.
- SQLite persistence for incidents, alerts, assets, missions, and persons.
- Explainable, deterministic intelligence for classification, severity, priority, duplicate checks, and recommendations.
- Operator-controlled asset dispatch and mission status updates.
- Coordinate visualization for incidents, assets, and people in the Control Centre.
- Deterministic drone, camera, robot, and scenario simulation modules with state transitions and events.

## Product Boundary

SafeZone separates four operational concerns:

1. **Citizen reporting**: a person submits information about an emergency.
2. **Emergency intelligence**: the backend applies deterministic rules to assess the report.
3. **Command Centre operations**: an authorized operator reviews the incident and chooses the next action.
4. **Response simulation**: software models demonstrate how future response assets could progress through a mission.

SafeZone does not replace emergency authorities. It provides a digital coordination layer between emergency reporting, incident assessment, and authorized response operations.

## High-Level System Vision

The following diagram describes the intended overall architecture. Items marked as simulated, deterministic, mocked, or planned are not represented as live integrations in this repository.

```text
			  EMERGENCY SOURCES
		  +-----------+-----------+
		  |           |           |
		 IMD       SACHET     CITIZENS
		  |           |           |
		  +-----------+-----------+
				  |
			  DATA INGESTION
				  |
		     DETERMINISTIC INTELLIGENCE
		  +-----------+-----------+
		  |           |           |
		VERIFY      ANALYZE     CORRELATE
		  |           |           |
	    TYPE/CHECK  SEVERITY    DUPLICATES
		  +-----------+-----------+
				  |
			 PRIORITY ENGINE
				  |
			  INCIDENT DB
			    SQLite
				  |
		  +-----------+-----------+
		  |                       |
	  ALERT SYSTEM              MAP VIEW
		  |                       |
		  +-----------+-----------+
				  |
			  COMMAND CENTRE
				  |
			     DISPATCH
				  |
		     DRONE SEARCH (SIMULATED)
				  |
			CAMERA (SIMULATED)
				  |
		 PERSON DETECTION (SIMULATED)
				  |
		     LOCATION IDENTIFIED
			  /             \
			 /               \
	 RESCUE TEAM              ROBOT (SIMULATED)
					    |
				    INSPECT / RESCUE
```

IMD and SACHET ingestion, live event streaming, physical assets, real camera feeds, and production computer vision are future scope. The current backend receives citizen reports and operator actions through REST endpoints.

## User Workflows

### Citizen Portal: `/`

The public-facing page lets a citizen select an emergency type, enter a description, provide coordinates, and submit the report. The frontend sends the report to `POST /incidents` and displays confirmation or duplicate-report feedback. Citizens do not dispatch assets.

### Control Centre: `/control`

The operator page retrieves incidents, alerts, assets, missions, and persons. It supports emergency-category filtering, incident selection, severity and priority review, deterministic analysis, recommendation display, coordinate visualization, available-asset selection, dispatch, and mission status updates. Person information appears when a person has been added through the API or simulation script.

## Dispatch Workflow

1. A citizen submits an emergency from the Citizen Portal.
2. React sends JSON to FastAPI.
3. Pydantic validates the request shape.
4. The backend checks for an exact type-and-coordinate duplicate, then applies deterministic severity and priority rules.
5. The incident is persisted in SQLite.
6. The Control Centre retrieves the incident and can request a fresh analysis.
7. The operator selects an asset whose backend status is `available`.
8. The operator dispatches it through `POST /dispatch`.
9. The backend validates that the incident and asset exist and that the asset is available.
10. A mission is created with status `assigned`, and the asset status changes to `deployed`.
11. Mission status and asset coordinates can be updated through `POST /missions/{mission_id}/status`.
12. The separate simulation layer can represent movement, search, person detection, and rescue states.

Dispatch does **not** automatically start a Python drone, camera, or robot simulation. The simulation scripts must be run separately, and the REST-facing drone script manually reports mission states and creates a person record.

## Intelligence Layer

The current intelligence is deterministic and rule-based, not a trained machine-learning model. It is designed to be explainable and testable.

- **Classification**: keyword-based incident classification for cases such as fire, flood, medical, structural, and general incidents.
- **Severity**: rule-based `critical`, `high`, `medium`, or `low` assessment.
- **Priority**: severity-based priorities in the incident workflow, plus a scored priority API for richer input such as affected population, distress, and confidence.
- **Duplicate checks**: exact type-and-coordinate checks during incident creation; the AI module also contains explainable text and coordinate correlation helpers.
- **Recommendations**: deterministic guidance such as dispatching an available asset for high-severity incidents or monitoring lower-severity reports.

## Backend Architecture

```text
React / Vite
	|
	| REST + JSON
	v
FastAPI + Uvicorn
	|
	| Pydantic validation and route-level business logic
	v
SQLite via Python built-in sqlite3
	|
	+-- incidents
	+-- alerts
	+-- assets
	+-- missions
	+-- persons
```

FastAPI provides a lightweight Python REST framework, automatic Swagger/OpenAPI documentation, and a convenient boundary for the Python intelligence and simulation modules. Uvicorn runs FastAPI as the ASGI server. SQLite is zero-configuration, file-based, and appropriate for this prototype; the project intentionally uses Python's built-in `sqlite3` module rather than SQLAlchemy.

The database file is `backend/emergency.db`. Tables are created during FastAPI startup by `backend/database.py`. There is no separate database server.

## API

With the backend running:

- Root health response: `http://127.0.0.1:8000/`
- Swagger/OpenAPI UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Route groups and implemented operations:

| Group | Implemented operations | Purpose |
|---|---|---|
| `/incidents` | `POST /`, `GET /`, `GET /{incident_id}`, `PUT /{incident_id}`, `POST /{incident_id}/analyze` | Create, retrieve, update, and assess incidents |
| `/alerts` | `POST /`, `GET /`, `GET /{alert_id}` | Create and retrieve incident alerts |
| `/assets` | `POST /`, `GET /`, `GET /{asset_id}`, `PUT /{asset_id}` | Configure and inspect response assets |
| `/missions` | `POST /`, `GET /`, `GET /{mission_id}`, `PUT /{mission_id}`, `POST /{mission_id}/status` | Create, inspect, update, and progress missions |
| `/persons` | `POST /`, `GET /`, `GET /{person_id}` | Record and retrieve located people |
| `/dispatch` | `POST /` | Validate and dispatch an available asset |
| `/ai` | `POST /analyze`, `POST /priority`, `POST /recommend` | Run deterministic intelligence functions |

The route implementations are in `backend/routes/`, with request and response models in `backend/models.py`. The complete JSON contract is also available in `backend/api_contract.md`; Swagger is the runtime source of truth.

## Response Assets

Assets have a name, type, status, latitude, and longitude. Dispatch only accepts an asset whose status is `available`.

The backend does **not** seed `Drone-01` or `Robot-01` automatically. The database tables are created at startup, but assets must be created with `POST /assets` or already exist in `backend/emergency.db`. The simulation data under `simulation/data/` contains separate fixed demo resources such as `DRONE-01` and `ROBOT-01`; it is not imported into the backend database.

To create the two UI demo choices in PowerShell after starting the backend:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/assets -ContentType 'application/json' -Body '{"name":"Drone-01","type":"drone","status":"available","latitude":18.5204,"longitude":73.8567}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/assets -ContentType 'application/json' -Body '{"name":"Robot-01","type":"robot","status":"available","latitude":18.5204,"longitude":73.8567}'
```

## Requirements

### System

- Windows, Linux, or macOS
- Python 3.x (the simulation uses modern Python typing and `StrEnum`)
- Node.js and npm
- Git

### Backend dependencies

The exact packages listed in `backend/requirements.txt` are:

- FastAPI
- Uvicorn
- httpx (used by the API tests through FastAPI's test client)

SQLite and `sqlite3` are provided by Python; no database installation is required.

### Frontend dependencies

`frontend/package.json` defines React, React DOM, and Vite. Available scripts are `npm run dev` and `npm run build`.

## Installation and Running

From the project directory:

```powershell
cd Emergency-Intelligence
```

### Backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend: `http://127.0.0.1:8000`  
Swagger: `http://127.0.0.1:8000/docs`

If PowerShell blocks script activation, use the Python environment's interpreter directly or adjust the local execution-policy setting according to your machine's policy.

### Frontend

Open a second terminal:

```powershell
cd Emergency-Intelligence\frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`  
Citizen Portal: `http://localhost:5173/`  
Control Centre: `http://localhost:5173/control`

The frontend API client is configured for `http://127.0.0.1:8000`. Start the backend before submitting or loading live data.

## Quick Demo

1. Start the backend and frontend using the commands above.
2. Create `Drone-01` and `Robot-01` with the asset commands, unless they already exist in the database.
3. Open the Citizen Portal at `http://localhost:5173/`.
4. Select **Fire**, enter an emergency description such as `Fire and smoke coming from a building`, and enter coordinates.
5. Submit the report and note the confirmation.
6. Open `http://localhost:5173/control`.
7. Select the **Fire** category and select the new incident.
8. Show its severity, priority, coordinates, and recommendation.
9. Choose **Drone-01** or **Robot-01**, then dispatch it.
10. Show the resulting mission and the asset's changed status.
11. Change mission status from the Control Centre, or run a separate simulation workflow where appropriate.
12. Show person and location information only after a person has been added through the API or a simulation script.
13. Explain clearly that physical hardware, live telemetry, and automatic simulation orchestration are future integration work.

## Simulation and Future Physical Integration

### Current prototype

- `simulation/drone/` models deterministic drone dispatch, movement, search, detection, and return states.
- `simulation/camera/` models a camera attached to a drone, simulated frames, and deterministic person detection.
- `simulation/robot/` models deterministic robot movement and rescue states.
- `simulation/data/` provides fixed demo incidents, drones, robots, and people.
- `simulation/contract.py`, `events.py`, and `state_machine.py` define shared states, events, and transition rules.
- `simulation/drone/drone.py` and `simulation/robot/robot.py` provide small REST-facing scripts for manually reporting progress.

These components are software representations of a future response layer. They use fixed values and state machines where applicable; they are not physical drones, robots, camera feeds, or trained computer-vision systems.

### Future scope

- Physical drone integration and real telemetry/GPS
- Real camera feeds and computer vision
- Autonomous robot integration
- IMD/SACHET and other emergency-authority integrations
- Real-time event streaming
- Production authentication, authorization, audit logging, and secure communication
- Deployment and scaling beyond a local SQLite prototype

## Real-World Workflow

Traditional response often looks like:

```text
Citizen -> emergency call/report -> authority/operator -> assessment
	  -> dispatch -> field response -> rescue
```

SafeZone's software workflow is:

```text
Citizen -> SafeZone Citizen Portal -> FastAPI -> incident intelligence
	  -> Control Centre -> authorized operator -> response asset -> monitoring
```

The edge is operational separation: citizens report, control operators decide, and response assets are controlled through an explicit dispatch workflow. The goal is to make the handoff from information to action easier to coordinate.

## Project Structure

```text
Emergency-Intelligence/
├── backend/
│   ├── main.py              # FastAPI application, CORS, startup, routers
│   ├── database.py          # SQLite connection and table initialization
│   ├── models.py            # Pydantic request and response models
│   ├── requirements.txt     # Backend dependencies
│   ├── api_contract.md      # API contract notes
│   ├── routes/              # incidents, alerts, assets, missions, persons, dispatch, ai
│   └── ai/                  # classifier, severity, priority, duplicate, recommendation rules
├── frontend/
│   ├── package.json         # React/Vite scripts and dependencies
│   ├── index.html
│   └── src/
│       ├── App.jsx          # Citizen Portal and Control Centre views
│       ├── main.jsx         # React entry point
│       ├── services/api.js  # REST client for the FastAPI backend
│       └── styles.css       # Application styling
├── simulation/
│   ├── contract.py          # Shared states and event vocabulary
│   ├── events.py            # Simulation event records
│   ├── state_machine.py     # Valid transition rules
│   ├── camera/              # Camera simulator
│   ├── data/                # Fixed demo incidents, assets, and people
│   ├── drone/               # Drone simulator and REST-facing demo script
│   └── robot/               # Robot simulator and REST-facing demo script
├── database/                # Database notes
└── tests/
    ├── test_ai_api.py       # AI and FastAPI endpoint tests
    ├── api/                 # API test area
    ├── simulation/          # Unit tests for simulation components
    └── scenarios/           # End-to-end deterministic scenario workflows
```

## Testing

The repository uses Python's `unittest` discovery. From the project root, with backend dependencies installed:

```powershell
python -m unittest discover -s tests -t . -p "test_*.py"
```

The suite covers AI classification, severity and priority behavior, recommendations, duplicate/correlation helpers, FastAPI AI endpoints, simulation contracts, deterministic drone/camera/robot behavior, demo data, state machines, and multi-step emergency scenarios. The frontend has a production build check but no frontend test script in `frontend/package.json`.

To verify the frontend bundle:

```powershell
cd frontend
npm run build
```

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | Citizen and operator interfaces |
| Backend | FastAPI | REST API and integration layer |
| Server | Uvicorn | ASGI server for FastAPI |
| Validation | Pydantic | Request and response validation |
| Database | SQLite | File-based persistence |
| DB access | Python `sqlite3` | Lightweight database access |
| Intelligence | Python rules | Deterministic, explainable assessment |
| Simulation | Python | Response asset and scenario simulation |
| API format | JSON | Frontend/backend communication |

## Security and Operational Boundary

SafeZone is a hackathon prototype and does not claim production security. Citizen reporting is intentionally separated from dispatch authority: the Control Centre workflow performs dispatch actions. A production deployment would require authenticated users, role-based authorization, audit logging, input and transport protection, secure secrets management, and operational safeguards.

## Limitations

The current boundary is deliberate and keeps the prototype demonstrable:

- External IMD, SACHET, and emergency-authority feeds are not integrated.
- Drone, robot, and camera behavior is simulated in software.
- Person detection uses fixed deterministic demo data, not a trained production computer-vision model.
- Coordinates are visualized in a purpose-built view, not on a full GIS or live map platform.
- Live telemetry, WebSockets, authentication, authorization, and production audit controls are not implemented.
- Dispatch creates and updates backend missions but does not automatically launch the simulation processes.
- SQLite is suitable for this local prototype, not a claim of production-scale persistence.

## Roadmap

### Phase 1 — Current Prototype

- Citizen reporting
- FastAPI backend and SQLite persistence
- Deterministic intelligence
- Control Centre workflow
- Asset dispatch and mission status
- Drone, camera, robot, and scenario simulation

### Phase 2 — Integration

- Real emergency data sources
- Real-time telemetry and live mapping
- Improved event correlation
- Authentication and authorization
- Event streaming and operational audit trails

### Phase 3 — Physical Deployment

- Drone integration
- Robot integration
- Camera and computer-vision integration
- Field rescue workflows and authority integrations

## Judge-Friendly Summary

**What we solve:** Reduce the coordination gap between emergency reporting and response.

**What we built:** A working React + FastAPI + SQLite emergency coordination prototype with deterministic intelligence, Control Centre workflows, operator-controlled asset dispatch, and response simulation.

**What makes it extensible:** The backend API is the integration boundary. Simulated assets and fixed demo data can eventually be connected to real devices, telemetry, vision systems, and external emergency data sources without changing the core citizen-to-operator workflow.
