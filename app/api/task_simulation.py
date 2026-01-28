from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import TaskSimulationInput, TaskSimulationOutput
from app.services.task_simulation import generate_task_simulation, get_available_companies

router = APIRouter()


@router.get("/companies")
async def list_companies() -> list[dict[str, str]]:
    """List all available Egyptian tech companies for task simulation."""
    return get_available_companies()


@router.post("/task-simulation", response_model=TaskSimulationOutput)
async def task_simulation(payload: TaskSimulationInput) -> TaskSimulationOutput:
    simulation = generate_task_simulation(
        company_name=payload.company_name,
        task_title=payload.task_title,
    )
    return TaskSimulationOutput(
        company_name=payload.company_name,
        task_title=payload.task_title,
        simulation=simulation,
    )
