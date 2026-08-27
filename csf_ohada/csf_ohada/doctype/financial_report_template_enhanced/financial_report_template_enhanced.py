# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import os
import shutil

import frappe
from erpnext.accounts.doctype.account_category.account_category import import_account_categories
from frappe import _
from frappe.model.document import Document

from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.column_layout import (
	build_column_defaults,
	find_column_cycles,
	get_measure_columns,
	get_template_column_codes,
	prune_row_column_settings,
)
from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_validation import (
	TemplateValidator,
)


class FinancialReportTemplateEnhanced(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from csf_ohada.csf_ohada.doctype.financial_report_column_enhanced.financial_report_column_enhanced import (
			FinancialReportColumnEnhanced,
		)
		from csf_ohada.csf_ohada.doctype.financial_report_row_enhanced.financial_report_row_enhanced import (
			FinancialReportRowEnhanced,
		)

		columns: DF.Table[FinancialReportColumnEnhanced]
		disabled: DF.Check
		module: DF.Link | None
		report_type: DF.Literal[
			"", "Profit and Loss Statement", "Balance Sheet", "Cash Flow", "Custom Financial Statement"
		]
		rows: DF.Table[FinancialReportRowEnhanced]
		template_name: DF.Data
	# end: auto-generated types

	def before_validate(self):
		self.clear_hidden_fields()
		self._prune_stale_column_references()

	def _prune_stale_column_references(self):
		"""Remove row column settings that point at deleted Value Columns."""
		valid_codes = get_template_column_codes(self)
		pruned_rows = 0

		for row in self.rows or []:
			if prune_row_column_settings(row, valid_codes):
				pruned_rows += 1

		if pruned_rows:
			frappe.msgprint(
				_(
					"Removed column settings from {0} report line(s) that referenced deleted Value Columns."
				).format(frappe.bold(str(pruned_rows))),
				title=_("Column settings updated"),
				indicator="orange",
			)

	def clear_hidden_fields(self):
		style_data_sources = {"Blank Line", "Column Break", "Section Break"}

		for row in self.rows:
			if row.data_source != "Account Data":
				row.balance_type = None
				row.balance_filter = "All"

			if row.data_source in style_data_sources:
				row.calculation_formula = None
				row.column_settings = None

	def validate(self):
		self._validate_columns()
		validator = TemplateValidator(self)
		result = validator.validate()
		result.notify_user()

	def _validate_columns(self):
		column_codes = []
		for col in self.columns or []:
			code = (col.column_code or "").strip()
			if not code:
				frappe.throw(_("Column Code is required for all Value Columns"))
			if code in column_codes:
				frappe.throw(_("Duplicate Column Code: {0}").format(frappe.bold(code)))
			column_codes.append(code)

		row_refs = {row.reference_code for row in self.rows if row.reference_code}

		# Formulas resolve column codes and line references in one namespace
		for code in column_codes:
			if code in row_refs:
				frappe.throw(
					_("Column Code {0} is also used as a Line Reference. Use distinct codes.").format(
						frappe.bold(code)
					)
				)

		for col in self.columns or []:
			if col.default_is_formula and not (col.default_calculation_formula or "").strip():
				frappe.throw(
					_("Value Column {0} is marked as a formula default but no formula is set").format(
						frappe.bold(col.column_code)
					)
				)

		self._validate_column_cycles()

	def _validate_column_cycles(self):
		if not self.columns:
			return

		measures = get_measure_columns(self)
		column_defaults = build_column_defaults(self)

		for row in self.rows:
			cyclic = find_column_cycles(row, measures, column_defaults)
			if cyclic:
				frappe.throw(
					_("Value columns of row {0} reference each other in a loop: {1}").format(
						frappe.bold(row.reference_code or row.display_name or row.idx),
						frappe.bold(", ".join(cyclic)),
					)
				)

	def on_update(self):
		self._export_template()

	def on_trash(self):
		self._delete_template()

	def _export_template(self):
		from frappe.modules.utils import export_module_json

		if not self.module:
			return

		export_module_json(self, True, self.module)
		self._export_account_categories()

	def _delete_template(self):
		if not self.module or not frappe.conf.developer_mode:
			return

		module_path = frappe.get_module_path(self.module)
		dir_path = os.path.join(module_path, "financial_report_template_enhanced", frappe.scrub(self.name))

		shutil.rmtree(dir_path, ignore_errors=True)

	def _export_account_categories(self):
		import json

		from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_engine import (
			FormulaFieldExtractor,
		)

		if not self.module or not frappe.conf.developer_mode or frappe.flags.in_import:
			return

		extractor = FormulaFieldExtractor(
			field_name="account_category", exclude_operators=["like", "not like"]
		)
		account_data_rows = [row for row in self.rows if row.data_source == "Account Data"]
		category_names = extractor.extract_from_rows(account_data_rows)

		if not category_names:
			return

		module_path = frappe.get_module_path(self.module)
		categories_file = os.path.join(
			module_path, "financial_report_template_enhanced", "account_categories.json"
		)

		existing_categories = {}
		if os.path.exists(categories_file):
			try:
				with open(categories_file) as f:
					existing_data = json.load(f)
					existing_categories = {cat["account_category_name"]: cat for cat in existing_data}
			except (json.JSONDecodeError, KeyError):
				pass

		if category_names:
			db_categories = frappe.get_all(
				"Account Category",
				filters={"account_category_name": ["in", list(category_names)]},
				fields=["account_category_name", "description"],
			)

			for cat in db_categories:
				existing_categories[cat["account_category_name"]] = cat

		sorted_categories = sorted(existing_categories.values(), key=lambda x: x["account_category_name"])

		os.makedirs(os.path.dirname(categories_file), exist_ok=True)
		with open(categories_file, "w") as f:
			json.dump(sorted_categories, f, indent=2)


def sync_financial_report_templates_enhanced(chart_of_accounts=None, existing_company=None):
	from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_chart

	if existing_company:
		return

	disable_default = False
	if chart_of_accounts:
		coa = get_chart(chart_of_accounts)
		if coa.get("disable_default_financial_report_template", False):
			disable_default = True

	for app in frappe.get_installed_apps():
		if disable_default and app == "erpnext":
			continue
		_sync_templates_for(app)


def _sync_templates_for(app_name):
	templates = []

	for module_name in frappe.local.app_modules.get(app_name) or []:
		module_path = frappe.get_module_path(module_name)
		template_path = os.path.join(module_path, "financial_report_template_enhanced")

		if not os.path.isdir(template_path):
			continue

		import_account_categories(template_path)

		for template_dir in os.listdir(template_path):
			json_file = os.path.join(template_path, template_dir, f"{template_dir}.json")
			if os.path.isfile(json_file):
				templates.append(json_file)

	if not templates:
		return

	frappe.flags.in_import = True

	for template_path in templates:
		with open(template_path) as f:
			template_data = frappe._dict(frappe.parse_json(f.read()))

		template_name = template_data.get("name")

		if not frappe.db.exists("Financial Report Template Enhanced", template_name):
			doc = frappe.get_doc(template_data)
			doc.flags.ignore_mandatory = True
			doc.flags.ignore_permissions = True
			doc.flags.ignore_validate = True
			doc.insert()

	frappe.flags.in_import = False
