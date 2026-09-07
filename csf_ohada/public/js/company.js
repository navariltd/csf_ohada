frappe.provide("erpnext.company");

frappe.ui.form.on("Company", {
	refresh: function (frm) {
		erpnext.company.set_chart_of_accounts_options(frm.doc);
	},

	country: function (frm) {
		erpnext.company.set_chart_of_accounts_options(frm.doc);
	},
});

erpnext.company.set_chart_of_accounts_options = function (doc) {
	var selected_value = doc.chart_of_accounts;
	if (doc.country) {
		return frappe.call({
			method: "csf_ohada.overrides.chart_of_accounts.chart_of_accounts.get_charts_for_country",
			args: {
				country: doc.country,
				with_standard: true,
			},
			callback: function (r) {
				console.log("RESPONSE", r);
				if (!r.exc) {
					set_field_options("chart_of_accounts", [""].concat(r.message).join("\n"));
					if (r.message.includes(selected_value))
						cur_frm.set_value("chart_of_accounts", selected_value);
				}
			},
		});
	}
};
