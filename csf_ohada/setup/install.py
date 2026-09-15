from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_template_enhanced import (
	sync_financial_report_templates_enhanced,
)
from csf_ohada.setup.account_category import import_account_categories


def sync_default_records():
	"""Create the app's default account categories and financial report templates."""
	import_account_categories()
	sync_financial_report_templates_enhanced()
