import frappe
from erpnext.setup.doctype.company.company import Company


class CustomCompany(Company):
	def create_default_accounts(self):
		from csf_ohada.csf_ohada.doctype.ohada_financial_report_template.ohada_financial_report_template import (
			sync_ohada_financial_report_templates,
		)
		from csf_ohada.overrides.chart_of_accounts.chart_of_accounts import (
			create_charts,
		)

		frappe.local.flags.ignore_root_company_validation = True
		sync_ohada_financial_report_templates(self.chart_of_accounts, self.existing_company)
		create_charts(self.name, self.chart_of_accounts, self.existing_company)

		self.db_set(
			"default_receivable_account",
			frappe.db.get_value(
				"Account",
				{"company": self.name, "account_type": "Receivable", "is_group": 0},
			),
		)

		self.db_set(
			"default_payable_account",
			frappe.db.get_value(
				"Account",
				{"company": self.name, "account_type": "Payable", "is_group": 0},
			),
		)
