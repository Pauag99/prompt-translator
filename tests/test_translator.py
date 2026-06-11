"""Tests unitarios para Prompt Translator."""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from translator import PromptTranslator


GOOD_PROMPT = """- Rol: Desarrollador senior
- Objetivo: Crear una solución clara para gestionar tareas.
- Contexto: La solución será utilizada por un equipo pequeño.
- Requisitos funcionales o tareas:
  - Permitir crear, editar y completar tareas.
  - Mantener la intención de la solicitud original.
- Restricciones:
  - No inventar tecnologías ni métricas no solicitadas.
- Formato de salida esperado: Entrega una propuesta estructurada con pasos.
- Criterios de aceptación: La propuesta debe ser clara, viable y verificable.
- Preguntas pendientes: Indica las decisiones importantes que falten."""


def ollama_response(text=GOOD_PROMPT, status_code=200):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {"response": text}
    return response


class TestPromptTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = PromptTranslator()

    @patch("translator.requests.post")
    def test_success_response_has_quality_evaluation(self, mock_post):
        mock_post.return_value = ollama_response()

        response = self.translator.translate("Crea una aplicación para gestionar tareas")

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["model"], "mistral")
        self.assertIn("optimized", response)
        self.assertIn("tips", response)
        self.assertIn("quality", response)
        self.assertTrue(response["quality"]["passed"])
        self.assertGreaterEqual(response["quality"]["score"], 70)

    @patch("translator.requests.post")
    def test_request_uses_configured_ollama_options(self, mock_post):
        mock_post.return_value = ollama_response()

        self.translator.translate("Crea una aplicación")

        payload = mock_post.call_args.kwargs["json"]
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["model"], "mistral")
        self.assertEqual(payload["options"]["temperature"], 0.4)
        self.assertEqual(payload["options"]["num_predict"], 800)

    def test_empty_request_is_rejected_without_calling_ollama(self):
        with patch("translator.requests.post") as mock_post:
            response = self.translator.translate("   ")

        self.assertEqual(response["status"], "error")
        self.assertIn("vacía", response["error"])
        mock_post.assert_not_called()

    @patch("translator.requests.post")
    def test_empty_ollama_response_is_rejected(self, mock_post):
        mock_post.return_value = ollama_response("   ")

        response = self.translator.translate("Haz un resumen")

        self.assertEqual(response["status"], "error")
        self.assertIn("respuesta vacía", response["error"])

    def test_quality_detects_concrete_requirement_not_requested(self):
        invented = GOOD_PROMPT + "\n- Debe alcanzar una precisión superior al 70%."

        quality = self.translator.evaluate_quality("Crea un modelo predictivo", invented)

        self.assertFalse(quality["passed"])
        self.assertTrue(quality["warnings"])

    def test_quality_detects_unrequested_file_format(self):
        invented = GOOD_PROMPT + "\n- Formato de salida esperado: Un archivo CSV."

        quality = self.translator.evaluate_quality("Analiza los datos", invented)

        self.assertFalse(quality["passed"])
        self.assertTrue(quality["warnings"])

    def test_quality_detects_unrequested_technology(self):
        invented = GOOD_PROMPT + "\n- La autenticación debe usar JWT."

        quality = self.translator.evaluate_quality("Crea una API REST", invented)

        self.assertFalse(quality["passed"])
        self.assertTrue(quality["warnings"])

    def test_quality_allows_json_as_rest_api_convention(self):
        prompt = GOOD_PROMPT + "\n- Formato de salida esperado: Respuestas JSON."

        quality = self.translator.evaluate_quality("Crea una API REST", prompt)

        self.assertTrue(quality["passed"])
        self.assertFalse(quality["warnings"])

    @patch("translator.requests.post")
    def test_translate_retries_once_when_quality_warning_is_detected(self, mock_post):
        mock_post.side_effect = [
            ollama_response("Crea un modelo predictivo sencillo."),
            ollama_response(GOOD_PROMPT),
        ]

        response = self.translator.translate("Crea un modelo predictivo")

        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(response["optimized"], GOOD_PROMPT)
        self.assertTrue(response["quality"]["passed"])

    def test_sanitize_replaces_unrequested_percentage_and_format(self):
        prompt = (
            "Entrega un archivo .csv y un archivo de texto plano "
            "con precisión superior al 70%."
        )

        sanitized = self.translator.sanitize_unrequested_specifics(
            "Crea un modelo predictivo", prompt
        )

        self.assertNotIn("70%", sanitized)
        self.assertNotIn(".csv", sanitized.lower())
        self.assertNotIn("archivo de texto plano", sanitized.lower())
        self.assertIn("[umbral acordado]", sanitized)
        self.assertIn("[formato de salida preferido]", sanitized)

    def test_sanitize_does_not_modify_words_containing_format_name(self):
        prompt = "Generar un resultado y no ignorar ninguna condición."

        sanitized = self.translator.sanitize_unrequested_specifics(
            "Generar un resultado", prompt
        )

        self.assertEqual(sanitized, prompt)

    def test_quality_rejects_short_unstructured_prompt(self):
        quality = self.translator.evaluate_quality("Crea una API", "Crea una API REST sencilla.")

        self.assertFalse(quality["passed"])
        self.assertLess(quality["score"], 70)

    def test_error_handling_connection(self):
        translator_wrong = PromptTranslator(base_url="http://localhost:99999")
        response = translator_wrong.translate("Test")

        self.assertEqual(response["status"], "error")
        self.assertIn("error", response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
