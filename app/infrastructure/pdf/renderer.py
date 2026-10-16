from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fpdf import FPDF

from app.domain.interfaces.i_pdf_renderer import IPdfRenderer
from app.domain.read_models import WeeklyReportRow

_HEADERS = (
    ("Week start", 30),
    ("Week end", 30),
    ("New users", 26),
    ("Users w/ deposits", 34),
    ("Deposits sum", 38),
    ("Withdrawals sum", 38),
    ("Total tx", 28),
    ("Tx w/o cancels", 32),
)


class PdfReportRenderer(IPdfRenderer):

    def render_weekly_report(
        self,
        rows: list[WeeklyReportRow],
        generated_at: datetime,
    ) -> bytes:
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Weekly Transaction Report", border=0, align="C")
        pdf.ln(12)

        pdf.set_font("Helvetica", "", 10)
        if rows:
            pdf.cell(
                0,
                6,
                f"Period: {rows[0].week_start.isoformat()} \
                    - {rows[-1].week_end.isoformat()}",
                align="C",
            )
            pdf.ln(7)
        pdf.cell(
            0,
            6,
            f"Generated at: {generated_at:%Y-%m-%d %H:%M} UTC",
            align="C",
        )
        pdf.ln(10)

        self._table_header(pdf)

        pdf.set_font("Helvetica", "", 8)
        for row in rows:
            self._row(
                pdf,
                (
                    row.week_start.isoformat(),
                    row.week_end.isoformat(),
                    str(row.new_users_count),
                    str(row.users_with_deposit_count),
                    f"{row.deposits_sum:.2f}",
                    f"{row.withdrawals_sum:.2f}",
                    str(row.total_transactions_count),
                    str(row.transactions_without_cancels_count),
                ),
            )

        if rows:
            pdf.set_font("Helvetica", "B", 8)
            self._row(
                pdf,
                (
                    "TOTAL",
                    "",
                    "",
                    "",
                    f"{sum((r.deposits_sum for r in rows), start=Decimal('0')):.2f}",
                    f"{sum((r.withdrawals_sum for r in rows), start=Decimal('0')):.2f}",
                    str(sum(r.total_transactions_count for r in rows)),
                    str(sum(r.transactions_without_cancels_count for r in rows)),
                ),
            )

        return bytes(pdf.output())

    def _table_header(self, pdf: FPDF) -> None:
        pdf.set_font("Helvetica", "B", 8)
        for title, width in _HEADERS:
            pdf.cell(width, 8, title, border=1, align="C")
        pdf.ln()

    def _row(self, pdf: FPDF, values: tuple[str, ...]) -> None:
        for (_title, width), value in zip(_HEADERS, values):
            pdf.cell(width, 7, value, border=1, align="R")
        pdf.ln()
