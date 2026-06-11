"""
Prompt Translator - Convierte lenguaje humano en prompts optimizados
Configurado para Mistral 7B
"""
import sys
import re

import requests


def configure_console_encoding():
    """Evita errores Unicode en consolas Windows con cp1252."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

class PromptTranslator:
    QUALITY_SECTIONS = {
        "role": ("rol", "actua como", "actúa como"),
        "objective": ("objetivo",),
        "context": ("contexto",),
        "requirements": ("requisitos", "tareas"),
        "constraints": ("restricciones", "limitaciones"),
        "output_format": ("formato de salida", "entregables"),
        "acceptance_criteria": ("criterios de aceptacion", "criterios de aceptación"),
    }

    INVENTION_PATTERNS = (
        (
            r"\b(?:superior|inferior|al menos|como minimo|como mínimo)\s+al?\s*\d+\s*%",
            "Contiene un umbral numérico no solicitado.",
        ),
        (
            r"\b(?:un\s+)?archivo\s+(?:csv|json|pdf|zip|rar|7z|txt|xlsx|de texto plano)\b",
            "Contiene un formato de archivo no solicitado.",
        ),
        (
            r"\bdebe usar\s+(?:react|angular|vue|django|flask|fastapi|spring)\b",
            "Contiene una tecnología obligatoria no solicitada.",
        ),
    )

    UNREQUESTED_SPECIFICS = (
        (
            r"\b(?:csv|json|pdf|zip|rar|7z|txt|xlsx)\b",
            "Contiene un formato concreto no solicitado.",
        ),
        (
            r"\b(?:jwt|oauth|react|angular|vue|django|flask|fastapi|spring)\b",
            "Contiene una tecnología concreta no solicitada.",
        ),
    )

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
3. No inventes datos concretos como nombres, URLs, credenciales, porcentajes,
   tecnologias obligatorias, formatos de archivo o umbrales de rendimiento.
4. Si faltan datos, incluye placeholders claros entre corchetes, por ejemplo [framework preferido].
5. El prompt final debe ser mas especifico, estructurado y util que la solicitud original.
6. Incluye criterios de calidad y restricciones cuando ayuden al resultado.
7. Pide al modelo una salida concreta, no una respuesta generica.
8. No conviertas preferencias opcionales en requisitos obligatorios.
9. No exijas entregables binarios como ZIP, PDF o archivos adjuntos salvo que
   la solicitud original los pida.
10. Si necesitas una metrica o tecnologia no indicada, formula una pregunta
    pendiente o usa un placeholder en vez de inventarla.
11. Los criterios de aceptacion no deben contener cifras, porcentajes o formatos
    concretos que no aparezcan en la solicitud original. Usa placeholders como
    [metrica objetivo], [umbral acordado] o [formato de salida preferido].

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
        human_request = human_request.strip() if isinstance(human_request, str) else ""
        if not human_request:
            return {
                "status": "error",
                "error": "La solicitud no puede estar vacía.",
                "original": human_request,
            }

        try:
            prompt = f"""Convierte la siguiente solicitud en un prompt final listo para copiar y pegar en un modelo de IA.

El prompt final debe:
- Mantener la intencion original.
- Anadir detalles utiles sin cambiar el objetivo.
- Usar secciones claras.
- Incluir entregables esperados.
- Incluir criterios para evaluar si la respuesta es buena.
- Incluir preguntas pendientes solo cuando falten decisiones importantes.
- No inventar porcentajes, umbrales, tecnologias ni formatos de archivo.
- Usar placeholders entre corchetes para cualquier decision no indicada.

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

                if not optimized_prompt:
                    return {
                        "status": "error",
                        "error": "Ollama devolvió una respuesta vacía.",
                        "original": human_request,
                    }

                optimized_prompt = self.sanitize_unrequested_specifics(
                    human_request, optimized_prompt
                )
                quality = self.evaluate_quality(human_request, optimized_prompt)

                for _ in range(2):
                    if not quality["warnings"]:
                        break

                    correction_prompt = f"""Corrige el siguiente prompt optimizado.

Solicitud original:
{human_request}

Prompt a corregir:
{optimized_prompt}

Problemas detectados:
{chr(10).join(f"- {warning}" for warning in quality["warnings"])}

Elimina cualquier cifra, umbral, tecnologia o formato no solicitado.
Sustituye decisiones desconocidas por placeholders entre corchetes.
Devuelve solo el prompt corregido con la misma estructura."""
                    corrected_response = requests.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": self.system_prompt + "\n\n" + correction_prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.2,
                                "num_predict": self.config["num_predict"],
                                "top_p": self.config["top_p"],
                                "repeat_penalty": self.config["repeat_penalty"],
                            },
                        },
                        timeout=self.config["timeout"],
                    )
                    if corrected_response.status_code != 200:
                        break

                    corrected_prompt = corrected_response.json().get("response", "").strip()
                    corrected_prompt = self.sanitize_unrequested_specifics(
                        human_request, corrected_prompt
                    )
                    corrected_quality = self.evaluate_quality(human_request, corrected_prompt)
                    if corrected_prompt and (
                        len(corrected_quality["warnings"]) < len(quality["warnings"])
                        or corrected_quality["score"] > quality["score"]
                    ):
                        optimized_prompt = corrected_prompt
                        quality = corrected_quality
                    else:
                        break
                
                return {
                    "status": "success",
                    "original": human_request,
                    "optimized": optimized_prompt,
                    "model": self.model,
                    "tips": self._generate_tips(human_request, optimized_prompt),
                    "quality": quality,
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

    def sanitize_unrequested_specifics(self, original: str, optimized: str) -> str:
        """Sustituye decisiones concretas no solicitadas por placeholders."""
        original_text = original.lower()
        sanitized = optimized

        if not re.search(r"\d+\s*%", original_text):
            sanitized = re.sub(
                r"\d+\s*%",
                "[umbral acordado]",
                sanitized,
                flags=re.IGNORECASE,
            )

        if "texto plano" not in original_text:
            sanitized = re.sub(
                r"(?:un\s+)?archivo\s+de texto plano",
                "[formato de salida preferido]",
                sanitized,
                flags=re.IGNORECASE,
            )

        formats = ("csv", "json", "pdf", "zip", "rar", "7z", "txt", "xlsx")
        for file_format in formats:
            allowed = file_format in original_text
            if file_format == "json" and "api" in original_text and "rest" in original_text:
                allowed = True
            if not allowed:
                sanitized = re.sub(
                    rf"(?<!\w)\.?{file_format}\b",
                    "[formato de salida preferido]",
                    sanitized,
                    flags=re.IGNORECASE,
                )

        technologies = ("jwt", "oauth", "react", "angular", "vue", "django", "flask", "fastapi", "spring")
        for technology in technologies:
            if technology not in original_text:
                sanitized = re.sub(
                    rf"\b{technology}\b",
                    "[tecnología preferida]",
                    sanitized,
                    flags=re.IGNORECASE,
                )

        return sanitized

    def evaluate_quality(self, original: str, optimized: str) -> dict:
        """Evalúa señales objetivas de calidad sin realizar otra llamada al modelo."""
        text = optimized.lower()
        original_text = original.lower()
        sections = {
            name: any(marker in text for marker in markers)
            for name, markers in self.QUALITY_SECTIONS.items()
        }
        warnings = []

        if len(optimized.split()) < 80:
            warnings.append("El prompt optimizado es demasiado corto.")

        if len(optimized) <= len(original):
            warnings.append("El prompt no amplía suficientemente la solicitud original.")

        for pattern, warning in self.INVENTION_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                warnings.append(warning)

        for pattern, warning in self.UNREQUESTED_SPECIFICS:
            optimized_matches = set(re.findall(pattern, text, flags=re.IGNORECASE))
            original_matches = set(re.findall(pattern, original_text, flags=re.IGNORECASE))
            allowed_matches = set()
            if "api" in original_text and "rest" in original_text:
                allowed_matches.add("json")

            if optimized_matches - original_matches - allowed_matches:
                warnings.append(warning)

        section_score = round(sum(sections.values()) / len(sections) * 70)
        length_score = 15 if len(optimized.split()) >= 80 else 5
        clarity_score = 15 if "\n" in optimized and ("-" in optimized or "1." in optimized) else 5
        score = max(0, section_score + length_score + clarity_score - len(warnings) * 10)

        return {
            "score": min(score, 100),
            "sections": sections,
            "warnings": warnings,
            "passed": score >= 70 and not warnings,
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
