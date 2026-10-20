from __future__ import annotations

from uuid import UUID

from app.domain.interfaces.i_report_storage import IReportStorage


class S3ReportStorage(IReportStorage):

    def __init__(self, client, bucket: str, public_endpoint: str) -> None:
        self._client = client
        self._bucket = bucket
        self._public_endpoint = public_endpoint.rstrip("/")

    async def upload_report(self, data: bytes, report_id: UUID) -> str:
        key = f"reports/{report_id}.pdf"

        await self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType="application/pdf",
        )

        return f"{self._public_endpoint}/{self._bucket}/{key}"

    async def delete_report(self, report_id: UUID) -> None:
        await self._client.delete_object(
            Bucket=self._bucket,
            Key=f"reports/{report_id}.pdf",
        )
