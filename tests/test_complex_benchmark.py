"""Tests de integridad para el benchmark complejo."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from benchmark_complex import (
    build_summary,
    concept_is_present,
    evaluate_case,
    forbidden_is_asserted,
    select_cases,
)
from complex_cases import COMPLEX_CASES


def test_complex_bank_has_at_least_40_cases():
    assert len(COMPLEX_CASES) >= 40


def test_complex_case_ids_are_unique():
    ids = [case["id"] for case in COMPLEX_CASES]
    assert len(ids) == len(set(ids))


def test_complex_cases_have_required_schema():
    required_fields = {
        "id", "category", "difficulty", "request",
        "required_concepts", "forbidden_assumptions", "tags",
    }
    for case in COMPLEX_CASES:
        assert set(case) == required_fields
        assert case["request"].strip()
        assert len(case["required_concepts"]) >= 3
        assert case["difficulty"] in {"media", "alta", "extrema"}


def test_complex_bank_has_broad_category_coverage():
    categories = {case["category"] for case in COMPLEX_CASES}
    assert len(categories) >= 10


def test_select_cases_filters_category_and_limit():
    selected = select_cases(category="Seguridad", limit=2)

    assert len(selected) == 2
    assert all(case["category"] == "Seguridad" for case in selected)


def test_concept_matching_accepts_basic_semantic_aliases():
    output = "El plan debe comunicar, identificar el origen y mitigar el impacto."

    assert concept_is_present("comunicacion", output)
    assert concept_is_present("investigacion", output)
    assert concept_is_present("contencion", output)


def test_forbidden_matching_ignores_negated_assumption():
    assert not forbidden_is_asserted(
        "reescritura completa",
        "Propone mejoras sin una reescritura completa.",
    )
    assert forbidden_is_asserted(
        "reescritura completa",
        "La solucion requiere una reescritura completa.",
    )


def test_evaluate_case_fails_when_forbidden_assumption_appears():
    case = COMPLEX_CASES[0]
    result = {
        "status": "success",
        "optimized": (
            "Rol Objetivo Contexto Requisitos Restricciones Formato Criterios "
            "multi-tenant separacion auditoria escalabilidad AWS"
        ),
        "quality": {"score": 100, "passed": True, "warnings": []},
    }

    evaluated = evaluate_case(case, result, elapsed=1.5)

    assert not evaluated["passed"]
    assert evaluated["forbidden_hits"] == ["aws"]


def test_build_summary_aggregates_results():
    results = [
        {
            "category": "A", "passed": True, "quality_score": 100,
            "concept_coverage": 1.0, "forbidden_hits": [], "elapsed_seconds": 1,
        },
        {
            "category": "A", "passed": False, "quality_score": 80,
            "concept_coverage": 0.5, "forbidden_hits": ["x"], "elapsed_seconds": 2,
        },
    ]

    summary = build_summary(results)

    assert summary["passed"] == 1
    assert summary["pass_rate"] == 50.0
    assert summary["average_quality"] == 90.0
    assert summary["forbidden_hits"] == 1
