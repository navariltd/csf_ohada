import json
import os

import frappe
from frappe.utils import cstr


@frappe.whitelist()
def get_chart(chart_template, existing_company=None):
	chart = {}
	if existing_company:
		return get_account_tree_from_existing_company(existing_company)

	elif chart_template == "Standard":
		from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
			standard_chart_of_accounts,
		)

		return standard_chart_of_accounts.get()
	elif chart_template == "Standard with Numbers":
		from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
			standard_chart_of_accounts_with_account_number,
		)

		return standard_chart_of_accounts_with_account_number.get()
	else:
		folders = ("verified",)
		if frappe.local.flags.allow_unverified_charts:
			folders = ("verified", "unverified")
		for folder in folders:
			path = os.path.join(os.path.dirname(__file__), folder)
			for fname in os.listdir(path):
				fname = frappe.as_unicode(fname)
				if fname.endswith(".json"):
					with open(os.path.join(path, fname)) as f:
						chart = f.read()
						if chart and json.loads(chart).get("name") == chart_template:
							return json.loads(chart).get("tree")


@frappe.whitelist()
def get_charts_for_country(country, with_standard=False):
	charts = []

	def _get_chart_name(content):
		if content:
			content = json.loads(content)
			if (
				content and content.get("disabled", "No") == "No"
			) or frappe.local.flags.allow_unverified_charts:
				charts.append(content["name"])

	country_code = frappe.get_cached_value("Country", country, "code")
	print("COUNTRY CODE", country_code)
	if country_code:
		folders = ("verified",)
		if frappe.local.flags.allow_unverified_charts:
			folders = ("verified", "unverified")

		for folder in folders:
			path = os.path.join(os.path.dirname(__file__), folder)
			if not os.path.exists(path):
				print("PATH NOT EXISTS", path)
				continue

			for fname in os.listdir(path):
				fname = frappe.as_unicode(fname)
				if (fname.startswith(country_code) or fname.startswith(country)) and fname.endswith(".json"):
					with open(os.path.join(path, fname)) as f:
						_get_chart_name(f.read())

	print("CHARTS", charts)
	# if more than one charts, returned then add the standard
	if len(charts) != 1 or with_standard:
		charts += ["Standard", "Standard with Numbers"]

	return charts


def get_account_tree_from_existing_company(existing_company):
	all_accounts = frappe.get_all(
		"Account",
		filters={"company": existing_company},
		fields=[
			"name",
			"account_name",
			"parent_account",
			"account_type",
			"is_group",
			"root_type",
			"tax_rate",
			"account_number",
			"account_currency",
		],
		order_by="lft, rgt",
	)

	account_tree = {}

	# fill in tree starting with root accounts (those with no parent)
	if all_accounts:
		build_account_tree(account_tree, None, all_accounts)
	return account_tree


def build_account_tree(tree, parent, all_accounts):
	# find children
	parent_account = parent.name if parent else ""
	children = [acc for acc in all_accounts if cstr(acc.parent_account) == parent_account]

	# if no children, but a group account
	if not children and parent.is_group:
		tree["is_group"] = 1
		tree["account_number"] = parent.account_number

	# build a subtree for each child
	for child in children:
		# start new subtree
		tree[child.account_name] = {}

		# assign account_type and root_type
		if child.account_number:
			tree[child.account_name]["account_number"] = child.account_number
		if child.account_type:
			tree[child.account_name]["account_type"] = child.account_type
		if child.tax_rate:
			tree[child.account_name]["tax_rate"] = child.tax_rate
		if child.account_currency:
			tree[child.account_name]["account_currency"] = child.account_currency
		if not parent:
			tree[child.account_name]["root_type"] = child.root_type

		# call recursively to build a subtree for current account
		build_account_tree(tree[child.account_name], child, all_accounts)
