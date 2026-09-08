// Copyright (c) 2026, Navari Ltd and contributors
// For license information, please see license.txt

const FSE_REPORT_NAME = "Financial Statement Enhanced";

frappe.query_reports[FSE_REPORT_NAME] = $.extend({}, erpnext.financial_statements);

erpnext.utils.add_dimensions(FSE_REPORT_NAME, 10);

frappe.query_reports[FSE_REPORT_NAME]["filters"].push(
	{
		fieldname: "report_template",
		label: __("Report Template"),
		fieldtype: "Link",
		options: "Financial Report Template Enhanced",
		get_query: { filters: { disabled: 0 } },
		reqd: 1,
	},
	{
		fieldname: "show_account_details",
		label: __("Account Detail Level"),
		fieldtype: "Select",
		options: ["Summary", "Account Breakdown"],
		default: "Summary",
		depends_on: "eval:doc.report_template",
	},
	{
		fieldname: "include_default_book_entries",
		label: __("Include Default FB Entries"),
		fieldtype: "Check",
		default: 1,
	}
);

// Datatable tree-indents the first column. Line Reference is first, so keep
// Account names indented in the formatter instead.
// Line Reference must stay Data: the custom-report formatter otherwise applies
// the row Value Type (usually Currency) and turns codes like "IM" into 0.00.
const fse_parent_formatter = frappe.query_reports[FSE_REPORT_NAME].formatter;
frappe.query_reports[FSE_REPORT_NAME].formatter = function (
	value,
	row,
	column,
	data,
	default_formatter,
	filter
) {
	const baseName = (column?.fieldname || "").replace(/^seg_\d+_/, "");

	if (baseName === "reference_code" || column.empty_column) {
		if (!data || erpnext.financial_statements.is_blank_row(data)) return "";

		const columnInfo = erpnext.financial_statements._parse_column_info(column.fieldname, data);
		const formatting = erpnext.financial_statements._get_formatting_for_column(
			data,
			columnInfo
		);
		if (formatting.is_blank_line) return "";

		const col = { ...column, fieldtype: "Data", options: null };
		const formattedValue = default_formatter(value == null ? "" : value, row, col, data);
		return erpnext.financial_statements._style_custom_value(formattedValue, formatting, null);
	}

	let formatted = fse_parent_formatter(value, row, column, data, default_formatter, filter);

	if (!data || !column?.fieldname || formatted === "") return formatted;

	if (baseName !== "account") return formatted;

	const totalSegments = data._segment_info?.total_segments || 1;
	if (totalSegments !== 1) return formatted;

	const indent = cint(data.indent);
	if (!indent) return formatted;

	return "&nbsp;".repeat(indent * 4) + formatted;
};

frappe.query_reports[FSE_REPORT_NAME]["export_hidden_cols"] = true;
