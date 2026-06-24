from __future__ import annotations

from fastapi import APIRouter

from app.services.demo_research import (
    cloud_platform_comparison_demo,
    nvidia_demo_report,
    semiconductor_equipment_demo,
)

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/research/nvidia")
def get_nvidia_demo_report() -> dict[str, object]:
    return nvidia_demo_report()


@router.get("/industry/semiconductor-equipment")
def get_semiconductor_equipment_demo() -> dict[str, object]:
    return semiconductor_equipment_demo()


@router.get("/comparison/cloud-platforms")
def get_cloud_platform_comparison_demo() -> dict[str, object]:
    return cloud_platform_comparison_demo()
