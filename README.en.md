# CSF OHADA

[![fr](https://img.shields.io/badge/lang-fr-green.svg)](./README.md)

ERPNext customizations and compliance features for entities operating within the OHADA accounting framework. This app provides SYSCOHADA charts of accounts for all 17 OHADA member countries and extends standard ERPNext reporting with OHADA-oriented financial statements.

## OHADA member countries

CSF OHADA currently covers the 17 member states of [OHADA](https://www.ohada.org/) (Organisation pour l'Harmonisation en Afrique du Droit des Affaires):

| Country                          | Code |
| -------------------------------- | ---- |
| Benin                            | BJ   |
| Burkina Faso                     | BF   |
| Cameroon                         | CM   |
| Central African Republic         | CF   |
| Chad                             | TD   |
| Comoros                          | KM   |
| Côte d'Ivoire                    | CI   |
| Democratic Republic of the Congo | CD   |
| Equatorial Guinea                | GQ   |
| Gabon                            | GA   |
| Guinea                           | GN   |
| Guinea-Bissau                    | GW   |
| Mali                             | ML   |
| Niger                            | NE   |
| Republic of the Congo            | CG   |
| Senegal                          | SN   |
| Togo                             | TG   |

## Chart of Accounts

This app overrides ERPNext's chart-of-accounts lookup so **Company** setup loads SYSCOHADA templates for the countries above, instead of only the charts bundled with ERPNext.

When you create a company in an OHADA member country, the following plans are available:

| Template                                  | Description                                                                                                                                                                                                 |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Syscohada - Plan Comptable**            | SYSCOHADA account tree with class and account codes in the account names (for example `1011-Capital souscrit, non appelé`).                                                                                 |
| **Syscohada - Plan Comptable avec code**  | Same SYSCOHADA tree with a dedicated account number on each account. Posting and subdivision accounts use 6-digit numbers (trailing zeros). Class accounts (1–8) and two-digit group headings stay short. |

ERPNext **Standard** and **Standard with Numbers** charts remain available. Regional templates for non-OHADA countries are also bundled so company setup still finds a chart when this app is installed.

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
