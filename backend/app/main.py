from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.simulation import router as simulation_router
from app.api.scenario import router as scenario_router
from app.api.experiment import router as experiment_router
from app.api.report import router as report_router
from app.core.config import settings
from app.api.experiment import router as experiment_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulation_router, prefix="/api/simulation", tags=["simulation"])
app.include_router(scenario_router, prefix="/api/scenario", tags=["scenario"])
app.include_router(experiment_router, prefix="/api/experiment", tags=["experiment"])
app.include_router(report_router, prefix="/api/report", tags=["report"])
app.include_router(experiment_router, prefix="/api/experiment", tags=["experiment"])


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} Backend Running"}