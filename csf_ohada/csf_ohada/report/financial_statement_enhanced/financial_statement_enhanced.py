# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import frappe

from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_engine import (
	FinancialReportEngine,
	get_xlsx_styles,  # hook for styling
)


def execute(filters: dict | None = None):
	if not filters.get("report_template"):
		frappe.throw("Report template is required")

	return FinancialReportEngine().execute(filters)
