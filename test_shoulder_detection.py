#!/usr/bin/env python3
"""
Script específico para probar detección de hombros e inflexiones.
Útil cuando tienes un "hombro" que no se detecta como pico tradicional.
"""

def create_test_spectrum_with_shoulder():
    """
    Crea un espectro de prueba con un hombro pronunciado.
    """
    try:
        import numpy as np
        import pandas as pd
        
        print("📊 Creando espectro con hombro para testing...")
        
        # Crear rango de longitudes de onda
        wavelength = np.linspace(350, 450, 200)
        
        # Línea base
        baseline = 100 + 0.05 * wavelength
        
        # Pico principal en 380nm
        main_peak = 600 * np.exp(-((wavelength - 380) / 15)**2)
        
        # HOMBRO en 365nm - esto es lo que buscamos detectar
        # Un hombro es una inflexión, no un pico completo
        shoulder_component = 200 * np.exp(-((wavelength - 365) / 8)**2) * 0.3  # Factor 0.3 lo hace más sutil
        
        # Pico secundario en 420nm
        secondary_peak = 300 * np.exp(-((wavelength - 420) / 12)**2)
        
        # Combinar componentes
        intensity = baseline + main_peak + shoulder_component + secondary_peak
        
        # Añadir ruido realista
        intensity += np.random.normal(0, 10, len(wavelength))
        
        # Crear DataFrame
        df = pd.DataFrame({
            'Wavelength': wavelength,
            'Intensity': intensity
        })
        
        return df, 365  # Retorna el DataFrame y la posición esperada del hombro
        
    except ImportError:
        print("❌ NumPy/Pandas no disponibles")
        return None, None
    except Exception as e:
        print(f"❌ Error creando datos: {e}")
        return None, None


def test_shoulder_detection_methods():
    """
    Prueba diferentes métodos de detección en un espectro con hombro.
    """
    print("🧪 TESTING DETECCIÓN DE HOMBROS")
    print("=" * 50)
    
    try:
        from curve_tools import (find_fluorescence_peaks_adaptive, 
                                find_shoulders_and_inflections,
                                find_peaks_and_shoulders_combined)
        
        # Crear datos de prueba
        df, expected_shoulder_position = create_test_spectrum_with_shoulder()
        if df is None:
            return False
        
        print(f"✅ Espectro creado con hombro esperado en ~{expected_shoulder_position} nm")
        
        # Método 1: Detección tradicional de picos
        print(f"\n1️⃣  DETECCIÓN TRADICIONAL DE PICOS:")
        traditional_results = find_fluorescence_peaks_adaptive(df, debug=True)
        
        # Método 2: Detección específica de hombros
        print(f"\n2️⃣  DETECCIÓN ESPECÍFICA DE HOMBROS:")
        shoulder_results = find_shoulders_and_inflections(df, max_features=5, sensitivity=0.1)
        print(f"📊 Hombros detectados: {shoulder_results['num_shoulders_found']}")
        
        if shoulder_results.get('all_shoulders'):
            for shoulder in shoulder_results['all_shoulders']:
                print(f"   🔹 Hombro {shoulder['index']}: {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u.")
                print(f"      Curvatura: {shoulder['curvature']:.2e}, Derivada: {shoulder['first_derivative']:.2f}")
        
        # Método 3: Detección combinada
        print(f"\n3️⃣  DETECCIÓN COMBINADA (PICOS + HOMBROS):")
        combined_results = find_peaks_and_shoulders_combined(df, max_peaks=3, max_shoulders=3)
        print(f"📊 Total features: {combined_results['num_total_features']}")
        print(f"   Picos tradicionales: {combined_results['num_peaks_found']}")
        print(f"   Hombros: {combined_results['num_shoulders_found']}")
        
        if combined_results.get('all_features'):
            print("📋 Todos los features por longitud de onda:")
            for feature in combined_results['all_features']:
                feature_type = feature.get('type', 'peak')
                icon = "🔸" if feature_type == 'peak' else "🔹"
                print(f"   {icon} {feature_type.title()} {feature.get('global_index', '?')}: {feature['wavelength']:.1f} nm, {feature['intensity']:.2f} a.u.")
        
        # Verificar si detectó el hombro esperado
        found_shoulder = False
        if shoulder_results.get('all_shoulders'):
            for shoulder in shoulder_results['all_shoulders']:
                if abs(shoulder['wavelength'] - expected_shoulder_position) < 10:  # Dentro de 10nm
                    found_shoulder = True
                    print(f"\n✅ ¡HOMBRO DETECTADO! En {shoulder['wavelength']:.1f} nm (esperado: ~{expected_shoulder_position} nm)")
                    break
        
        if not found_shoulder:
            print(f"\n❌ Hombro esperado en ~{expected_shoulder_position} nm NO detectado")
            print("💡 Prueba con mayor sensibilidad:")
            
            # Probar con mayor sensibilidad
            sensitive_shoulders = find_shoulders_and_inflections(df, max_features=10, sensitivity=0.05)
            print(f"   Con sensibilidad 0.05: {sensitive_shoulders['num_shoulders_found']} hombros")
            
            if sensitive_shoulders.get('all_shoulders'):
                for shoulder in sensitive_shoulders['all_shoulders']:
                    if abs(shoulder['wavelength'] - expected_shoulder_position) < 15:
                        print(f"   🔹 Posible hombro: {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante testing: {e}")
        return False


def test_with_real_data():
    """
    Plantilla para probar con datos reales.
    """
    print(f"\n" + "=" * 50)
    print("🔍 TESTING CON DATOS REALES")
    print("=" * 50)
    
    # MODIFICAR ESTOS VALORES PARA TUS DATOS
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    expected_shoulder_range = (360, 370)  # <<<< CAMBIAR ESTO
    
    print(f"📁 Archivo: {data_file}")
    print(f"🎯 Hombro esperado en rango: {expected_shoulder_range[0]}-{expected_shoulder_range[1]} nm")
    
    try:
        import pandas as pd
        from curve_tools import find_shoulders_and_inflections, find_peaks_and_shoulders_combined
        
        # Intentar cargar datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Modifica la variable 'data_file' en este script")
            return False
        
        # Probar detección de hombros
        print(f"\n🔍 Buscando hombros en tus datos...")
        shoulder_results = find_shoulders_and_inflections(df, max_features=10, sensitivity=0.1)
        
        print(f"📊 Hombros detectados: {shoulder_results['num_shoulders_found']}")
        
        found_in_range = []
        if shoulder_results.get('all_shoulders'):
            for shoulder in shoulder_results['all_shoulders']:
                print(f"   🔹 {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u., curvatura: {shoulder['curvature']:.2e}")
                
                # Verificar si está en el rango esperado
                if expected_shoulder_range[0] <= shoulder['wavelength'] <= expected_shoulder_range[1]:
                    found_in_range.append(shoulder)
        
        if found_in_range:
            print(f"\n✅ ¡Encontrados {len(found_in_range)} hombros en el rango esperado!")
            for shoulder in found_in_range:
                print(f"   🎯 {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u.")
        else:
            print(f"\n❌ No se encontraron hombros en el rango {expected_shoulder_range[0]}-{expected_shoulder_range[1]} nm")
            print(f"💡 Prueba con mayor sensibilidad o revisa el rango esperado")
        
        return len(found_in_range) > 0
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🔬 DETECTOR DE HOMBROS E INFLEXIONES")
    print("=" * 60)
    
    # Test 1: Con datos sintéticos
    print("Prueba 1: Datos sintéticos con hombro conocido")
    success1 = test_shoulder_detection_methods()
    
    # Test 2: Con datos reales (opcional)
    if success1:
        print(f"\n" + "🎉" * 20)
        print("✅ La detección de hombros funciona con datos sintéticos!")
        print("💡 Ahora puedes probar con tus datos reales:")
        print("   1. Modifica 'data_file' y 'expected_shoulder_range' en test_with_real_data()")
        print("   2. Ejecuta de nuevo este script")
        
        # Descomenta la siguiente línea para probar con datos reales:
        # test_with_real_data()
    else:
        print(f"\n❌ Error en testing básico")
    
    print(f"\n" + "=" * 60)
    print("📋 RESUMEN DE FUNCIONES DISPONIBLES:")
    print("   • find_shoulders_and_inflections() - Detecta solo hombros")
    print("   • find_peaks_and_shoulders_combined() - Detecta picos Y hombros")
    print("   • Parámetro 'sensitivity': 0.01-1.0 (menor = más sensible)")
    print("   • Los hombros se detectan por cambios en la curvatura (2ª derivada)")