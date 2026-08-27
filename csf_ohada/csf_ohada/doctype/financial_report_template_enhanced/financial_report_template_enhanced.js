// Copyright (c) 2026, Navari Ltd and contributors
// Based on ERPNext Financial Report Template
// For license information, please see license.txt

frappe.ui.form.on("Financial Report Template Enhanced", {
	refresh(frm) {
		collapse_legacy_overrides(frm);

		if (frm.is_new() || !frm.doc.rows || frm.doc.rows.length === 0) return;

		// add custom button to view missed accounts
		frm.add_custom_button(__("View Account Coverage"), function () {
			let selected_rows = frm.get_field("rows").grid.get_selected_children();
			const has_selection = selected_rows.length > 0;
			if (selected_rows.length === 0) selected_rows = frm.doc.rows;

			show_accounts_tree(selected_rows, has_selection);
		});

		// add custom button to open the financial report
		frm.add_custom_button(__("View Report"), function () {
			frappe.set_route("query-report", "Financial Statement Enhanced", {
				report_template: frm.doc.name,
			});
		});
	},

	after_save(frm) {
		if (!frm.doc.rows || frm.doc.rows.length === 0) {
			frappe.msgprint(
				__("At least one row is required for a financial report template enhanced")
			);
		}
	},

	columns_remove(frm) {
		prune_stale_column_settings_on_form(frm);
		refresh_open_column_settings_editors(frm);
	},
});

frappe.ui.form.on("Financial Report Row Enhanced", {
	data_source(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		update_formula_label(frm, row.data_source);
		update_formula_description(frm, row.data_source);

		set_up_filters_editor(frm, cdt, cdn);
		set_up_column_settings_editor(frm, cdt, cdn);
	},

	form_render(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		update_formula_label(frm, row.data_source);
		update_advanced_formula_property(frm, cdt, cdn);
		set_up_filters_editor(frm, cdt, cdn);
		set_up_column_settings_editor(frm, cdt, cdn);
		update_formula_description(frm, row.data_source);
	},

	calculation_formula(frm, cdt, cdn) {
		update_advanced_formula_property(frm, cdt, cdn);
	},

	advanced_filtering(frm, cdt, cdn) {
		set_up_filters_editor(frm, cdt, cdn);
		set_up_column_settings_editor(frm, cdt, cdn);
	},
});

// FILTERS EDITOR

function set_up_filters_editor(frm, cdt, cdn) {
	const row = locals[cdt][cdn];

	if (row.data_source !== "Account Data" || row.advanced_filtering) return;

	const grid_row = frm.fields_dict["rows"].grid.get_row(cdn);
	const wrapper = grid_row.get_field("filters_editor").$wrapper;
	wrapper.empty();

	const ACCOUNT = "Account";
	const FIELD_IDX = 1;
	const OPERATOR_IDX = 2;
	const VALUE_IDX = 3;

	// Parse saved filters
	let saved_filters = [];

	if (row.calculation_formula) {
		try {
			const parsed = JSON.parse(row.calculation_formula);

			if (Array.isArray(parsed)) saved_filters = [parsed];
			else if (parsed.and) saved_filters = parsed.and;
		} catch (e) {
			frappe.show_alert({
				message: __("Invalid filter formula. Please check the syntax."),
				indicator: "red",
			});
		}
	}

	if (saved_filters.length)
		// Ensure every filter starts with "Account"
		saved_filters = saved_filters.map((f) => [ACCOUNT, ...f]);

	frappe.model.with_doctype(ACCOUNT, () => {
		const filter_group = new frappe.ui.FilterGroup({
			parent: wrapper,
			doctype: ACCOUNT,
			on_change: () => {
				// only need [[field, operator, value]]
				const filters = filter_group
					.get_filters()
					.map((f) => [f[FIELD_IDX], f[OPERATOR_IDX], f[VALUE_IDX]]);

				const current = filters.length > 1 ? { and: filters } : filters[0];
				frappe.model.set_value(cdt, cdn, "calculation_formula", JSON.stringify(current));
			},
		});

		filter_group.add_filters_to_filter_group(saved_filters);
	});
}

function update_advanced_formula_property(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const is_advanced = is_advanced_formula(row);

	frm.set_df_property("rows", "read_only", is_advanced, frm.doc.name, "advanced_filtering", cdn);

	if (is_advanced && !row.advanced_filtering) {
		row.advanced_filtering = 1;
		frm.refresh_field("rows");
	}
}

function is_advanced_formula(row) {
	if (!row || row.data_source !== "Account Data") return false;

	let parsed = null;
	if (row.calculation_formula) {
		try {
			parsed = JSON.parse(row.calculation_formula);
		} catch (e) {
			console.warn("Invalid JSON in calculation_formula:", e);
			return false;
		}
	}

	if (Array.isArray(parsed)) return false;
	if (parsed?.or) return true;
	if (parsed?.and) return parsed.and.some((cond) => !Array.isArray(cond));

	return false;
}

// ACCOUNTS TREE VIEW

function show_accounts_tree(template_rows, has_selection) {
	// filtered rows
	const account_rows = template_rows.filter((row) => row.data_source === "Account Data");

	if (account_rows.length === 0) {
		frappe.show_alert(__("No <strong>Account Data</strong> row found"));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("Accounts Missing from Report"),
		fields: [
			{
				fieldname: "company",
				fieldtype: "Link",
				options: "Company",
				label: "Company",
				reqd: 1,
				default: frappe.defaults.get_user_default("Company"),
				onchange: () => {
					const company_field = dialog.get_field("company");
					if (!company_field.value || company_field.value === company_field.last_value)
						return;
					refresh_tree_view(dialog, account_rows);
				},
			},
			{
				fieldname: "view_type",
				fieldtype: "Select",
				options: ["Missing Accounts", "Filtered Accounts"],
				label: "View",
				default: has_selection ? "Filtered Accounts" : "Missing Accounts",
				reqd: 1,
				onchange: () => {
					dialog.set_title(
						dialog.get_value("view_type") === "Missing Accounts"
							? __("Accounts Missing from Report")
							: __("Accounts Included in Report")
					);

					refresh_tree_view(dialog, account_rows);
				},
			},
			{
				fieldname: "tip",
				fieldtype: "HTML",
				label: "Tip",
				options: `
					<div class="alert alert-success" role="alert">
							Tip: Select report lines to view their accounts
					</div>
				`,
				depends_on: has_selection ? "eval: false" : "eval: true",
			},
			{
				fieldname: "tree_area",
				fieldtype: "HTML",
				label: "Chart of Accounts",
				read_only: 1,
				depends_on: "eval: doc.company",
			},
		],
		primary_action_label: __("Done"),
		primary_action() {
			dialog.hide();
		},
	});

	dialog.show();
	refresh_tree_view(dialog, account_rows);
}

async function refresh_tree_view(dialog, account_rows) {
	const missed = dialog.get_value("view_type") === "Missing Accounts";
	const company = dialog.get_value("company");

	const wrapper = dialog.get_field("tree_area").$wrapper;
	wrapper.empty();

	// get filtered accounts
	const { message: filtered_accounts } = await frappe.call({
		method: "csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_engine.get_filtered_accounts",
		args: { company: company, account_rows: account_rows },
	});

	// render tree
	const tree = new FilteredTree({
		parent: wrapper,
		label: company,
		root_value: company,
		method: "csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_engine.get_children_accounts",
		args: {
			doctype: "Account",
			company: company,
			filtered_accounts: filtered_accounts,
			missed: missed,
		},
		toolbar: [],
	});

	tree.load_children(tree.root_node, true);
}

class FilteredTree extends frappe.ui.Tree {
	render_children_of_all_nodes(data_list) {
		data_list = this.get_filtered_data_list(data_list);
		super.render_children_of_all_nodes(data_list);
	}

	get_filtered_data_list(data_list) {
		let removed_nodes = new Set();

		// Filter nodes with no data
		data_list = data_list.filter((d) => {
			if (d.data.length === 0) {
				removed_nodes.add(d.parent);
				return false;
			}
			return true;
		});

		// Remove references to removed nodes and iteratively remove empty parents
		while (removed_nodes.size > 0) {
			const current_removed = [...removed_nodes];
			removed_nodes.clear();

			data_list = data_list.filter((d) => {
				d.data = d.data.filter((a) => !current_removed.includes(a.value));

				if (d.data.length === 0) {
					removed_nodes.add(d.parent);
					return false;
				}
				return true;
			});
		}

		return data_list;
	}
}

function update_formula_label(frm, data_source) {
	const grid = frm.fields_dict.rows.grid;
	const field = grid.fields_map.calculation_formula;
	if (!field) return;

	const labels = {
		"Account Data": "Account Filter",
		"Custom API": "API Method Path",
	};

	grid.update_docfield_property(
		"calculation_formula",
		"label",
		labels[data_source] || "Calculation Formula"
	);
}

// FORMULA DESCRIPTION

function update_formula_description(frm, data_source) {
	if (!data_source) return;

	let grid = frm.fields_dict.rows.grid;
	let field = grid.fields_map.formula_description;
	if (!field) return;

	// Common CSS styles and elements
	const container_style = `style="padding: var(--padding-md); border: 1px solid var(--border-color); border-radius: var(--border-radius); margin-top: var(--margin-sm);"`;
	const title_style = `style="margin-top: 0; color: var(--text-color);"`;
	const subtitle_style = `style="color: var(--text-color); margin-bottom: var(--margin-xs);"`;
	const text_style = `style="margin-bottom: var(--margin-sm); color: var(--text-muted);"`;
	const list_style = `style="margin-bottom: var(--margin-sm); color: var(--text-muted); font-size: 0.9em;"`;
	const note_style = `style="margin-bottom: 0; color: var(--text-muted); font-size: 0.9em;"`;
	const tip_style = `style="margin-bottom: 0; color: var(--text-color); font-size: 0.85em;"`;
	const code_style = `style="background: var(--bg-light-gray); padding: var(--padding-xs); border-radius: var(--border-radius); font-size: 0.85em; width: max-content; margin-bottom: var(--margin-sm);"`;
	const pre_style = `style="margin: 0; border-radius: var(--border-radius)"`;

	let description_html = "";

	if (data_source === "Account Data") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Account Filter Guide</h5>
				<p ${text_style}>Specify which accounts to include in this line.</p>

				<h6 ${subtitle_style}>Basic Examples:</h6>
				<ul ${list_style}>
					<li><code>["account_type", "=", "Cash"]</code> - All Cash accounts</li>
					<li><code>["root_type", "in", ["Asset", "Liability"]]</code> - All Asset and Liability accounts</li>
					<li><code>["account_category", "like", "Revenue"]</code> - Revenue accounts</li>
				</ul>

				<h6 ${subtitle_style}>Multiple Conditions (AND/OR):</h6>
				<ul ${list_style}>
					<li><code>{"and": [["root_type", "=", "Asset"], ["account_type", "=", "Cash"]]}</code></li>
					<li><code>{"or": [["account_category", "like", "Revenue"], ["account_category", "like", "Income"]]}</code></li>
				</ul>

				<p ${note_style}><strong>Available operators:</strong> <code>=, !=, in, not in, like, not like, is</code></p>
				<p ${tip_style}><strong>Balance Filter:</strong> Use <code>Debit Accounts</code> / <code>Credit Accounts</code> to place only those accounts on this line (the counterpart row keeps the other sign). Use <code>Net Debit</code> / <code>Net Credit</code> to move the whole line when the overall balance (last visible column) has that sign. Pair with Hide If Zero. Sign is debit minus credit, before Reverse Sign.</p>
				<p ${tip_style}><strong>Multi-Company Tip:</strong> Use fields like <code>account_type</code>, <code>root_type</code>, and <code>account_category</code> for templates that work across multiple companies.</p>
			</div>`;
	} else if (data_source === "Calculated Amount") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Formula Guide</h5>
				<p ${text_style}>Create calculations using reference codes from other lines.</p>

				<h6 ${subtitle_style}>Basic Examples:</h6>
				<ul ${list_style}>
					<li><code>REV100 + REV200</code> - Add two revenue lines</li>
					<li><code>ASSETS - LIABILITIES</code> - Calculate equity</li>
					<li><code>REVENUE * 0.1</code> - 10% of revenue</li>
				</ul>

				<h6 ${subtitle_style}>Common Functions:</h6>
				<ul ${list_style}>
					<li><code>abs(value)</code> - Remove negative sign</li>
					<li><code>round(value)</code> - Round to whole number</li>
					<li><code>max(val1, val2)</code> - Larger of two values</li>
					<li><code>min(val1, val2)</code> - Smaller of two values</li>
				</ul>

				<p ${note_style}><strong>Required:</strong> Use "Reference Code" from other rows in your formulas.</p>
			</div>`;
	} else if (data_source === "Custom API") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Custom API Setup</h5>
				<p ${text_style}>Path to your custom method that returns financial data.</p>

				<h6 ${subtitle_style}>Format:</h6>
				<ul ${list_style}>
					<li><code>erpnext.custom.financial_apis.get_custom_revenue</code></li>
					<li><code>my_app.financial_reports.get_kpi_data</code></li>
				</ul>

				<h6 ${subtitle_style}>Method Signature:</h6>
				<div ${code_style}>
					<pre ${pre_style}>def get_custom_data(filters, periods, row): <br>&nbsp; # filters: dict — report filters (company, period, etc.) <br>&nbsp; # periods: list[dict] — period definitions <br>&nbsp; # row: dict — the current report row <br><br>&nbsp; return [1000.0, 1200.0, 1150.0]  # one value per period</pre>
				</div>

				<h6 ${subtitle_style}>Return Format:</h6>
				<p ${text_style}>A list of numbers, one for each period: <code>[1000.0, 1200.0, 1150.0]</code></p>
			</div>`;
	} else if (data_source === "Blank Line") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Blank Line</h5>
				<p ${text_style}>Adds empty space for better visual separation.</p>

				<h6 ${subtitle_style}>Use For:</h6>
				<ul ${list_style}>
					<li>Separating major sections</li>
					<li>Adding space before totals</li>
				</ul>

				<p ${note_style}><strong>Note:</strong> No formula needed - creates visual spacing only.</p>
			</div>`;
	} else if (data_source === "Column Break") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Column Break</h5>
				<p ${text_style}>Creates a visual break for side-by-side layout.</p>

				<h6 ${subtitle_style}>Use For:</h6>
				<ul ${list_style}>
					<li>Horizontal P&L statements</li>
					<li>Side-by-side Balance Sheet sections</li>
				</ul>

				<p ${note_style}><strong>Note:</strong> No formula needed - this is for formatting only.</p>
			</div>`;
	} else if (data_source === "Section Break") {
		description_html = `
			<div ${container_style}>
				<h5 ${title_style}>Section Break</h5>
				<p ${text_style}>Creates a visual break for separating different sections.</p>

				<h6 ${subtitle_style}>Use For:</h6>
				<ul ${list_style}>
					<li>Separating major sections in a report - say trading & profit and loss</li>
					<li>Improving readability by adding space</li>
				</ul>

				<p ${note_style}><strong>Note:</strong> No formula needed - this is for formatting only.</p>
			</div>`;
	}

	grid.update_docfield_property("formula_description", "options", description_html);
}

// COLUMN SETTINGS (per value column on the row)

const STYLE_DATA_SOURCES = ["Blank Line", "Column Break", "Section Break", "Custom API"];
const BALANCE_TYPE_OPTIONS = [
	"",
	"Opening Balance",
	"Closing Balance",
	"Period Movement (Debits - Credits)",
	"Debits",
	"Credits",
];

frappe.ui.form.on("Financial Report Column Enhanced", {
	column_code(frm) {
		refresh_open_column_settings_editors(frm);
	},
	label(frm) {
		refresh_open_column_settings_editors(frm);
	},
	default_is_formula(frm) {
		refresh_open_column_settings_editors(frm);
	},
	default_calculation_formula(frm) {
		refresh_open_column_settings_editors(frm);
	},
	default_balance_type(frm) {
		refresh_open_column_settings_editors(frm);
	},
});

function collapse_legacy_overrides(frm) {
	const section = frm.get_field("section_break_overrides");
	if (section && typeof section.collapse === "function") {
		section.collapse(true);
	}
}

function refresh_open_column_settings_editors(frm) {
	const grid = frm.fields_dict.rows && frm.fields_dict.rows.grid;
	if (!grid) return;

	(grid.grid_rows || []).forEach((grid_row) => {
		if (grid_row && grid_row.grid_form && grid_row.doc) {
			set_up_column_settings_editor(frm, grid_row.doc.doctype, grid_row.doc.name);
		}
	});
}

function parse_column_settings(row) {
	if (!row || !row.column_settings) return {};
	if (typeof row.column_settings === "object") return { ...row.column_settings };
	try {
		return JSON.parse(row.column_settings) || {};
	} catch (e) {
		return {};
	}
}

function save_column_settings(cdt, cdn, settings) {
	const cleaned = {};
	for (const [code, val] of Object.entries(settings || {})) {
		if (!val || val.use_default) continue;
		cleaned[code] = {
			balance_type: val.balance_type || "",
			is_formula: val.is_formula ? 1 : 0,
			calculation_formula: val.calculation_formula || "",
		};
	}
	const json = Object.keys(cleaned).length ? JSON.stringify(cleaned) : "";
	frappe.model.set_value(cdt, cdn, "column_settings", json);
}

function value_columns(frm) {
	return (frm.doc.columns || []).filter((col) => (col.column_code || "").trim());
}

function prune_stale_column_settings_on_form(frm) {
	const valid_codes = new Set(
		value_columns(frm)
			.map((col) => (col.column_code || "").trim())
			.filter(Boolean)
	);

	for (const row of frm.doc.rows || []) {
		const settings = parse_column_settings(row);
		const pruned = {};
		for (const [code, val] of Object.entries(settings)) {
			if (valid_codes.has(code)) {
				pruned[code] = val;
			}
		}
		if (Object.keys(pruned).length !== Object.keys(settings).length) {
			frappe.model.set_value(
				row.doctype,
				row.name,
				"column_settings",
				Object.keys(pruned).length ? JSON.stringify(pruned) : ""
			);
		}
	}
}

function column_default_hint(col) {
	if (cint(col.default_is_formula) && col.default_calculation_formula) {
		return __("Column default: {0}", [col.default_calculation_formula]);
	}
	if (col.default_calculation_formula) {
		return __("Column default filter is set");
	}
	if (col.default_balance_type) {
		return __("Column default balance: {0}", [col.default_balance_type]);
	}
	return "";
}

function set_up_column_settings_editor(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const grid = frm.fields_dict.rows && frm.fields_dict.rows.grid;
	const grid_row = grid && grid.get_row(cdn);
	if (!grid_row) return;

	const field = grid_row.get_field("column_settings_editor");
	if (!field) return;

	const wrapper = field.$wrapper;
	wrapper.empty();

	if (!row || STYLE_DATA_SOURCES.includes(row.data_source)) return;

	const columns = value_columns(frm);
	if (!columns.length) {
		wrapper.html(
			`<p class="text-muted" style="margin-top: var(--margin-sm);">${__(
				"Add Value Columns to set a different filter or formula per column on this line."
			)}</p>`
		);
		return;
	}

	const settings = parse_column_settings(row);
	const is_account = row.data_source === "Account Data";
	const is_calculated = row.data_source === "Calculated Amount";

	const panel = $(`
		<div class="column-settings-panel" style="margin-top: var(--margin-sm);">
			<p class="text-muted" style="margin-bottom: var(--margin-sm);">
				${__(
					"Row fields apply to every value column. Customise a column here only when it should differ. Keys left on row default use the Value Column default, then this line's Balance Type and Formula."
				)}
			</p>
		</div>
	`);
	wrapper.append(panel);

	columns.forEach((col) => {
		const code = (col.column_code || "").trim();
		const stored = settings[code] || {};
		const use_default = !settings[code];
		const state = {
			use_default,
			balance_type: stored.balance_type || "",
			is_formula: is_calculated ? 1 : cint(stored.is_formula),
			calculation_formula: stored.calculation_formula || "",
		};

		const card = render_column_setting_card(col, code, state, is_account, is_calculated);
		panel.append(card);

		bind_column_setting_card({
			frm,
			cdt,
			cdn,
			row,
			code,
			state,
			settings,
			card,
			is_account,
			is_calculated,
		});
	});
}

function render_column_setting_card(col, code, state, is_account, is_calculated) {
	const hint = column_default_hint(col);
	const label = col.label
		? `${frappe.utils.escape_html(code)} — ${frappe.utils.escape_html(col.label)}`
		: frappe.utils.escape_html(code);
	const balance_options = BALANCE_TYPE_OPTIONS.map(
		(opt) =>
			`<option value="${frappe.utils.escape_html(opt)}" ${
				state.balance_type === opt ? "selected" : ""
			}>${frappe.utils.escape_html(opt || __("Row default"))}</option>`
	).join("");

	return $(`
		<div class="column-setting-card" data-column-code="${frappe.utils.escape_html(code)}"
			style="border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: var(--padding-sm); margin-bottom: var(--margin-sm);">
			<div class="flex justify-between align-center" style="gap: var(--margin-sm); flex-wrap: wrap;">
				<strong>${label}</strong>
				<label class="mb-0">
					<input type="checkbox" class="cs-use-default" ${state.use_default ? "checked" : ""}>
					${__("Use row default")}
				</label>
			</div>
			${
				hint
					? `<p class="text-muted small mb-0" style="margin-top: 4px;">${frappe.utils.escape_html(
							hint
					  )}</p>`
					: ""
			}
			<div class="cs-custom" style="margin-top: var(--margin-sm); ${
				state.use_default ? "display: none;" : ""
			}">
				${
					is_account
						? `<div class="form-group">
							<label class="control-label">${__("Balance Type")}</label>
							<select class="form-control cs-balance-type">${balance_options}</select>
						</div>
						<div class="checkbox">
							<label>
								<input type="checkbox" class="cs-is-formula" ${state.is_formula ? "checked" : ""}>
								${__("Evaluate as Formula")}
							</label>
						</div>`
						: ""
				}
				<div class="cs-formula-area"></div>
			</div>
		</div>
	`);
}

function bind_column_setting_card(ctx) {
	const { cdt, cdn, code, state, settings, card, is_account, is_calculated } = ctx;

	const persist = () => {
		settings[code] = { ...state };
		save_column_settings(cdt, cdn, settings);
	};

	const render_formula_area = () => {
		const area = card.find(".cs-formula-area");
		area.empty();
		if (state.use_default) return;

		const show_formula = is_calculated || state.is_formula;
		if (show_formula) {
			area.append(`
				<div class="form-group">
					<label class="control-label">${__("Formula")}</label>
					<textarea class="form-control cs-formula" rows="3">${frappe.utils.escape_html(
						state.calculation_formula || ""
					)}</textarea>
				</div>
			`);
			area.find(".cs-formula").on("change input", function () {
				state.calculation_formula = $(this).val();
				persist();
			});
			return;
		}

		if (is_account && ctx.row.advanced_filtering) {
			area.append(`
				<div class="form-group">
					<label class="control-label">${__("Account Filter")}</label>
					<textarea class="form-control cs-formula" rows="3">${frappe.utils.escape_html(
						state.calculation_formula || ""
					)}</textarea>
				</div>
			`);
			area.find(".cs-formula").on("change input", function () {
				state.calculation_formula = $(this).val();
				persist();
			});
			return;
		}

		if (is_account) {
			mount_column_filter_group(area, state, persist);
		}
	};

	card.find(".cs-use-default").on("change", function () {
		state.use_default = this.checked;
		card.find(".cs-custom").toggle(!state.use_default);
		if (state.use_default) {
			delete settings[code];
			save_column_settings(cdt, cdn, settings);
		} else {
			persist();
			render_formula_area();
		}
	});

	card.find(".cs-balance-type").on("change", function () {
		state.balance_type = $(this).val();
		persist();
	});

	card.find(".cs-is-formula").on("change", function () {
		state.is_formula = this.checked ? 1 : 0;
		if (!state.is_formula && looks_like_formula(state.calculation_formula)) {
			state.calculation_formula = "";
		}
		persist();
		render_formula_area();
	});

	render_formula_area();
}

function looks_like_formula(value) {
	if (!value) return false;
	const trimmed = String(value).trim();
	return trimmed && !["[", "{"].includes(trimmed[0]);
}

function mount_column_filter_group(area, state, persist) {
	const ACCOUNT = "Account";
	const FIELD_IDX = 1;
	const OPERATOR_IDX = 2;
	const VALUE_IDX = 3;
	const filter_parent = $('<div class="cs-filter-group"></div>');
	area.append(filter_parent);

	let saved_filters = [];
	if (state.calculation_formula) {
		try {
			const parsed = JSON.parse(state.calculation_formula);
			if (Array.isArray(parsed)) saved_filters = [parsed];
			else if (parsed.and) saved_filters = parsed.and;
		} catch (e) {
			filter_parent.append(
				`<p class="text-danger">${__("Invalid filter. Please check the syntax.")}</p>`
			);
		}
	}

	if (saved_filters.length) {
		saved_filters = saved_filters.map((f) => [ACCOUNT, ...f]);
	}

	frappe.model.with_doctype(ACCOUNT, () => {
		const filter_group = new frappe.ui.FilterGroup({
			parent: filter_parent,
			doctype: ACCOUNT,
			on_change: () => {
				const filters = filter_group
					.get_filters()
					.map((f) => [f[FIELD_IDX], f[OPERATOR_IDX], f[VALUE_IDX]]);
				if (!filters.length) {
					state.calculation_formula = "";
				} else {
					const current = filters.length > 1 ? { and: filters } : filters[0];
					state.calculation_formula = JSON.stringify(current);
				}
				persist();
			},
		});

		if (saved_filters.length) {
			filter_group.add_filters_to_filter_group(saved_filters);
		}
	});
}
