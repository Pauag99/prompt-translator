"""
Casos de Prueba para Prompt Translator
Incluye ejemplos reales de uso en contexto profesional
"""

TEST_CASES = [
    {
        "id": "test_01",
        "category": "Web Scraping",
        "original": "Necesito un script que descargue imágenes de un sitio web",
        "expected_keywords": ["web scraping", "descargar", "imágenes", "url", "carpeta"],
        "description": "Solicitud técnica para web scraping"
    },
    {
        "id": "test_02",
        "category": "Análisis de Datos",
        "original": "Quiero que analices un CSV y me des un resumen estadístico",
        "expected_keywords": ["análisis", "estadístico", "datos", "csv", "resumen"],
        "description": "Solicitud de análisis de datos"
    },
    {
        "id": "test_03",
        "category": "Documentación",
        "original": "Necesito documentación clara para mi código Python",
        "expected_keywords": ["documentación", "código", "python", "comentarios", "docstring"],
        "description": "Solicitud de documentación técnica"
    },
    {
        "id": "test_04",
        "category": "Base de Datos",
        "original": "Optimi za una consulta SQL que es muy lenta",
        "expected_keywords": ["sql", "optimización", "consulta", "índice", "rendimiento"],
        "description": "Solicitud de optimización SQL"
    },
    {
        "id": "test_05",
        "category": "API REST",
        "original": "Crea una API REST con endpoints para gestionar usuarios",
        "expected_keywords": ["api", "rest", "endpoints", "usuarios", "crud"],
        "description": "Solicitud de desarrollo API"
    },
    {
        "id": "test_06",
        "category": "Machine Learning",
        "original": "Necesito un modelo que prediga rotación de clientes",
        "expected_keywords": ["modelo", "predicción", "machine learning", "clasificación", "datos"],
        "description": "Solicitud ML"
    },
    {
        "id": "test_07",
        "category": "Testing",
        "original": "Escribe tests unitarios para mi función de validación",
        "expected_keywords": ["test", "unitario", "validación", "pytest", "cobertura"],
        "description": "Solicitud de testing"
    },
    {
        "id": "test_08",
        "category": "DevOps",
        "original": "Configura Docker para mi aplicación Python",
        "expected_keywords": ["docker", "contenedor", "imagen", "dockerfile", "compose"],
        "description": "Solicitud de DevOps"
    },
    {
        "id": "test_09",
        "category": "Seguridad",
        "original": "Revisa mi código para vulnerabilidades de seguridad",
        "expected_keywords": ["seguridad", "vulnerabilidad", "validación", "inyección", "auth"],
        "description": "Solicitud de seguridad"
    },
    {
        "id": "test_10",
        "category": "Resumen",
        "original": "Hazme un resumen ejecutivo de este texto técnico",
        "expected_keywords": ["resumen", "ejecutivo", "puntos clave", "conciso", "relevante"],
        "description": "Solicitud de resumen"
    },
    {
        "id": "test_11",
        "category": "Refactoring",
        "original": "Refactoriza este código para que sea más limpio y mantenible",
        "expected_keywords": ["refactorizar", "código limpio", "legibilidad", "mantenibilidad", "patrones"],
        "description": "Solicitud de refactoring"
    },
    {
        "id": "test_12",
        "category": "Arquitectura",
        "original": "Diseña la arquitectura para una app de e-commerce escalable",
        "expected_keywords": ["arquitectura", "diseño", "escalabilidad", "microservicios", "base datos"],
        "description": "Solicitud de arquitectura"
    }
]

QUICK_TESTS = [
    "Crea un script Python que automatice tareas del sistema",
    "Optimiza esta consulta de base de datos que es muy lenta",
    "Necesito un resumen profesional de mis logros en el proyecto",
    "Diseña un modelo de datos para un sistema de gestión de proyectos",
    "Revisa y mejora este fragmento de código JavaScript",
]

PROFESSIONAL_CONTEXT_TESTS = [
    {
        "context": "Software Development",
        "requests": [
            "Refactoriza una función de validación de emails",
            "Crea una API REST completa con autenticación",
            "Diseña un sistema de caché distribuido",
            "Implementa un patrón de retry con backoff exponencial",
            "Documenta una arquitectura de microservicios"
        ]
    },
    {
        "context": "Data Science",
        "requests": [
            "Prepara datos para un modelo de predicción",
            "Visualiza correlaciones entre variables",
            "Normaliza características para machine learning",
            "Detecta y maneja valores atípicos",
            "Evalúa el rendimiento de un modelo"
        ]
    },
    {
        "context": "DevOps",
        "requests": [
            "Configura un pipeline CI/CD en Jenkins",
            "Automatiza el despliegue a Kubernetes",
            "Monitorea una aplicación en producción",
            "Escala automáticamente basado en carga",
            "Implementa recuperación ante desastres"
        ]
    }
]

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CASOS DE PRUEBA DISPONIBLES")
    print("="*70 + "\n")
    
    print(f"✓ {len(TEST_CASES)} Casos de prueba completos")
    print(f"✓ {len(QUICK_TESTS)} Pruebas rápidas")
    print(f"✓ {sum(len(ctx['requests']) for ctx in PROFESSIONAL_CONTEXT_TESTS)} Casos por contexto profesional\n")
    
    print("CASOS COMPLETOS:")
    for test in TEST_CASES[:5]:
        print(f"  [{test['id']}] {test['category']}: {test['original'][:50]}...")
    print(f"  ... y {len(TEST_CASES) - 5} más\n")
    
    print("PRUEBAS RÁPIDAS (primeras 3):")
    for i, test in enumerate(QUICK_TESTS[:3], 1):
        print(f"  {i}. {test[:60]}...")
