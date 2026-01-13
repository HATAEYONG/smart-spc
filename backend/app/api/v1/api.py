"""
API Router - V1
Aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, qcost, inspection, spc, qa

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(qcost.router, prefix="/qcost", tags=["Q-COST"])
api_router.include_router(inspection.router, prefix="/inspection", tags=["Inspection"])
api_router.include_router(spc.router, prefix="/spc", tags=["SPC"])
api_router.include_router(qa.router, prefix="/qa", tags=["QA"])
