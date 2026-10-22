frappe.provide("erpnext.setup");

// Setup wizard scripts load in parallel, so patch ERPNext's slide once all of them have run
frappe.setup.on("before_load", function () {
	const organization_slide = (erpnext.setup.slides_settings || []).find(
		(slide) => slide.name === "organization"
	);
	if (!organization_slide) return;

	// Load chart of accounts options from csf_ohada so OHADA charts are listed in the setup wizard
	organization_slide.load_chart_of_accounts = function (slide) {
		let country = frappe.wizard.values.country || frappe.defaults.get_default("country");

		if (country) {
			frappe.call({
				method: "csf_ohada.overrides.chart_of_accounts.chart_of_accounts.get_charts_for_country",
				args: { country: country, with_standard: true },
				callback: function (r) {
					if (r.message) {
						slide.get_input("chart_of_accounts").empty().add_options(r.message);
					}
				},
			});
		}
	};

	// Same as ERPNext's charts_modal, but the tree is loaded via csf_ohada's get_coa
	organization_slide.charts_modal = function (slide, chart_template) {
		let parent = __("All Accounts");

		let dialog = new frappe.ui.Dialog({
			title: chart_template,
			fields: [
				{
					fieldname: "expand_all",
					label: __("Expand All"),
					fieldtype: "Button",
					click: function () {
						// expand all nodes on button click
						coa_tree.load_children(coa_tree.root_node, true);
					},
				},
				{
					fieldname: "collapse_all",
					label: __("Collapse All"),
					fieldtype: "Button",
					click: function () {
						coa_tree
							.get_all_nodes(
								coa_tree.root_node.data.value,
								coa_tree.root_node.is_root
							)
							.then((data_list) => {
								data_list.map((d) => {
									coa_tree.toggle_node(coa_tree.nodes[d.parent]);
								});
							});
					},
				},
			],
		});

		// render tree structure in the dialog modal
		let coa_tree = new frappe.ui.Tree({
			parent: $(dialog.body),
			label: parent,
			expandable: true,
			row_style: true,
			method: "csf_ohada.overrides.chart_of_accounts.chart_of_accounts.get_coa",
			args: {
				chart: chart_template,
				parent: parent,
				doctype: "Account",
			},
			onclick: function (node) {
				parent = node.value;
			},
		});

		// add class to show buttons side by side
		const form_container = $(dialog.body).find("form");
		const buttons = $(form_container).find(".frappe-control");
		form_container.addClass("flex");
		buttons.map((index, button) => {
			$(button).css({ "margin-right": "1em" });
		});

		dialog.show();
		coa_tree.load_children(coa_tree.root_node, true);
	};
});
