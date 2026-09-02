# CSF OHADA

[![fr](https://img.shields.io/badge/lang-fr-green.svg)](./README.md)

ERPNext customizations and compliance features for entities operating within the OHADA accounting framework. This app extends standard ERPNext reporting with OHADA-oriented financial statements

## Reports

### Reports powered by Financial Report Template Enhanced

**Financial Report Template Enhanced** Financial Report Template Enhanced is a template builder for defining any financial report layout, not limited to a fixed set of statements. Once a template is configured, run it from **Financial Statement Enhanced**.

Common reports configured using this app include:

| Reports             | Description                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| **Profit and Loss** | Income statement showing revenue, expenses, and net profit for a period. |
| **Balance Sheet**   | Statement of financial position with assets, liabilities, and equity.    |
| **Cash Flow**       | Statement of cash inflows and outflows.                                  |

You can also define custom statements beyond these examples. Templates are configured once and reused, no need to rebuild reports in Excel each period.

## Financial Report Template Enhanced

Financial Report Template Enhanced builds on ERPNext's Financial Report Template. It is a flexible blueprint for any financial statement you need to produce from **Financial Statement Enhanced**.

**What it achieves**

- **Configurable value columns** - define named value columns (for example Gross Value, Net Value, Depreciation) that expand across each report period. Leave value columns empty to keep ERPNext-style behaviour with one value column per period.
- **Per-column rules** - override balance type, account filters, or formulas for individual value columns without duplicating rows.
- **Professional layout** - bold headings, indentation, colour, hide-if-zero, debit/credit side filtering, and chart support.
- **Single run point** - all enhanced templates are executed from Financial Statement Enhanced, keeping report generation in one place.

## Other reports

| Report                            | Based on             | What it adds                                                                                                          |
| --------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Fixed Asset Register Enhanced** | Fixed Asset Register | Revaluation amounts, chart-of-accounts numbers (when grouped by asset category), and depreciation rates per category. |

## Documentation

Step-by-step setup guides, template configuration, formula reference, and validation rules are available in the full documentation:

**[docs.navari.co.ke](https://docs.navari.co.ke)**

## Installation

Install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app csf_ohada
```

## Contributing

This app uses `pre-commit` for code formatting and linting. Please install pre-commit and enable it for this repository:

```bash
cd apps/csf_ohada
pre-commit install
```

Pre-commit is configured to use the following tools:

- ruff
- eslint
- prettier
- pyupgrade

## CI

This app uses GitHub Actions for CI. The following workflows are configured:

- **CI:** Installs this app and runs unit tests on every push to the `develop` branch.
- **Linters:** Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

## License

AGPL-3.0
