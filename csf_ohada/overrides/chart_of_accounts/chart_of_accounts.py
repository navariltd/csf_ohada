import os

import frappe
from erpnext.accounts.doctype.account.chart_of_accounts import chart_of_accounts as erpnext_coa
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
	add_suffix_if_duplicate,
	build_tree_from_json,
	get_chart_metadata_fields,
	identify_is_group,
	rebuild_tree,
)
from frappe import _
from frappe.utils import cstr


def create_charts(
	company,
	chart_template=None,
	existing_company=None,
	custom_chart=None,
	from_coa_importer=None,
):
	chart = custom_chart or get_chart(chart_template, existing_company)
	if chart:
		accounts = []

		def _import_accounts(children, parent, root_type, root_account=False):
			nonlocal custom_chart
			for account_name, child in children.items():
				if root_account:
					root_type = child.get("root_type")

				if account_name not in get_chart_metadata_fields():
					account_number = cstr(child.get("account_number")).strip()
					account_name, account_name_in_db = add_suffix_if_duplicate(
						account_name, account_number, accounts
					)

					is_group = identify_is_group(child)
					report_type = (
						"Balance Sheet"
						if root_type in ["Asset", "Liability", "Equity"]
						else "Profit and Loss"
					)

					account = frappe.get_doc(
						{
							"doctype": "Account",
							"account_name": (
								child.get("account_name") if from_coa_importer else account_name
							),
							"company": company,
							"parent_account": parent,
							"is_group": is_group,
							"root_type": root_type,
							"report_type": report_type,
							"account_number": account_number,
							"account_type": child.get("account_type"),
							"account_category": child.get("account_category"),
							"account_currency": (
								child.get("account_currency")
								if custom_chart
								else frappe.get_cached_value("Company", company, "default_currency")
							),
							"tax_rate": child.get("tax_rate"),
						}
					)

					if root_account or frappe.local.flags.allow_unverified_charts:
						account.flags.ignore_mandatory = True

					account.flags.ignore_permissions = True

					account.insert()

					accounts.append(account_name_in_db)

					_import_accounts(child, account.name, root_type)

		# Rebuild NestedSet HSM tree for Account Doctype
		# after all accounts are already inserted.
		frappe.local.flags.ignore_update_nsm = True
		_import_accounts(chart, None, None, root_account=True)
		rebuild_tree("Account")
		frappe.local.flags.ignore_update_nsm = False


def get_ohada_charts():
	"""Charts shipped by csf_ohada, which take precedence over ERPNext charts with the same name"""
	path = os.path.join(os.path.dirname(__file__), "verified")
	charts = []
	for fname in sorted(os.listdir(path)):
		if fname.endswith(".json"):
			charts.append((fname, frappe.get_file_json(os.path.join(path, fname))))
	return charts


@frappe.whitelist()
def get_chart(chart_template: str, existing_company: str | None = None) -> dict:
	if not existing_company:
		for _fname, chart in get_ohada_charts():
			if chart.get("name") == chart_template:
				return chart.get("tree")

	return erpnext_coa.get_chart(chart_template, existing_company)


@frappe.whitelist()
def get_charts_for_country(country: str, with_standard: bool = False) -> list[str]:
	standard_charts = ["Standard", "Standard with Numbers"]
	charts = []

	country_code = frappe.get_cached_value("Country", country, "code")
	if country_code:
		for fname, chart in get_ohada_charts():
			if (fname.startswith(country_code) or fname.startswith(country)) and (
				chart.get("disabled", "No") == "No" or frappe.local.flags.allow_unverified_charts
			):
				charts.append(chart["name"])

	for chart_name in erpnext_coa.get_charts_for_country(country):
		if chart_name not in charts and chart_name not in standard_charts:
			charts.append(chart_name)

	# if more than one charts, returned then add the standard
	if len(charts) != 1 or with_standard:
		charts += standard_charts

	return charts


@frappe.whitelist()
def get_coa(doctype: str, parent: str, is_root: bool | None = None, chart: str | None = None) -> list[dict]:
	"""Same as erpnext.accounts.utils.get_coa, but resolves the chart via csf_ohada's get_chart"""
	parent = None if parent == _("All Accounts") else parent
	accounts = build_tree_from_json(chart, chart_data=get_chart(chart)) or []

	# filter out to show data for the selected node only
	return [d for d in accounts if d["parent_account"] == parent]
