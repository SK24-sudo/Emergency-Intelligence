from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import init_database
from routes import ai, alerts, assets, dispatch, incidents, missions, persons


app = FastAPI(title="Emergency Intelligence Backend")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
	init_database()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
	if isinstance(exception.detail, dict):
		return JSONResponse(status_code=exception.status_code, content=exception.detail)
	return JSONResponse(status_code=exception.status_code, content={"error": "Request failed", "detail": exception.detail})


@app.get("/")
def root():
	return {"status": "ok", "service": "Emergency Intelligence Backend"}


app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])
app.include_router(missions.router, prefix="/missions", tags=["missions"])
app.include_router(persons.router, prefix="/persons", tags=["persons"])
app.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
