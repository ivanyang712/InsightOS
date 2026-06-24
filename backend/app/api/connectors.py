from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.connectors import ConnectorError
from app.connectors.fred import FredConnector, normalize_fred_observations
from app.connectors.sec import SecConnector, normalize_company_facts
from app.services.data_ingestion import raw_record_from_response
from app.tasks.data_updates import data_update_runner, job_to_update_log

router = APIRouter(prefix="/api", tags=["connectors"])


@router.get("/connectors/sec/company/{cik}/profile")
def sec_company_profile(cik: str) -> dict[str, object]:
    try:
        response = SecConnector().get_company_profile(cik)
    except ConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {
        "raw": raw_record_from_response("sec", response, normalized_status="profile_loaded"),
        "company": {
            "cik": response.payload.get("cik"),
            "name": response.payload.get("name"),
            "tickers": response.payload.get("tickers", []),
            "sic": response.payload.get("sic"),
            "sic_description": response.payload.get("sicDescription"),
        },
    }


@router.get("/connectors/sec/company/{cik}/filings")
def sec_company_filings(cik: str) -> dict[str, object]:
    try:
        filings = SecConnector().get_filing_list(cik)
    except ConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {"filings": filings}


@router.get("/connectors/sec/company/{cik}/facts")
def sec_company_facts(cik: str) -> dict[str, object]:
    try:
        response = SecConnector().get_company_facts(cik)
    except ConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    facts = normalize_company_facts(response)
    return {
        "raw": raw_record_from_response("sec", response, normalized_status="facts_normalized"),
        "facts": facts,
    }


@router.get("/connectors/fred/series/{series_id}")
def fred_series(series_id: str) -> dict[str, object]:
    try:
        response = FredConnector().get_series_observations(series_id)
    except ConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    observations = normalize_fred_observations(series_id, response)
    return {
        "raw": raw_record_from_response("fred", response, normalized_status="series_normalized"),
        "observations": observations,
    }


@router.post("/data-updates/sec/company/{cik}/facts")
def refresh_sec_company_facts(cik: str, background_tasks: BackgroundTasks) -> dict[str, object]:
    background_tasks.add_task(data_update_runner.run_sec_company_facts, cik)
    return {"status": "queued", "connector": "sec", "target_identifier": cik}


@router.post("/data-updates/fred/series/{series_id}")
def refresh_fred_series(series_id: str, background_tasks: BackgroundTasks) -> dict[str, object]:
    background_tasks.add_task(data_update_runner.run_fred_series, series_id)
    return {"status": "queued", "connector": "fred", "target_identifier": series_id}


@router.get("/data-updates/{job_id}")
def data_update_status(job_id: str) -> dict[str, object]:
    job = data_update_runner.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Data update job not found.")
    return {"job": job, "log": job_to_update_log(job)}
