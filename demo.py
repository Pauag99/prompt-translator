"""
Script de Demostración - Prompt Translator
Ejecuta casos de prueba y valida que todo funciona correctamente
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from translator import PromptTranslator, configure_console_encoding
from test_cases import TEST_CASES, QUICK_TESTS, PROFESSIONAL_CONTEXT_TESTS


def print_header(text):
    """Imprime un header formateado"""
    print("\n" + "="*75)
    print(f"  {text}")
    print("="*75)


def print_section(text):
    """Imprime una sección"""
    print(f"\n{text}")
    print("-" * 75)


def print_result(original, result):
    """Imprime un resultado formateado"""
    if result["status"] == "success":
        print(f"\n📝 SOLICITUD ORIGINAL:")
        print(f"   {original}")
        
        print(f"\n✨ PROMPT OPTIMIZADO:")
        # Limitar a primeras 5 líneas para legibilidad
        optimized_lines = result["optimized"].split('\n')
        for line in optimized_lines[:8]:
            if line.strip():
                print(f"   {line}")
        
        if len(optimized_lines) > 8:
            print(f"   ... (truncado, {len(result['optimized'].split())} palabras totales)")
        
        if result["tips"]:
            print(f"\n💡 MEJORAS DETECTADAS:")
            for tip in result["tips"]:
                print(f"   {tip}")

        quality = result.get("quality")
        if quality:
            status = "APROBADO" if quality["passed"] else "REVISAR"
            print(f"\nCALIDAD: {quality['score']}/100 - {status}")
            for warning in quality["warnings"]:
                print(f"   AVISO: {warning}")
    else:
        print(f"\n❌ ERROR: {result['error']}")
    
    print()


def run_quick_demo():
    """Ejecuta una demostración rápida con pocos casos"""
    print_header("DEMOSTRACIÓN RÁPIDA - PROMPT TRANSLATOR")
    
    translator = PromptTranslator(model="mistral")
    
    print(f"\n📊 Información:")
    print(f"   Modelo: {translator.model}")
    print(f"   Base URL: {translator.base_url}")
    print(f"   Casos a probar: {len(QUICK_TESTS)}")
    print(f"   Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
    
    successful = 0
    failed = 0
    
    for i, request in enumerate(QUICK_TESTS, 1):
        print_section(f"Prueba {i}/{len(QUICK_TESTS)}")
        print(f"⏳ Procesando...")
        
        start_time = time.time()
        result = translator.translate(request)
        elapsed_time = time.time() - start_time
        
        print_result(request, result)
        
        if result["status"] == "success":
            successful += 1
            print(f"⏱️  Tiempo: {elapsed_time:.2f}s")
        else:
            failed += 1
    
    print_header("RESUMEN DE RESULTADOS")
    print(f"\n✅ Exitosas: {successful}/{len(QUICK_TESTS)}")
    print(f"❌ Fallidas: {failed}/{len(QUICK_TESTS)}")
    print(f"📊 Tasa de éxito: {(successful/len(QUICK_TESTS)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ¡Todas las pruebas pasaron correctamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Verifica la conexión con Ollama.")


def run_comprehensive_test():
    """Ejecuta todas las pruebas disponibles"""
    print_header("PRUEBAS COMPLETAS - PROMPT TRANSLATOR")
    
    translator = PromptTranslator(model="mistral")
    
    print(f"\n📊 Información:")
    print(f"   Modelo: {translator.model}")
    print(f"   Base URL: {translator.base_url}")
    print(f"   Casos a probar: {len(TEST_CASES)}")
    print(f"   Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
    
    results_by_category = {}
    
    for test in TEST_CASES:
        category = test["category"]
        if category not in results_by_category:
            results_by_category[category] = {"success": 0, "failed": 0, "times": []}
        
        print_section(f"{category}: {test['original'][:60]}...")
        print(f"⏳ Procesando (ID: {test['id']})...")
        
        start_time = time.time()
        result = translator.translate(test["original"])
        elapsed_time = time.time() - start_time
        
        if result["status"] == "success":
            results_by_category[category]["success"] += 1
            results_by_category[category]["times"].append(elapsed_time)
            print(f"✅ Éxito en {elapsed_time:.2f}s")
        else:
            results_by_category[category]["failed"] += 1
            print(f"❌ Error: {result['error']}")
    
    # Resumen por categoría
    print_header("RESULTADOS POR CATEGORÍA")
    
    total_success = 0
    total_failed = 0
    all_times = []
    
    for category, results in sorted(results_by_category.items()):
        success = results["success"]
        failed = results["failed"]
        total = success + failed
        times = results["times"]
        
        total_success += success
        total_failed += failed
        all_times.extend(times)
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n{category}:")
            print(f"  ✅ Exitosas: {success}/{total}")
            print(f"  ⏱️  Tiempo promedio: {avg_time:.2f}s")
    
    # Resumen general
    print_header("RESUMEN GENERAL")
    total_tests = total_success + total_failed
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Pruebas exitosas: {total_success}/{total_tests}")
    print(f"❌ Pruebas fallidas: {total_failed}/{total_tests}")
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    
    if all_times:
        avg_time = sum(all_times) / len(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        
        print(f"\n⏱️  Estadísticas de tiempo:")
        print(f"   Mínimo: {min_time:.2f}s")
        print(f"   Máximo: {max_time:.2f}s")
        print(f"   Promedio: {avg_time:.2f}s")
        print(f"   Total: {sum(all_times):.2f}s")
    
    print(f"\n🏁 Finalizó a: {datetime.now().strftime('%H:%M:%S')}")
    
    if total_failed == 0:
        print("\n🎉 ¡Todas las pruebas pasaron correctamente!")
        print("✨ El Prompt Translator está listo para producción.")
    else:
        print(f"\n⚠️  {total_failed} prueba(s) fallaron.")
        print("   Asegúrate de que Ollama esté ejecutándose correctamente.")


def run_single_test(query):
    """Ejecuta una prueba individual"""
    print_header("PRUEBA INDIVIDUAL - PROMPT TRANSLATOR")
    
    translator = PromptTranslator(model="mistral")
    
    print(f"\n🔍 Solicitud: {query}\n")
    
    start_time = time.time()
    result = translator.translate(query)
    elapsed_time = time.time() - start_time
    
    print_result(query, result)
    
    if result["status"] == "success":
        print(f"⏱️  Tiempo total: {elapsed_time:.2f}s")


def main():
    """Función principal"""
    print("\n")
    print("╔" + "="*73 + "╗")
    print("║" + " "*73 + "║")
    print("║" + "  PROMPT TRANSLATOR - DEMO Y VALIDACIÓN".center(73) + "║")
    print("║" + "  Traductor de prompts con Mistral 7B".center(73) + "║")
    print("║" + " "*73 + "║")
    print("╚" + "="*73 + "╝")
    
    print("\n¿Qué quieres hacer?\n")
    print("1. Prueba rápida (5 casos - ~30-60 segundos)")
    print("2. Pruebas completas (12 casos - ~2-3 minutos)")
    print("3. Prueba individual (ingresa tu propia solicitud)")
    print("4. Salir")
    
    while True:
        choice = input("\nOpción (1-4): ").strip()
        
        if choice == "1":
            try:
                run_quick_demo()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\n⚠️  Asegúrate de que:")
                print("   1. Ollama está ejecutándose (ollama serve)")
                print("   2. Mistral está descargado (ollama pull mistral)")
                print("   3. Las dependencias están instaladas (pip install -r requirements.txt)")
            break
        
        elif choice == "2":
            try:
                run_comprehensive_test()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("\n⚠️  Asegúrate de que:")
                print("   1. Ollama está ejecutándose (ollama serve)")
                print("   2. Mistral está descargado (ollama pull mistral)")
                print("   3. Las dependencias están instaladas (pip install -r requirements.txt)")
            break
        
        elif choice == "3":
            query = input("\nIngresa tu solicitud: ").strip()
            if query:
                try:
                    run_single_test(query)
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    print("\n⚠️  Asegúrate de que Ollama está ejecutándose.")
            break
        
        elif choice == "4":
            print("\n👋 Hasta luego!\n")
            break
        
        else:
            print("❌ Opción inválida. Intenta de nuevo.")


if __name__ == "__main__":
    configure_console_encoding()

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario.")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
