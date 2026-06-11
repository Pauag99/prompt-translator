"""
Validador de Instalación - Prompt Translator
Verifica que todo esté correctamente instalado antes de ejecutar
"""

import sys
import subprocess
import os
import shutil
from pathlib import Path


def configure_console_encoding():
    """Evita errores Unicode en consolas Windows con cp1252."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def print_check(status, message):
    """Imprime un check de validación"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")
    return status


def print_header(text):
    """Imprime un header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def check_python_version():
    """Verifica la versión de Python"""
    print_header("1. VERIFICACIÓN DE PYTHON")
    
    version = sys.version_info
    is_valid = version.major >= 3 and version.minor >= 8
    
    print_check(is_valid, f"Python {version.major}.{version.minor}.{version.micro}")
    
    if not is_valid:
        print("   ⚠️  Se requiere Python 3.8 o superior")
        return False
    
    return True


def check_ollama():
    executable = shutil.which("ollama")
    if not executable and os.name == "nt":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            candidate = Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe"
            if candidate.exists():
                executable = str(candidate)

    """Verifica si Ollama está instalado"""
    print_header("2. VERIFICACIÓN DE OLLAMA")
    
    try:
        result = subprocess.run(
            [executable or "ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_check(True, f"Ollama instalado: {version}")
            return True
        else:
            print_check(False, "Ollama no responde")
            return False
    
    except FileNotFoundError:
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print_check(True, "Ollama detectado por API local en localhost:11434")
                print("   Aviso: el comando 'ollama' no está en el PATH de esta terminal")
                return True
        except Exception:
            pass

        print_check(False, "Ollama no está instalado")
        print("   Descárgalo desde: https://ollama.com/download")
        return False
    except subprocess.TimeoutExpired:
        print_check(False, "Ollama no responde (timeout)")
        return False
    except Exception as e:
        print_check(False, f"Error al verificar Ollama: {e}")
        return False


def check_ollama_running():
    """Verifica si Ollama está ejecutándose"""
    print_header("3. VERIFICACIÓN DE OLLAMA EN EJECUCIÓN")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            print_check(True, "Ollama está ejecutándose en localhost:11434")
            
            # Intenta parsear modelos disponibles
            try:
                data = response.json()
                models = data.get("models", [])
                
                if models:
                    print(f"   Modelos disponibles: {len(models)}")
                    for model in models[:3]:
                        print(f"     - {model.get('name', 'Unknown')}")
                    if len(models) > 3:
                        print(f"     ... y {len(models) - 3} más")
                else:
                    print("   ⚠️  No hay modelos descargados")
                    print("   Descarga uno: ollama pull mistral")
                
            except:
                pass
            
            return True
        else:
            print_check(False, f"Ollama responde con estado {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_check(False, "No se puede conectar con Ollama")
        print("   Ejecuta en otra terminal: ollama serve")
        return False
    except Exception as e:
        print_check(False, f"Error al verificar Ollama: {e}")
        return False


def check_mistral_model():
    """Verifica si Mistral está descargado"""
    print_header("4. VERIFICACIÓN DE MODELO MISTRAL")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if "mistral" in model_names:
                print_check(True, "Mistral está descargado")
                return True
            else:
                print_check(False, "Mistral no está descargado")
                print("   Descárgalo: ollama pull mistral")
                print("   Esto puede tomar 10-15 minutos")
                return False
    
    except Exception as e:
        print_check(False, f"Error al verificar: {e}")
        return False


def check_python_packages():
    """Verifica los paquetes Python requeridos"""
    print_header("5. VERIFICACIÓN DE PAQUETES PYTHON")
    
    required_packages = {
        "requests": "requests",
        "pytest": "pytest",
        "colorama": "colorama"
    }
    
    all_ok = True
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_check(True, f"{package_name} instalado")
        except ImportError:
            print_check(False, f"{package_name} no instalado")
            print(f"   Instala: pip install {package_name}")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """Verifica la estructura del proyecto"""
    print_header("6. VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO")
    
    base_dir = Path(__file__).parent
    required_files = [
        "backend/translator.py",
        "backend/config.py",
        "tests/test_translator.py",
        "tests/test_cases.py",
        "requirements.txt",
        "README.md",
        "SETUP.txt"
    ]
    
    all_ok = True
    
    for file_path in required_files:
        full_path = base_dir / file_path
        exists = full_path.exists()
        print_check(exists, file_path)
        if not exists:
            all_ok = False
    
    return all_ok


def main():
    """Ejecuta todas las validaciones"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + "  VALIDADOR DE INSTALACIÓN - PROMPT TRANSLATOR".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    checks = [
        ("Python 3.8+", check_python_version),
        ("Ollama instalado", check_ollama),
        ("Ollama ejecutándose", check_ollama_running),
        ("Modelo Mistral", check_mistral_model),
        ("Paquetes Python", check_python_packages),
        ("Estructura del proyecto", check_project_structure),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error en validación: {e}")
            results[name] = False
    
    # Resumen
    print_header("RESUMEN DE VALIDACIÓN")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {passed}/{total} validaciones pasadas")
    print(f"{'='*70}\n")
    
    if all(results.values()):
        print("🎉 ¡Todo está correctamente configurado!")
        print("\n📝 Próximo paso:")
        print("   python demo.py")
        return 0
    else:
        print("⚠️  Hay problemas que necesitan solucionar:")
        
        issues = []
        if not results.get("Python 3.8+"):
            issues.append("- Instala Python 3.8 o superior desde python.org")
        if not results.get("Ollama instalado"):
            issues.append("- Instala Ollama desde https://ollama.com/download")
        if not results.get("Ollama ejecutándose"):
            issues.append("- Ejecuta 'ollama serve' en una terminal")
        if not results.get("Modelo Mistral"):
            issues.append("- Descarga Mistral: ollama pull mistral")
        if not results.get("Paquetes Python"):
            issues.append("- Instala dependencias: pip install -r requirements.txt")
        
        for issue in issues:
            print(f"   {issue}")
        
        print("\nUna vez resueltos los problemas, ejecuta de nuevo este validador.")
        return 1


if __name__ == "__main__":
    configure_console_encoding()
    sys.exit(main())
