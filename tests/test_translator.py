"""
Tests para el Prompt Translator
"""
import unittest
import sys
import os

# Agregar el backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from translator import PromptTranslator


class TestPromptTranslator(unittest.TestCase):
    
    def setUp(self):
        self.translator = PromptTranslator()
    
    def test_translation_response_structure(self):
        """Verifica que la respuesta tenga la estructura correcta"""
        response = self.translator.translate("Haz un resumen")
        
        self.assertIn("status", response)
        self.assertIn("original", response)
        
        if response["status"] == "success":
            self.assertIn("optimized", response)
            self.assertIn("model", response)
            self.assertIn("tips", response)
    
    def test_optimized_prompt_is_different(self):
        """Verifica que el prompt optimizado sea diferente al original"""
        original = "Dame un script"
        response = self.translator.translate(original)
        
        if response["status"] == "success":
            self.assertNotEqual(original, response["optimized"])
    
    def test_error_handling_connection(self):
        """Verifica el manejo de errores de conexión"""
        translator_wrong = PromptTranslator(base_url="http://localhost:99999")
        response = translator_wrong.translate("Test")
        
        self.assertEqual(response["status"], "error")
        self.assertIn("error", response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
