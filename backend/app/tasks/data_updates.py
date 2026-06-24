from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.connectors.fred import FredConnector, normalize_fred_observations
from app.connectors.sec import SecConnector, normalize_company_facts
from app.schemas import DataUpdateLogCreate
from app.services.data_ingestion import update_log


@dataclass
class DataUpdateJob:
    job_id: str
    connector_name: str
    target_identifier: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    records_read: int = 0
    records_written: int = 0
    error_message: str | None = None


class InMemoryDataUpdateRunner:
    def __init__(self) -> None:
        self.jobs: dict[str, DataUpdateJob] = {}

    def run_sec_company_facts(self, cik: str) -> DataUpdateJob:
        job = self._start("sec", cik)
        try:
            response = SecConnector().get_company_facts(cik)
            facts = normalize_company_facts(response)
            self._finish(job, records_read=1, records_written=len(facts))
        except Exception as error:  # noqa: BLE001
            self._fail(job, str(error))
        return job

    def run_fred_series(self, series_id: str) -> DataUpdateJob:
        job = self._start("fred", series_id)
        try:
            response = FredConnector().get_series_observations(series_id)
            observations = normalize_fred_observations(series_id, response)
            self._finish(job, records_read=1, records_written=len(observations))
        except Exception as error:  # noqa: BLE001
            self._fail(job, str(error))
        return job

    def get(self, job_id: str) -> DataUpdateJob | None:
        return self.jobs.get(job_id)

    def _start(self, connector_name: str, target_identifier: str) -> DataUpdateJob:
        job = DataUpdateJob(
            job_id=str(uuid4()),
            connector_name=connector_name,
            target_identifier=target_identifier,
            status="running",
            started_at=datetime.now(UTC),
        )
        self.jobs[job.job_id] = job
        return job

    def _finish(self, job: DataUpdateJob, *, records_read: int, records_written: int) -> None:
        job.status = "succeeded"
        job.finished_at = datetime.now(UTC)
        job.records_read = records_read
        job.records_written = records_written

    def _fail(self, job: DataUpdateJob, error_message: str) -> None:
        job.status = "failed"
        job.finished_at = datetime.now(UTC)
        job.error_message = error_message


data_update_runner = InMemoryDataUpdateRunner()


def job_to_update_log(job: DataUpdateJob) -> DataUpdateLogCreate:
    return update_log(
        connector_name=job.connector_name,
        job_type="connector_refresh",
        target_identifier=job.target_identifier,
        status=job.status,
        records_read=job.records_read,
        records_written=job.records_written,
        error_message=job.error_message,
    )
