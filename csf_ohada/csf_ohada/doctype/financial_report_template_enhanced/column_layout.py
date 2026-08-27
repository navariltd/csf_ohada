# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt


from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from csf_ohada.csf_ohada.doctype.financial_report_template_enhanced.financial_report_validation import (
	extract_reference_codes_from_formula,
)

DEFAULT_MEASURE = "_default"

MODE_ACCOUNT = "account"
MODE_FORMULA = "formula"


@dataclass(frozen=True)
class MeasureColumn:
	column_code: str
	label: str
	period_scope: str = "All Periods"
	title_template: str | None = None
	fieldtype: str | None = "Currency"
	hidden: bool = False

	@property
	def is_default(self) -> bool:
		return self.column_code == DEFAULT_MEASURE


def get_measure_columns(template) -> list[MeasureColumn]:
	"""Return configured measure columns, or a single default measure when none are set."""
	columns = getattr(template, "columns", None) or []
	if not columns:
		return [
			MeasureColumn(
				column_code=DEFAULT_MEASURE,
				label="",
				period_scope="All Periods",
				title_template="{period}",
				fieldtype="Currency",
				hidden=False,
			)
		]

	return [
		MeasureColumn(
			column_code=(col.column_code or "").strip(),
			label=col.label or col.column_code,
			period_scope=col.period_scope or "All Periods",
			title_template=col.title_template,
			fieldtype=col.fieldtype or "Currency",
			hidden=bool(col.hidden),
		)
		for col in columns
		if (col.column_code or "").strip()
	]


def build_column_defaults(template) -> dict[str, dict[str, Any]]:
	"""Map column_code -> default balance_type / is_formula / calculation_formula."""
	defaults = {}
	for col in getattr(template, "columns", None) or []:
		code = (col.column_code or "").strip()
		if not code:
			continue
		defaults[code] = {
			"balance_type": (getattr(col, "default_balance_type", None) or "").strip() or None,
			"is_formula": bool(getattr(col, "default_is_formula", 0)),
			"calculation_formula": (getattr(col, "default_calculation_formula", None) or "").strip() or None,
		}
	return defaults


def parse_row_column_settings(row) -> dict[str, dict[str, Any]]:
	"""Parse a row's column_settings JSON into {column_code: setting dict}."""
	data, error = load_row_column_settings(row)
	if error:
		return {}
	return data


def load_row_column_settings(row) -> tuple[dict[str, dict[str, Any]], str | None]:
	"""Return (settings, error_message) for a row's column_settings JSON."""
	raw = getattr(row, "column_settings", None)
	if not raw:
		return {}, None
	if isinstance(raw, dict):
		data = raw
	elif isinstance(raw, str):
		try:
			data = json.loads(raw)
		except json.JSONDecodeError as e:
			return {}, str(e)
	else:
		return {}, "Column settings must be a JSON object"

	if data is None or data == "":
		return {}, None
	if not isinstance(data, dict):
		return {}, "Column settings must be a JSON object"

	parsed = {}
	for key, value in data.items():
		code = (key or "").strip() if isinstance(key, str) else ""
		if not code:
			continue
		if not isinstance(value, dict):
			return {}, f"Column setting for {code} must be an object"
		parsed[code] = {
			"balance_type": (value.get("balance_type") or "").strip() or None,
			"is_formula": bool(value.get("is_formula")),
			"calculation_formula": (value.get("calculation_formula") or "").strip() or None,
		}
	return parsed, None


def get_template_column_codes(template) -> set[str]:
	"""Return the set of configured Value Column codes on a template."""
	return {
		(col.column_code or "").strip()
		for col in getattr(template, "columns", None) or []
		if (col.column_code or "").strip()
	}


def set_row_column_settings(row, settings: dict[str, dict[str, Any]] | None) -> None:
	"""Persist pruned column_settings on a report row."""
	if not settings:
		row.column_settings = None
		return
	row.column_settings = json.dumps(settings)


def prune_row_column_settings(row, valid_column_codes: set[str]) -> bool:
	"""Drop settings for removed value columns. Returns True if the row was modified."""
	settings = parse_row_column_settings(row)
	if not settings:
		return False

	if not valid_column_codes:
		row.column_settings = None
		return True

	pruned = {code: value for code, value in settings.items() if code in valid_column_codes}
	if len(pruned) == len(settings):
		return False

	set_row_column_settings(row, pruned or None)
	return True


def resolve_row_settings(
	row,
	column_code: str,
	column_defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
	"""Resolve balance_type, calculation_formula, and is_formula for a row x value column.

	Precedence: row.column_settings → Value Column defaults → row fields.
	"""
	data_source = getattr(row, "data_source", "") or ""
	balance_type = getattr(row, "balance_type", None)
	calculation_formula = getattr(row, "calculation_formula", None)
	is_formula = data_source == "Calculated Amount"

	def apply_layer(layer: dict | None):
		nonlocal balance_type, calculation_formula, is_formula
		if not layer:
			return
		if layer.get("balance_type"):
			balance_type = layer["balance_type"]
		if layer.get("calculation_formula"):
			calculation_formula = layer["calculation_formula"]
		if data_source == "Calculated Amount":
			is_formula = True
			return
		if layer.get("is_formula"):
			is_formula = True
		elif layer.get("calculation_formula"):
			is_formula = False

	apply_layer((column_defaults or {}).get(column_code))

	row_setting = parse_row_column_settings(row).get(column_code)
	if row_setting:
		apply_layer(row_setting)

	return {
		"balance_type": balance_type,
		"calculation_formula": calculation_formula,
		"is_formula": is_formula,
	}


@dataclass
class FormulaColumnSetting:
	"""A column of a row that is evaluated as a calculation formula."""

	column_code: str
	calculation_formula: str
	idx: int | None = None
	is_formula: bool = True


def iter_formula_column_settings(row, template) -> list[FormulaColumnSetting]:
	"""Formula columns that apply to this row after precedence (excluding the row's own default formula)."""
	data_source = getattr(row, "data_source", "") or ""
	if data_source not in {"Account Data", "Calculated Amount"}:
		return []

	measures = get_measure_columns(template)
	if not measures or measures[0].is_default:
		return []

	column_defaults = build_column_defaults(template)
	row_formula = (getattr(row, "calculation_formula", None) or "").strip() or None
	results = []

	for measure in measures:
		settings = resolve_row_settings(row, measure.column_code, column_defaults)
		formula = (settings.get("calculation_formula") or "").strip()
		if not formula:
			continue

		if data_source == "Calculated Amount":
			if formula == row_formula:
				continue
		elif not settings.get("is_formula"):
			continue

		results.append(
			FormulaColumnSetting(
				column_code=measure.column_code,
				calculation_formula=formula,
				idx=getattr(row, "idx", None),
			)
		)

	return results


@dataclass(frozen=True)
class ColumnPlanEntry:
	"""How a single row x value column should be computed."""

	column_code: str
	mode: str
	balance_type: str | None = None
	formula: str | None = None

	@property
	def is_formula(self) -> bool:
		return self.mode == MODE_FORMULA


def _build_plan_entries(
	row,
	measures: list[MeasureColumn],
	column_defaults: dict[str, Any] | None = None,
):
	data_source = getattr(row, "data_source", "") or ""
	entries = []

	for measure in measures:
		settings = resolve_row_settings(row, measure.column_code, column_defaults)

		if data_source == "Calculated Amount":
			mode = MODE_FORMULA
		elif data_source == "Account Data" and settings.get("is_formula"):
			mode = MODE_FORMULA
		else:
			mode = MODE_ACCOUNT

		entries.append(
			ColumnPlanEntry(
				column_code=measure.column_code,
				mode=mode,
				balance_type=settings["balance_type"],
				formula=settings["calculation_formula"],
			)
		)

	return entries


def build_row_column_plan(
	row,
	measures: list[MeasureColumn],
	column_defaults: dict[str, Any] | None = None,
):
	"""Plan every value column of a row, ordered so formulas run after what they reference."""
	ordered, _cyclic = resolve_column_dependencies(_build_plan_entries(row, measures, column_defaults))
	return ordered


def get_column_dependencies(entry: ColumnPlanEntry, column_codes: list[str]) -> list[str]:
	"""Column codes referenced by a formula column, excluding self-reference."""
	if not entry.is_formula or not entry.formula:
		return []

	candidates = [code for code in column_codes if code != entry.column_code]
	return extract_reference_codes_from_formula(entry.formula, candidates)


def resolve_column_dependencies(
	entries: list[ColumnPlanEntry],
) -> tuple[list[ColumnPlanEntry], list[str]]:
	"""Order entries so a formula column runs after the columns it references.

	Returns the ordered entries plus any column codes left in a dependency cycle.
	"""
	column_codes = [entry.column_code for entry in entries]
	entry_map = {entry.column_code: entry for entry in entries}

	dependencies = {
		entry.column_code: [dep for dep in get_column_dependencies(entry, column_codes) if dep in entry_map]
		for entry in entries
	}

	ordered = []
	resolved = set()

	# Kahn's algorithm, keeping the template's column order among ready entries
	while True:
		ready = [
			code
			for code in column_codes
			if code not in resolved and all(dep in resolved for dep in dependencies[code])
		]
		if not ready:
			break

		for code in ready:
			ordered.append(entry_map[code])
			resolved.add(code)

	cyclic = [code for code in column_codes if code not in resolved]
	ordered.extend(entry_map[code] for code in cyclic)

	return ordered, cyclic


def find_column_cycles(
	row,
	measures: list[MeasureColumn],
	column_defaults: dict[str, Any] | None = None,
) -> list[str]:
	"""Column codes that reference each other in a cycle for the given row."""
	_ordered, cyclic = resolve_column_dependencies(_build_plan_entries(row, measures, column_defaults))
	return cyclic


def period_in_scope(period_index: int, period_count: int, period_scope: str) -> bool:
	if period_scope == "Current Period Only":
		return period_index == period_count - 1 if period_count else period_index == 0
	if period_scope == "Previous Periods Only":
		return period_index < period_count - 1
	return True


def make_fieldname(column_code: str, period_key: str) -> str:
	if column_code == DEFAULT_MEASURE:
		return period_key
	safe_code = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in column_code).lower()
	return f"{safe_code}_{period_key}"


def make_column_label(measure: MeasureColumn, period_label: str) -> str:
	template = measure.title_template or ("{period}" if measure.is_default else "{label} ({period})")
	return template.format(label=measure.label or "", period=period_label)


def iter_visible_value_columns(measures: list[MeasureColumn], period_list: list[dict]) -> list[dict]:
	"""Yield visible report columns grouped by value column, then by period (newest first).

	Example with GROSS and NET across FY2025 and FY2026:
	GROSS (2026), GROSS (2025), NET (2026), NET (2025)
	"""
	period_count = len(period_list)
	period_indices = list(reversed(range(period_count)))
	result = []

	for measure in measures:
		if measure.hidden:
			continue
		for period_index in period_indices:
			if not period_in_scope(period_index, period_count, measure.period_scope):
				continue
			period = period_list[period_index]
			result.append(
				{
					"measure": measure,
					"period": period,
					"period_index": period_index,
					"fieldname": make_fieldname(measure.column_code, period["key"]),
					"label": make_column_label(measure, period.get("label") or period["key"]),
				}
			)
	return result
