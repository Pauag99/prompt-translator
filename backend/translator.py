"""
Prompt Translator - Convierte lenguaje humano en prompts optimizados
Configurado para Mistral 7B
"""
import sys

import requests


def configure_console_encoding():
    """Evita errores Unicode en consolas Windows con cp1252."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

class PromptTranslator:
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Inicializa el Prompt Translator
        
        Args:
            model: Modelo a usar (default: mistral - Optimizado para 16GB RAM)
            base_url: URL del servidor Ollama (default: localhost:11434)
        """
        self.model = model
        self.base_url = base_url
        
        # Configuración optimizada para Mistral 7B en portátil 16GB
        self.config = {
            "num_predict": 800,      # Limite de tokens de salida
            "temperature": 0.4,      # Respuestas mas consistentes
            "top_p": 0.9,            # Diversidad controlada
            "repeat_penalty": 1.1,   # Evita repeticiones
            "timeout": 60            # Timeout en segundos
        }
        
        self.system_prompt = """Eres un experto senior en ingenieria de prompts.
Transformas solicitudes vagas o incompletas en prompts finales, claros y accionables.

Reglas obligatorias:
1. Responde siempre en espanol.
2. No expliques que hiciste; devuelve solo el prompt optimizado.
3. No inventes datos concretos como nombres de empresa, URLs o credenciales.
4. Si faltan datos, incluye placeholders claros entre corchetes, por ejemplo [framework preferido].
5. El prompt final debe ser mas especifico, estructurado y util que la solicitud original.
6. Incluye criterios de calidad y restricciones cuando ayuden al resultado.
7. Pide al modelo una salida concreta, no una respuesta generica.

Formato recomendado del prompt final:
- Rol
- Objetivo
- Contexto
- Requisitos funcionales o tareas
- Restricciones
- Formato de salida esperado
- Criterios de aceptacion
- Preguntas pendientes, solo si son necesarias"""

    def translate(self, human_request: str) -> dict:
        """
        Traduce una solicitud en lenguaje natural a un prompt optimizado
        
        Args:
            human_request: La solicitud en lenguaje natural

        Returns:
            Diccionario con estado, solicitud original, prompt optimizado,
            modelo usado y tips de mejora.
        """
        try:
            prompt = f"""Convierte la siguiente solicitud en un prompt final listo para copiar y pegar en un modelo de IA.

El prompt final debe:
- Mantener la intencion original.
- Anadir detalles utiles sin cambiar el objetivo.
- Usar secciones claras.
- Incluir entregables esperados.
- Incluir criterios para evaluar si la respuesta es buena.
- Incluir preguntas pendientes solo cuando falten decisiones importantes.

SOLICITUD: {human_request}

PROMPT OPTIMIZADO:"""
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self.system_prompt + "\n\n" + prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config["temperature"],
                        "num_predict": self.config["num_predict"],
                        "top_p": self.config["top_p"],
                        "repeat_penalty": self.config["repeat_penalty"],
                    },
                },
                timeout=self.config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                optimized_prompt = result.get("response", "").strip()
                
                return {
                    "status": "success",
                    "original": human_request,
                    "optimized": optimized_prompt,
                    "model": self.model,
                    "tips": self._generate_tips(human_request, optimized_prompt)
                }
            else:
                return {
                    "status": "error",
                    "error": f"Error en la API: {response.status_code}",
                    "original": human_request
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "error": "No se puede conectar con Ollama. ¿Está ejecutándose?",
                "original": human_request
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "original": human_request
            }
    
    def _generate_tips(self, original: str, optimized: str) -> list:
        """Genera consejos sobre cómo mejorar el prompt"""
        tips = []
        
        if "role:" in optimized.lower() or "como" in optimized.lower() or "actúa como" in optimized.lower():
            tips.append("✓ Define claramente el rol del modelo")
        
        if "ejemplo" in optimized.lower() or "ej:" in optimized.lower() or "input" in optimized.lower():
            tips.append("✓ Incluye ejemplos de entrada/salida")
        
        if "formato" in optimized.lower() or "output" in optimized.lower() or "json" in optimized.lower():
            tips.append("✓ Especifica formato de salida")
        
        if "paso" in optimized.lower() or "pasos" in optimized.lower() or "siguiente" in optimized.lower():
            tips.append("✓ Define pasos o proceso claro")
        
        if "restricción" in optimized.lower() or "límit" in optimized.lower() or "no incluya" in optimized.lower():
            tips.append("✓ Incluye restricciones y limitaciones")
        
        if not tips:
            tips.append("✓ Prompt optimizado y estructurado")
        
        return tips


if __name__ == "__main__":
    configure_console_encoding()

    # Prueba básica
    translator = PromptTranslator()
    
    test_requests = [
        "Necesito un script que haga web scraping",
        "Quiero que me ayudes a escribir un resumen de un texto",
        "Cómo puedo optimizar una consulta SQL lenta"
    ]
    
    print("=" * 60)
    print("PRUEBAS DEL TRADUCTOR DE PROMPTS")
    print("=" * 60)
    
    for request in test_requests:
        print(f"\n📝 SOLICITUD ORIGINAL:\n{request}\n")
        result = translator.translate(request)
        
        if result["status"] == "success":
            print(f"✨ PROMPT OPTIMIZADO:\n{result['optimized']}\n")
            print(f"💡 TIPS:")
            for tip in result["tips"]:
                print(f"  {tip}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print("-" * 60)
