from csf_ohada.csf_ohada.doctype.ohada_financial_report_template.ohada_financial_report_template import (
	sync_ohada_financial_report_templates,
)
from csf_ohada.setup.account_category import import_account_categories


def sync_default_records():
	"""Create the app's default account categories and financial report templates."""
	import_account_categories()
	sync_ohada_financial_report_templates()
