# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt


from __future__ import annotations

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


def build_override_map(template) -> dict[tuple[str, str], Any]:
	"""Map (row_reference_code, column_code) -> override row."""
	overrides = {}
	for override in getattr(template, "column_overrides", None) or []:
		row_ref = (override.row_reference_code or "").strip()
		col_code = (override.column_code or "").strip()
		if row_ref and col_code:
			overrides[(row_ref, col_code)] = override
	return overrides


def get_override(row, column_code: str, override_map: dict[tuple[str, str], Any]):
	"""Return the override configured for a row x value column, if any."""
	if column_code == DEFAULT_MEASURE:
		return None

	return override_map.get(((getattr(row, "reference_code", "") or "").strip(), column_code))


def resolve_row_settings(row, column_code: str, override_map: dict[tuple[str, str], Any]) -> dict[str, Any]:
	"""Resolve balance_type and calculation_formula for a row x value column."""
	balance_type = getattr(row, "balance_type", None)
	calculation_formula = getattr(row, "calculation_formula", None)

	override = get_override(row, column_code, override_map)
	if override:
		if override.balance_type:
			balance_type = override.balance_type
		if override.calculation_formula:
			calculation_formula = override.calculation_formula

	return {
		"balance_type": balance_type,
		"calculation_formula": calculation_formula,
	}


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


def _build_plan_entries(row, measures: list[MeasureColumn], override_map: dict[tuple[str, str], Any]):
	data_source = getattr(row, "data_source", "") or ""
	entries = []

	for measure in measures:
		settings = resolve_row_settings(row, measure.column_code, override_map)
		override = get_override(row, measure.column_code, override_map)

		if data_source == "Calculated Amount":
			mode = MODE_FORMULA
		elif data_source == "Account Data" and override and override.is_formula:
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


def build_row_column_plan(row, measures: list[MeasureColumn], override_map: dict[tuple[str, str], Any]):
	"""Plan every value column of a row, ordered so formulas run after what they reference."""
	ordered, _cyclic = resolve_column_dependencies(_build_plan_entries(row, measures, override_map))
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
	row, measures: list[MeasureColumn], override_map: dict[tuple[str, str], Any]
) -> list[str]:
	"""Column codes that reference each other in a cycle for the given row."""
	_ordered, cyclic = resolve_column_dependencies(_build_plan_entries(row, measures, override_map))
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
	period_count = len(period_list)
	result = []
	for period_index, period in enumerate(period_list):
		for measure in measures:
			if measure.hidden:
				continue
			if not period_in_scope(period_index, period_count, measure.period_scope):
				continue
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
