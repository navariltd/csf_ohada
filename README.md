### Csf Ohada

A collection of ERPNext customizations, regional settings, and compliance features designed for businesses operating in Francophone countries

### Primary Features

#### Financial Report Template Enhanced

Financial Report Template Enhanced builds on ERPNext Financial Report Templates to create professional financial reports that fit dynamic business needs, including OHADA-style statements with multiple value columns (for example Gross Value and Net Value) for the same line.

Instead of editing reports in Excel, set up a template once and generate Balance Sheets, Profit & Loss statements, Cash Flow reports, or custom statements from **Financial Statement Enhanced**.

##### What is different from ERPNext?

| ERPNext template                                          | Financial Report Template Enhanced                                                                 |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| One value column per report period                        | Named **Value Columns** (Gross, Net, …) expanded across periods                                    |
| Balance type / formula apply to the whole row             | Same defaults on the row, with optional **per-column settings** (and Value Column defaults)        |
| Run from Balance Sheet / P&L / Custom Financial Statement | Run from **Financial Statement Enhanced**                                                          |

Leave Value Columns empty to keep ERPNext-style behaviour (one value column per period).

##### Main Components

###### 1. Financial Report Template Enhanced

This is the report blueprint. It defines:

- **Template Name:** Descriptive name for identification (e.g., "OHADA Balance Sheet")
- **Report Type:** Balance Sheet, Profit & Loss, Cash Flow, or Custom (metadata; the report is always run from Financial Statement Enhanced)
- **Value Columns:** Named measures such as Gross Value or Net Value (optional). Each column can declare a default formula or balance type for every row.
- **Rows:** The individual lines that make up the report. Expand a line to set a different filter or formula per value column.

###### 2. Financial Report Row Enhanced (Child Table)

Each row represents a line in the financial report:

- **Display Name:** What appears in the report (e.g., "Machinery and Equipment")
- **Reference Code (Line Reference):** Short code for calculations (e.g., `FA_MACHINES`, `REV100`)
- **Data Source:** Where the numbers come from:
  - **Account Data:** Pulls balances from the Chart of Accounts
  - **Calculated Amount:** Uses formulas based on other rows (and value columns when a column setting or column default replaces the row formula)
  - **Custom API:** Calls a custom Python method
  - **Visual Elements:** Blank Line, Column Break, or Section Break for layout
- **Balance Type:** Default for Account Data rows (Opening, Closing, Period Movement, Debits, or Credits) unless a column setting or Value Column default replaces it
- **Balance Filter:** For Account Data rows, which GL balances to include (see below)
- **Value Column Settings:** When Value Columns are defined, expand the line and customise only the columns that should differ from this row (and from the column default)
- **Formatting:** Bold, italic, colour, indentation, hide if zero, reverse sign, include in charts

###### 3. Financial Report Column Enhanced (Value Columns)

Value Columns define _what kinds of amounts_ appear, not which period. Report filters still generate periods; the engine builds report columns as **value column × period**.

For each value column:

- **Column Code:** Used in column settings and formulas (e.g., `GROSS`, `DEPR`, `NET`)
- **Label:** Base title (e.g., "Gross Value", "Net Value")
- **Period Scope:**
  - **All Periods:** Show this column for every generated period
  - **Current Period Only:** Only the latest period
  - **Previous Periods Only:** All periods except the latest
- **Title Template:** Optional; placeholders `{label}` and `{period}`. Default: `{label} ({period})` e.g. `Net Value (2026)`
- **Value Type:** Currency, Float, Int, or Percent
- **Hidden:** Compute the column but do not show it (useful for intermediate columns such as Depreciation)
- **Default Balance Type / Default is Formula / Default Formula:** Optional. Applied to every row that does not set that column on the line. Use this for a formula that is the same on all lines (e.g. `NET = GROSS - DEPR`).

**Example**

Value Columns:

| Column Code | Label        | Period Scope        | Hidden |
| ----------- | ------------ | ------------------- | ------ |
| `GROSS`     | Gross Value  | Current Period Only | No     |
| `DEPR`      | Depreciation | Current Period Only | Yes    |
| `NET`       | Net Value    | All Periods         | No     |

Filters: FY 2025 and FY 2026 -> report columns grouped by value column (newest period first), e.g. `Gross Value (2026)`, `Gross Value (2025)`, `Net Value (2026)`, `Net Value (2025)`.

###### 4. Per-column values (row settings, then column defaults)

Balance type and formula stay on the row by default and apply to every value column. Change a column in two places, in this order of precedence:

1. **Value Column Settings on the row** (expand a report line): different account filter, balance type, or formula for that column on that line only.
2. **Defaults on the Value Column:** e.g. mark `NET` as a formula default `GROSS - DEPR` once, instead of repeating it on 50 lines.
3. **Row fields:** used when the column has no setting and no column default.

Leave a column on **Use row default** to fall through.

**Example: Gross from the row filter, Depreciation per line, Net from a column default**

- Row `FA_MACHINES`: Account Filter `["account_number", "like", "24%"]` (this is Gross).
- On that same line, uncheck Use row default for `DEPR` and set `["account_number", "like", "281%"]`.
- On the `NET` Value Column, set Default is Formula and `GROSS - DEPR`. Every line inherits Net; you do not set NET on the row.

**Example: Formula that references other rows for one column**

On a Calculated Amount row `CM1`, customise column `DEPR` with `CM3 + CM2`. The engine orders rows so `CM2` and `CM3` are computed before `CM1`, even if they appear later in the template.

###### 5. Account Category

Same as ERPNext: a classification for accounts that enables standardised filtering across companies.

Examples:

- Cash and Cash Equivalents
- Trade Receivables
- Operating Expenses
- Revenue from Operations

##### How to Get Data for the Report

###### 1. Account Data - pull from Chart of Accounts

Gets actual balances from accounts. Filter by category or other Account fields.

Simple example - all cash balances:

- Filter: `["account_category", "=", "Cash and Cash Equivalents"]` (or use the filter editor)
- Balance type: Closing Balance

Advanced example - nested conditions:

```json
{
  "and": [
    ["root_type", "=", "Asset"],
    ["account_number", "like", "24%"]
  ]
}
```

Balance types:

- **Opening Balance:** Balance at the start of the period
- **Closing Balance:** Balance at the end of the period
- **Period Movement (Debits − Credits):** Change during the period (debits minus credits)
- **Debits:** Sum of debit postings in the period (not netted with credits)
- **Credits:** Sum of credit postings in the period (not netted with debits)

From the template form, use **View Account Coverage** to see which accounts a row (or selected rows) include or miss.

###### 2. Calculated Amount

Add, subtract, or compute ratios using other rows’ Reference Codes.

Simple examples:

- Total Assets: `CURRENT_ASSETS + NON_CURRENT_ASSETS`
- Gross Profit: `REVENUE - COST_OF_GOODS_SOLD`
- Profit Margin: `(NET_PROFIT / REVENUE) * 100`

Safe division:

```text
(GROSS_PROFIT / REVENUE) * 100 if REVENUE != 0 else 0
```

With Value Columns, a formula on a Calculated Amount row is evaluated **per value column**. Cross-row references use the same column of the other row (e.g. under `NET`, `FA` means that row’s Net series). Same-row value columns can also appear in a formula when a column setting or Value Column default sets **Evaluate as Formula** (e.g. `GROSS - DEPR`).

###### 3. Visual Elements

- **Blank Line:** Space between sections; Display Name can still be shown (e.g. bold "ASSETS")
- **Column Break:** Side-by-side / horizontal layout; Display Name is the segment header
- **Section Break:** Separates major sections when used with column breaks

##### How to Run a Report

1. Create or open a **Financial Report Template Enhanced**
2. Define Value Columns (optional, including column defaults), Rows, and per-column settings on lines that need them
3. Open **Financial Statement Enhanced**
4. Set Company, fiscal years or date range, periodicity
5. Select the template under **Report Template** and run

From the template form, **View Report** opens Financial Statement Enhanced with the template pre-selected.

Standard ERPNext reports (Balance Sheet, Profit and Loss Statement, Cash Flow, Custom Financial Statement) continue to use ERPNext’s original Financial Report Template - not Enhanced templates.

##### Making Reports Look Professional

- **Bold Text / Italic Text:** Headings and subtotals
- **Colour:** Highlight exceptions or key figures
- **Indentation:** Visual hierarchy
- **Hide If Zero:** Omit empty lines
- **Reverse Sign:** Show expenses as positive where helpful
- **Balance Filter:** Place debit and credit balances on opposite sides of a statement without hidden helper rows:
  - **Debit Accounts / Credit Accounts:** Keep only accounts whose GL balance has that sign in each period (clients débiteurs vs clients créditeurs)
  - **Net Debit / Net Credit:** Keep the whole line when the overall balance (last visible value column, typically Net) has that sign; otherwise zero
  - Sign is always debit minus credit, before Reverse Sign. Pair the two sides and enable Hide If Zero.
- **Include in Charts:** Drive the report chart (first visible value column when Value Columns are defined)
- **Hidden value columns:** Keep intermediate amounts (e.g. Depreciation) out of the printed columns while still using them in formulas

##### Built-in Validations

The system checks templates to prevent silent mistakes:

**Reference Codes**

- Must be unique
- Must start with a letter; letters, numbers, and underscores only  
  ✅ `REV100`, `ASSET1`  
  ❌ `100REV`, `ASSET-1`

**Value Columns and column settings**

- Column Codes must be unique
- A Column Code must not reuse a Line Reference (formulas share one namespace; the row’s own column would shadow the other row)
- **Evaluate as Formula** / **Default is Formula** requires a formula
- Column settings and legacy overrides must point at an existing Column Code
- Value columns of the same row must not form a dependency loop (e.g. `NET = GROSS - DEPR` and `GROSS = NET + DEPR`)

**Calculations**

- Referenced row codes must exist
- Circular references between rows are rejected
- Parentheses must be balanced

**Account Filters**

- Filter syntax is validated
- Account categories used in filters should exist

##### How to Assign Categories to Accounts

- **One by one:** Accounts -> set Account Category
- **Bulk:** Data Import Tool

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app csf_ohada
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/csf_ohada
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### License

agpl-3.0
