import json
import os

import frappe
from frappe.model.document import bulk_insert


def import_account_categories():
	file_path = os.path.join(os.path.dirname(__file__), "account_categories.json")

	with open(file_path) as f:
		categories = json.load(f)

	create_account_categories(categories)


def create_account_categories(categories: list[dict]):
	if not categories:
		return

	existing_categories = set(frappe.get_all("Account Category", pluck="name"))
	new_categories = []

	for category_data in categories:
		category_name = category_data.get("account_category_name")
		if not category_name or category_name in existing_categories:
			continue

		doc = frappe.get_doc(
			{
				**category_data,
				"doctype": "Account Category",
				"name": category_name,
			}
		)

		new_categories.append(doc)
		existing_categories.add(category_name)

	if new_categories:
		bulk_insert("Account Category", new_categories)
