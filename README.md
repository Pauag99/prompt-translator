# Prompt Translator

Traductor local de prompts que convierte solicitudes en lenguaje natural en
prompts optimizados para modelos de IA.

Funciona con Ollama y usa `mistral` como modelo por defecto. Todo corre en local:
despues de descargar el modelo, no necesitas enviar datos a servicios externos.

## Requisitos

- Python 3.10+
- Ollama
- Modelo `mistral` descargado con Ollama
- 8 GB RAM minimo, 16 GB recomendado
- 8 GB libres en disco

## Preparar en otro PC

Lee primero:

```text
QUICKSTART.txt
```

En Windows puedes ejecutar el instalador completo:

```bat
setup_new_pc.bat
```

Ese script crea `.venv`, instala dependencias, comprueba Ollama, descarga
`mistral` y ejecuta la validacion.

## Instalacion manual rapida

Windows:

```bat
py -3 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull mistral
python validate_setup.py
python demo.py
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull mistral
python validate_setup.py
python demo.py
```

## Uso diario

Si Ollama no esta activo:

```bash
ollama serve
```

Despues ejecuta:

```bash
python demo.py
```

La demo permite:

1. Prueba rapida
2. Pruebas completas
3. Prueba individual
4. Salir

## Validacion

```bash
python validate_setup.py
python -m pytest
```

Estado esperado:

- `validate_setup.py`: 6/6 validaciones pasadas
- `pytest`: tests pasados

## Benchmark complejo

El proyecto incluye 40 casos avanzados con ambiguedad, restricciones,
supuestos prohibidos y solicitudes adversariales.

Ejecutar una muestra rapida:

```bash
python benchmark_complex.py --limit 5
```

Ejecutar una categoria:

```bash
python benchmark_complex.py --category Seguridad
```

Ejecutar todos los casos y guardar un informe:

```bash
python benchmark_complex.py --output benchmark_reports/latest.json
```

El informe mide calidad, cobertura de conceptos, supuestos prohibidos y tiempos.

## Estructura

```text
prompt-translator/
├── backend/
│   ├── translator.py
│   └── config.py
├── tests/
│   ├── test_translator.py
│   └── test_cases.py
├── demo.py
├── benchmark_complex.py
├── validate_setup.py
├── setup_new_pc.bat
├── install_mistral.bat
├── requirements.txt
├── QUICKSTART.txt
├── SETUP.txt
└── README.md
```

## Notas

- No copies `.venv` a otro PC; crealo de nuevo.
- No copies `__pycache__`.
- Los modelos de Ollama se descargan en cada PC con `ollama pull mistral`.
- Si quieres usar otro modelo, cambia `MODEL` en `backend/config.py` o instancia
  `PromptTranslator(model="nombre")`.
