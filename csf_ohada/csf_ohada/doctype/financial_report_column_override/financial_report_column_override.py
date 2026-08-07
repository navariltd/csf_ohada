# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FinancialReportColumnOverride(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		balance_type: DF.Literal[
			"", "Opening Balance", "Closing Balance", "Period Movement (Debits - Credits)"
		]
		calculation_formula: DF.Code | None
		column_code: DF.Data
		is_formula: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		row_reference_code: DF.Data
	# end: auto-generated types

	pass
