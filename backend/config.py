"""
Configuración del Prompt Translator
Optimizado para Mistral 7B en portátil con 16GB RAM
"""

# Modelo a utilizar
MODEL = "mistral"

# URL del servidor Ollama
OLLAMA_BASE_URL = "http://localhost:11434"

# Parámetros de generación (optimizados para portátil)
GENERATION_PARAMS = {
    # Número máximo de tokens a generar (evita respuestas muy largas)
    "num_predict": 500,
    
    # Temperatura: controla la creatividad (0.0-1.0)
    # 0.0 = determinista, 1.0 = muy creativo
    # 0.7 es equilibrio para prompts
    "temperature": 0.7,
    
    # Top-p: diversidad de tokens considerados
    # 0.9 es good para balance
    "top_p": 0.9,
    
    # Penalty para repeticiones
    "repeat_penalty": 1.1,
    
    # Timeout en segundos
    "timeout": 60
}

# Modelos alternativos disponibles en Ollama
ALTERNATIVE_MODELS = {
    "mistral": {
        "description": "7B - Recomendado para 16GB RAM",
        "speed": "Rápido",
        "quality": "Muy Buena",
        "ram_required": "8-10GB"
    },
    "llama2": {
        "description": "7B - Más rápido, menos preciso",
        "speed": "Muy Rápido",
        "quality": "Buena",
        "ram_required": "8-10GB"
    },
    "neural-chat": {
        "description": "7B - Mejor para conversaciones",
        "speed": "Rápido",
        "quality": "Buena",
        "ram_required": "8-10GB"
    },
    "dolphin-mixtral": {
        "description": "8x7B - Mejor calidad (más pesado)",
        "speed": "Lento",
        "quality": "Excelente",
        "ram_required": "16-20GB"
    }
}

# Mensajes del sistema para el modelo
SYSTEM_PROMPTS = {
    "default": """Eres un experto en ingeniería de prompts. Tu tarea es transformar 
solicitudes en lenguaje natural en prompts optimizados, claros y eficientes para modelos de IA.

Principios para optimizar prompts:
1. Sé específico y claro en las instrucciones
2. Define el rol o contexto del modelo
3. Proporciona ejemplos si es necesario
4. Especifica el formato de salida deseado
5. Incluye restricciones o limitaciones relevantes
6. Usa estructura y separadores claros

Devuelve solo el prompt optimizado, sin explicaciones adicionales.""",
    
    "technical": """Eres un experto en ingeniería de prompts para contextos técnicos.
Tu tarea es transformar solicitudes en prompts optimizados para generar código,
consultas de base de datos, scripts y documentación técnica.

Asegúrate de:
1. Incluir lenguaje de programación específico si aplica
2. Definir restricciones técnicas claras
3. Incluir ejemplos de código cuando sea relevante
4. Especificar formato de salida (JSON, XML, etc.)

Devuelve solo el prompt optimizado."""
}
