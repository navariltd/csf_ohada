# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FinancialReportColumnEnhanced(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		column_code: DF.Data
		default_balance_type: DF.Literal[
			"",
			"Opening Balance",
			"Closing Balance",
			"Period Movement (Debits - Credits)",
			"Debits",
			"Credits",
		]
		default_calculation_formula: DF.Code | None
		default_is_formula: DF.Check
		fieldtype: DF.Literal["", "Currency", "Float", "Int", "Percent"]
		hidden: DF.Check
		label: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		period_scope: DF.Literal["All Periods", "Current Period Only", "Previous Periods Only"]
		title_template: DF.Data | None
	# end: auto-generated types

	pass
