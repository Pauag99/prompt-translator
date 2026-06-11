#!/bin/bash
set -e

echo ""
echo "===================================================================="
echo "  PROMPT TRANSLATOR - INSTALADOR DE MISTRAL"
echo "===================================================================="
echo ""

if ! command -v ollama >/dev/null 2>&1; then
    echo "[ERROR] Ollama no esta instalado o no esta en PATH."
    echo ""
    echo "Instala Ollama desde:"
    echo "https://ollama.com/download"
    echo ""
    echo "Despues cierra y abre la terminal, y ejecuta este script otra vez."
    exit 1
fi

echo "[OK] Ollama detectado:"
ollama --version
echo ""

echo "Descargando/verificando Mistral 7B..."
echo "Esto puede tardar 10-20 minutos la primera vez."
echo ""

ollama pull mistral

echo ""
echo "===================================================================="
echo "[OK] MISTRAL ESTA LISTO"
echo "===================================================================="
echo ""
echo "Siguientes pasos recomendados:"
echo "  python3 -m venv .venv"
echo "  source .venv/bin/activate"
echo "  python -m pip install --upgrade pip"
echo "  python -m pip install -r requirements.txt"
echo "  python validate_setup.py"
echo "  python demo.py"
echo ""
echo "Si Ollama no responde, abre otra terminal y ejecuta:"
echo "  ollama serve"
echo ""
