#!/usr/bin/env python3
"""
Script para probar manualmente la detección de picos en una región específica.
Úsalo cuando tengas un pico que no se detecta.
"""

def test_manual_peak_detection():
    """
    Función para probar manualmente la detección de picos.
    Modifica los valores abajo según tu caso específico.
    """
    
    print("🔍 TEST MANUAL DE DETECCIÓN DE PICOS")
    print("=" * 50)
    
    try:
        import pandas as pd
        import numpy as np
        from curve_tools import diagnose_missing_peak, find_peaks_in_region
        
        # ===== CONFIGURA AQUÍ TUS DATOS =====
        # Cambia esta ruta por la de tu archivo de datos
        data_file = "tu_archivo_de_datos.csv"  # CAMBIAR ESTA LÍNEA
        
        # Rango de longitud de onda donde esperas el pico
        wavelength_range = (370, 380)  # CAMBIAR ESTOS VALORES
        
        print(f"📁 Intentando cargar: {data_file}")
        print(f"🎯 Buscando pico en rango: {wavelength_range[0]}-{wavelength_range[1]} nm")
        
        # Intenta cargar los datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Para usar este script:")
            print("   1. Guarda tus datos como CSV con columnas: Wavelength, Intensity")
            print("   2. Modifica 'data_file' en este script con la ruta correcta")
            print("   3. Modifica 'wavelength_range' con el rango donde esperas el pico")
            return False
        
        # Diagnóstico de la región
        print(f"\n🔍 DIAGNÓSTICO DEL RANGO {wavelength_range[0]}-{wavelength_range[1]} nm:")
        diagnosis = diagnose_missing_peak(df, wavelength_range, debug=True)
        
        # Intenta encontrar picos en la región específica
        print(f"\n🎯 BÚSQUEDA ESPECÍFICA EN REGIÓN:")
        region_results = find_peaks_in_region(df, wavelength_range, max_peaks=3)
        
        if 'error' in region_results:
            print(f"❌ Error: {region_results['error']}")
        else:
            print(f"📊 Picos encontrados en región: {region_results['num_peaks_found']}")
            for peak in region_results.get('all_peaks', []):
                print(f"   🔸 {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Este script requiere que las dependencias estén instaladas.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def create_test_data_with_weak_peak():
    """
    Crea datos de prueba con un pico débil para testing.
    """
    try:
        import numpy as np
        import pandas as pd
        
        print("\n📊 Creando datos de prueba con pico débil...")
        
        # Crear espectro sintético
        wavelength = np.linspace(350, 450, 200)
        
        # Línea base con ruido
        baseline = 100 + 0.1 * wavelength + np.random.normal(0, 5, len(wavelength))
        
        # Pico fuerte en 360 nm
        strong_peak = 500 * np.exp(-((wavelength - 360) / 8)**2)
        
        # Pico débil en 375 nm (el problemático)
        weak_peak = 30 * np.exp(-((wavelength - 375) / 4)**2)  # Muy débil
        
        # Pico medio en 420 nm
        medium_peak = 200 * np.exp(-((wavelength - 420) / 10)**2)
        
        # Combinar todo
        intensity = baseline + strong_peak + weak_peak + medium_peak
        
        # Añadir ruido realista
        intensity += np.random.normal(0, 8, len(wavelength))
        
        # Crear DataFrame
        df = pd.DataFrame({
            'Wavelength': wavelength,
            'Intensity': intensity
        })
        
        # Guardar datos de prueba
        test_file = "test_data_with_weak_peak.csv"
        df.to_csv(test_file, index=False)
        print(f"✅ Datos de prueba guardados en: {test_file}")
        print(f"   Pico débil esperado en ~375 nm")
        
        # Probar detección en el pico débil
        from curve_tools import diagnose_missing_peak, find_peaks_in_region
        
        weak_peak_range = (370, 380)
        print(f"\n🔍 Probando detección en rango {weak_peak_range[0]}-{weak_peak_range[1]} nm:")
        
        diagnosis = diagnose_missing_peak(df, weak_peak_range, debug=True)
        region_results = find_peaks_in_region(df, weak_peak_range, max_peaks=1)
        
        if region_results.get('num_peaks_found', 0) > 0:
            print(f"✅ ¡Pico débil detectado!")
            for peak in region_results['all_peaks']:
                print(f"   🔸 {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        else:
            print(f"❌ Pico débil NO detectado")
            print(f"💡 Prueba con parámetros aún más sensibles")
        
        return True
        
    except ImportError:
        print("❌ NumPy/Pandas no disponibles para crear datos de prueba")
        return False
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False


if __name__ == "__main__":
    print("🧪 HERRAMIENTA DE DIAGNÓSTICO DE PICOS")
    print("=" * 60)
    
    # Opción 1: Probar con datos reales (requiere configurar archivo)
    print("\n1️⃣  Probando con datos reales...")
    success = test_manual_peak_detection()
    
    # Opción 2: Crear y probar con datos sintéticos
    if not success:
        print("\n2️⃣  Creando datos de prueba...")
        create_test_data_with_weak_peak()
    
    print(f"\n" + "=" * 60)
    print("💡 INSTRUCCIONES:")
    print("   1. Modifica las variables al inicio de test_manual_peak_detection()")
    print("   2. Especifica tu archivo de datos y el rango del pico problemático")
    print("   3. Ejecuta este script para obtener diagnóstico detallado")
    print("   4. Usa los parámetros sugeridos para detectar el pico")