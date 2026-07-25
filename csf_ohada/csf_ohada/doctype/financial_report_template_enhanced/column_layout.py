# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt


from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_MEASURE = "_default"


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


def resolve_row_settings(row, column_code: str, override_map: dict[tuple[str, str], Any]) -> dict[str, Any]:
	"""Resolve balance_type and calculation_formula for a row x measure column."""
	balance_type = getattr(row, "balance_type", None)
	calculation_formula = getattr(row, "calculation_formula", None)

	if column_code != DEFAULT_MEASURE:
		override = override_map.get(((row.reference_code or "").strip(), column_code))
		if override:
			if override.balance_type:
				balance_type = override.balance_type
			if override.calculation_formula:
				calculation_formula = override.calculation_formula

	return {
		"balance_type": balance_type,
		"calculation_formula": calculation_formula,
	}


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
