#!/usr/bin/env python3
"""
Script para probar la nueva detección ULTRA AGRESIVA de hombros.
Crea datos sintéticos y verifica que encuentra hombros.
"""

def create_test_data_with_clear_shoulder():
    """Crea datos con un hombro muy claro para testing."""
    try:
        import numpy as np
        import pandas as pd
        
        print("📊 Creando datos de prueba con hombro claro...")
        
        # Crear espectro sintético
        wavelength = np.linspace(350, 450, 200)
        
        # Línea base
        baseline = 100 + 0.05 * wavelength
        
        # Pico principal grande en 400nm
        main_peak = 800 * np.exp(-((wavelength - 400) / 12)**2)
        
        # HOMBRO CLARO en 375nm
        shoulder = 150 * np.exp(-((wavelength - 375) / 6)**2)
        
        # Pico secundario en 425nm
        secondary_peak = 300 * np.exp(-((wavelength - 425) / 8)**2)
        
        # Combinar
        intensity = baseline + main_peak + shoulder + secondary_peak
        
        # Añadir ruido mínimo
        intensity += np.random.normal(0, 5, len(wavelength))
        
        # Crear DataFrame
        df = pd.DataFrame({
            'Wavelength': wavelength,
            'Intensity': intensity
        })
        
        print(f"✅ Datos creados:")
        print(f"   - Pico principal: ~400 nm")
        print(f"   - Hombro esperado: ~375 nm")
        print(f"   - Pico secundario: ~425 nm")
        
        return df, 375  # DataFrame y posición esperada del hombro
        
    except ImportError:
        print("❌ NumPy/Pandas no disponibles")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


def test_ultra_aggressive_detection():
    """Prueba la detección ultra agresiva."""
    
    print("🔬 TEST: DETECCIÓN ULTRA AGRESIVA DE HOMBROS")
    print("=" * 60)
    
    try:
        from curve_tools import (find_fluorescence_peaks_adaptive,
                                find_true_shoulders_excluding_peaks,
                                find_peaks_and_shoulders_combined)
        
        # Crear datos de prueba
        df, expected_shoulder = create_test_data_with_clear_shoulder()
        if df is None:
            return False
        
        # Paso 1: Detección tradicional
        print(f"\n1️⃣  DETECCIÓN TRADICIONAL DE PICOS:")
        traditional_results = find_fluorescence_peaks_adaptive(df, max_peaks=5, debug=False)
        
        if traditional_results.get('all_peaks'):
            for peak in traditional_results['all_peaks']:
                print(f"   🔸 P{peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        else:
            print("   ❌ No se detectaron picos tradicionales")
        
        # Paso 2: Detección ultra agresiva de hombros
        print(f"\n2️⃣  DETECCIÓN ULTRA AGRESIVA DE HOMBROS:")
        shoulder_results = find_true_shoulders_excluding_peaks(df, max_features=10, sensitivity=0.01)
        
        if shoulder_results.get('all_shoulders'):
            print(f"✅ Encontrados {shoulder_results['num_shoulders_found']} hombros:")
            for shoulder in shoulder_results['all_shoulders']:
                print(f"   🔹 {shoulder['index']}: {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u.")
                print(f"      Prominencia: {shoulder['prominence']:.2f}, Método: {shoulder['detection_method']}")
        else:
            print("❌ No se detectaron hombros")
        
        # Paso 3: Verificar si encontró el hombro esperado
        found_expected = False
        if shoulder_results.get('all_shoulders'):
            for shoulder in shoulder_results['all_shoulders']:
                if abs(shoulder['wavelength'] - expected_shoulder) < 10:  # Dentro de 10nm
                    found_expected = True
                    print(f"\n✅ ¡HOMBRO ESPERADO ENCONTRADO!")
                    print(f"   Esperado: ~{expected_shoulder} nm")
                    print(f"   Encontrado: {shoulder['wavelength']:.1f} nm")
                    print(f"   Diferencia: {abs(shoulder['wavelength'] - expected_shoulder):.1f} nm")
                    break
        
        if not found_expected:
            print(f"\n❌ HOMBRO ESPERADO NO ENCONTRADO")
            print(f"   Se esperaba hombro cerca de {expected_shoulder} nm")
        
        # Paso 4: Detección unificada
        print(f"\n3️⃣  DETECCIÓN UNIFICADA (todos como picos):")
        unified_results = find_peaks_and_shoulders_combined(df, max_total_peaks=8)
        
        if unified_results.get('all_peaks'):
            print(f"📊 Total picos unificados: {unified_results['num_peaks_found']}")
            print(f"   - Tradicionales: {unified_results.get('traditional_peaks_count', 0)}")
            print(f"   - Hombros: {unified_results.get('shoulder_peaks_count', 0)}")
            
            print(f"\n📋 Lista unificada:")
            for peak in unified_results['all_peaks']:
                detection_type = peak.get('detection_type', 'unknown')
                type_indicator = "(tradicional)" if detection_type == 'traditional_peak' else "(hombro)"
                print(f"   🔸 {peak['display_id']}: {peak['wavelength']:.1f} nm {type_indicator}")
        
        return found_expected
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Este script requiere numpy, pandas y scipy.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_real_data():
    """Plantilla para probar con datos reales."""
    
    # ===== CONFIGURA TUS DATOS AQUÍ =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    expected_shoulder_wavelength = 375  # <<<< CAMBIAR ESTO
    
    print(f"\n" + "=" * 60)
    print("🔍 TEST CON DATOS REALES")
    print("=" * 60)
    print(f"📁 Archivo: {data_file}")
    print(f"🎯 Hombro esperado cerca de: {expected_shoulder_wavelength} nm")
    
    try:
        import pandas as pd
        from curve_tools import find_peaks_and_shoulders_combined
        
        # Cargar datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Modifica 'data_file' al inicio de test_with_real_data()")
            return False
        
        # Probar detección unificada
        print(f"\n🔍 Ejecutando detección unificada ultra agresiva...")
        results = find_peaks_and_shoulders_combined(df, max_total_peaks=10)
        
        if results.get('all_peaks'):
            print(f"\n📊 Resultados:")
            print(f"   Total picos: {results['num_peaks_found']}")
            print(f"   Tradicionales: {results.get('traditional_peaks_count', 0)}")
            print(f"   Hombros: {results.get('shoulder_peaks_count', 0)}")
            
            print(f"\n📋 Todos los picos:")
            found_near_expected = False
            for peak in results['all_peaks']:
                detection_type = peak.get('detection_type', 'unknown')
                type_indicator = "(tradicional)" if detection_type == 'traditional_peak' else "(hombro)"
                print(f"   🔸 {peak['display_id']}: {peak['wavelength']:.1f} nm {type_indicator}")
                
                # Verificar si hay algo cerca del hombro esperado
                if abs(peak['wavelength'] - expected_shoulder_wavelength) < 15:
                    found_near_expected = True
                    distance = abs(peak['wavelength'] - expected_shoulder_wavelength)
                    print(f"      ⭐ ¡Cerca del hombro esperado! (diferencia: {distance:.1f} nm)")
            
            if not found_near_expected:
                print(f"\n⚠️  No se encontró nada cerca de {expected_shoulder_wavelength} nm")
                print(f"   Prueba con sensibilidad aún mayor o revisa la posición esperada")
        else:
            print(f"\n❌ No se detectaron picos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 PRUEBA DE DETECCIÓN ULTRA AGRESIVA")
    print("=" * 70)
    
    # Test con datos sintéticos
    success = test_ultra_aggressive_detection()
    
    if success:
        print(f"\n🎉 ¡TEST CON DATOS SINTÉTICOS EXITOSO!")
        print(f"✅ La detección ultra agresiva funciona")
        print(f"✅ Encontró el hombro esperado")
    else:
        print(f"\n❌ TEST FALLÓ - Revisar algoritmo")
    
    # Descomenta la siguiente línea para probar con datos reales:
    # test_with_real_data()
    
    print(f"\n" + "=" * 70)
    print("💡 PARA USAR CON TUS DATOS:")
    print("1. Descomenta test_with_real_data() arriba")
    print("2. Modifica 'data_file' y 'expected_shoulder_wavelength'")
    print("3. Ejecuta de nuevo este script")
    print("4. Si no encuentra el hombro, puedes disminuir aún más la sensibilidad")