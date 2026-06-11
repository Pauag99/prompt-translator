"""Ejecuta el benchmark complejo contra Prompt Translator."""

import argparse
import json
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "tests"))

from complex_cases import COMPLEX_CASES
from translator import PromptTranslator, configure_console_encoding


CONCEPT_ALIASES = {
    "contencion": ("contencion", "contener", "mitigar", "minimizar el dano"),
    "investigacion": ("investigacion", "investigar", "identificar", "evaluar"),
    "comunicacion": ("comunicacion", "comunicar", "notificar"),
    "separacion": ("separacion", "aislamiento", "aislar"),
    "escalabilidad": ("escalabilidad", "escalable", "crecimiento"),
    "priorizacion": ("priorizacion", "priorizar"),
    "monitorizacion": ("monitorizacion", "monitoreo", "supervision"),
    "validacion": ("validacion", "validar", "verificar"),
    "preguntas": ("preguntas", "preguntar"),
    "caracterizacion": ("caracterizacion", "comportamiento", "comportamientos clave"),
    "riesgo": ("riesgo", "areas criticas", "puntos criticos"),
    "incremental": ("incremental", "gradual", "conjunto inicial", "plan de implementacion"),
    "descubrimiento": ("descubrimiento", "identificar", "documentar", "investigar"),
    "transicion": ("transicion", "migracion", "cambio de proveedor"),
    "riesgos": ("riesgos", "conflictos", "desafios", "impactos"),
    "hipotesis": ("hipotesis", "posible causa", "posibles causas"),
    "evidencia": ("evidencia", "registros", "errores", "datos"),
    "alternativas": ("alternativas", "causas externas", "posibles causas"),
}


def normalize(text):
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def concept_is_present(concept, normalized_output):
    aliases = CONCEPT_ALIASES.get(normalize(concept), (concept,))
    return any(normalize(alias) in normalized_output for alias in aliases)


def forbidden_is_asserted(assumption, normalized_output):
    assumption = normalize(assumption)
    start = normalized_output.find(assumption)
    while start >= 0:
        prefix = normalized_output[max(0, start - 35):start]
        negated = any(marker in prefix for marker in (" no ", " sin ", " evitar ", " nunca "))
        if not negated:
            return True
        start = normalized_output.find(assumption, start + len(assumption))
    return False


def evaluate_case(case, result, elapsed):
    optimized = result.get("optimized", "")
    normalized_output = normalize(optimized)
    required_hits = [
        concept for concept in case["required_concepts"]
        if concept_is_present(concept, normalized_output)
    ]
    forbidden_hits = [
        assumption for assumption in case["forbidden_assumptions"]
        if forbidden_is_asserted(assumption, normalized_output)
    ]
    quality = result.get("quality", {})
    concept_coverage = (
        len(required_hits) / len(case["required_concepts"])
        if case["required_concepts"] else 1
    )
    passed = (
        result.get("status") == "success"
        and quality.get("passed", False)
        and concept_coverage >= 0.5
        and not forbidden_hits
    )
    return {
        "id": case["id"],
        "category": case["category"],
        "difficulty": case["difficulty"],
        "request": case["request"],
        "status": result.get("status"),
        "passed": passed,
        "quality_score": quality.get("score", 0),
        "quality_warnings": quality.get("warnings", []),
        "required_hits": required_hits,
        "required_total": len(case["required_concepts"]),
        "concept_coverage": round(concept_coverage, 3),
        "forbidden_hits": forbidden_hits,
        "elapsed_seconds": round(elapsed, 2),
        "optimized": optimized,
    }


def build_summary(results):
    categories = defaultdict(lambda: {"total": 0, "passed": 0, "scores": []})
    for result in results:
        category = categories[result["category"]]
        category["total"] += 1
        category["passed"] += int(result["passed"])
        category["scores"].append(result["quality_score"])

    category_summary = {}
    for name, values in sorted(categories.items()):
        category_summary[name] = {
            "total": values["total"],
            "passed": values["passed"],
            "pass_rate": round(values["passed"] / values["total"] * 100, 1),
            "average_quality": round(sum(values["scores"]) / len(values["scores"]), 1),
        }

    total = len(results)
    passed = sum(result["passed"] for result in results)
    return {
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total * 100, 1) if total else 0,
        "average_quality": round(
            sum(result["quality_score"] for result in results) / total, 1
        ) if total else 0,
        "average_concept_coverage": round(
            sum(result["concept_coverage"] for result in results) / total * 100, 1
        ) if total else 0,
        "forbidden_hits": sum(len(result["forbidden_hits"]) for result in results),
        "total_seconds": round(sum(result["elapsed_seconds"] for result in results), 2),
        "categories": category_summary,
    }


def select_cases(category=None, limit=None):
    cases = COMPLEX_CASES
    if category:
        cases = [case for case in cases if normalize(case["category"]) == normalize(category)]
    return cases[:limit] if limit else cases


def main():
    parser = argparse.ArgumentParser(description="Benchmark complejo de Prompt Translator")
    parser.add_argument("--category", help="Ejecutar solo una categoria")
    parser.add_argument("--limit", type=int, help="Limitar numero de casos")
    parser.add_argument("--output", help="Guardar informe JSON")
    args = parser.parse_args()

    configure_console_encoding()
    cases = select_cases(args.category, args.limit)
    if not cases:
        print("No hay casos que coincidan con los filtros.")
        return 1

    translator = PromptTranslator()
    results = []
    print(f"Ejecutando {len(cases)} casos complejos...\n")
    for index, case in enumerate(cases, 1):
        start = time.time()
        result = translator.translate(case["request"])
        evaluated = evaluate_case(case, result, time.time() - start)
        results.append(evaluated)
        status = "PASS" if evaluated["passed"] else "REVIEW"
        print(
            f"[{index:02}/{len(cases):02}] {case['id']} {status} "
            f"quality={evaluated['quality_score']} "
            f"concepts={len(evaluated['required_hits'])}/{evaluated['required_total']} "
            f"forbidden={len(evaluated['forbidden_hits'])} "
            f"time={evaluated['elapsed_seconds']:.2f}s"
        )

    summary = build_summary(results)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "model": translator.model,
        "summary": summary,
        "results": results,
    }

    print("\nRESUMEN")
    print(f"Casos aprobados: {summary['passed']}/{summary['total']} ({summary['pass_rate']}%)")
    print(f"Calidad media: {summary['average_quality']}/100")
    print(f"Cobertura media de conceptos: {summary['average_concept_coverage']}%")
    print(f"Supuestos prohibidos detectados: {summary['forbidden_hits']}")
    print(f"Tiempo total: {summary['total_seconds']}s")

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Informe guardado en: {output}")

    return 0 if summary["passed"] == summary["total"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
