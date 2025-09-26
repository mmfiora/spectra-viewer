#!/usr/bin/env python3
"""
Script de debug específico para verificar la detección de hombros.
Muestra exactamente dónde está detectando el hombro y por qué.
"""

def debug_shoulder_detection(data_file, shoulder_region, sensitivity=0.05):
    """
    Debug detallado de la detección de hombros en una región específica.
    
    Parameters:
    - data_file: ruta al archivo CSV
    - shoulder_region: tupla (min_nm, max_nm) donde buscar
    - sensitivity: sensibilidad de detección
    """
    
    print("🔬 DEBUG DETALLADO DE DETECCIÓN DE HOMBROS")
    print("=" * 60)
    print(f"📁 Archivo: {data_file}")
    print(f"🎯 Región: {shoulder_region[0]}-{shoulder_region[1]} nm")
    print(f"🔧 Sensibilidad: {sensitivity}")
    
    try:
        import pandas as pd
        import numpy as np
        from scipy.signal import savgol_filter
        from curve_tools import find_shoulder_in_region
        
        # Cargar datos
        df = pd.read_csv(data_file)
        print(f"✅ Datos cargados: {len(df)} puntos")
        
        # Extraer datos básicos
        wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
        intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
        
        # Ordenar
        sort_indices = np.argsort(wavelength)
        wavelength = wavelength[sort_indices]
        intensity = intensity[sort_indices]
        
        # Filtrar región
        mask = (wavelength >= shoulder_region[0]) & (wavelength <= shoulder_region[1])
        region_wl = wavelength[mask]
        region_int = intensity[mask]
        
        print(f"\n📊 ANÁLISIS DE LA REGIÓN:")
        print(f"   Puntos en región: {len(region_wl)}")
        print(f"   Intensidad máxima: {np.max(region_int):.2f}")
        print(f"   Intensidad mínima: {np.min(region_int):.2f}")
        print(f"   Rango de intensidad: {np.max(region_int) - np.min(region_int):.2f}")
        
        # Suavizar datos
        if len(region_int) >= 5:
            smoothed_int = savgol_filter(region_int, min(len(region_int)//2*2-1, 7), polyorder=2)
        else:
            smoothed_int = region_int.copy()
        
        # Calcular derivadas
        first_deriv = np.gradient(smoothed_int, region_wl)
        second_deriv = np.gradient(first_deriv, region_wl)
        
        print(f"\n🔍 BÚSQUEDA DE MÁXIMOS LOCALES (picos de hombros):")
        max_candidates = []
        
        for i in range(2, len(region_int) - 2):
            # Verificar si es un máximo local
            is_local_max = (region_int[i] > region_int[i-1] and 
                           region_int[i] > region_int[i+1] and
                           region_int[i] >= region_int[i-2] and 
                           region_int[i] >= region_int[i+2])
            
            if is_local_max:
                # Calcular características
                window = min(4, len(region_int)//3)
                start = max(0, i - window)
                end = min(len(region_int), i + window + 1)
                local_min = np.min(region_int[start:end])
                prominence = region_int[i] - local_min
                
                curvature = second_deriv[i] if i < len(second_deriv) else 0
                first_d = first_deriv[i] if i < len(first_deriv) else 0
                
                max_candidates.append({
                    'index': i,
                    'wavelength': region_wl[i],
                    'intensity': region_int[i],
                    'prominence': prominence,
                    'curvature': curvature,
                    'first_derivative': first_d
                })
                
                print(f"   🔸 Máximo local en {region_wl[i]:.1f} nm:")
                print(f"      Intensidad: {region_int[i]:.2f}")
                print(f"      Prominencia: {prominence:.2f}")
                print(f"      Curvatura: {curvature:.2e}")
                print(f"      1ª derivada: {first_d:.2e}")
        
        if not max_candidates:
            print("   ❌ No se encontraron máximos locales en la región")
            print("   💡 Posibles causas:")
            print("      - La región es demasiado pequeña")
            print("      - El hombro es muy sutil")
            print("      - Los datos tienen mucho ruido")
        
        print(f"\n🧮 ANÁLISIS DE DERIVADAS:")
        print(f"   1ª derivada - Rango: {np.min(first_deriv):.2e} a {np.max(first_deriv):.2e}")
        print(f"   2ª derivada - Rango: {np.min(second_deriv):.2e} a {np.max(second_deriv):.2e}")
        
        # Buscar cambios de signo en primera derivada (cruces por cero)
        zero_crossings = []
        for i in range(1, len(first_deriv) - 1):
            if ((first_deriv[i-1] > 0 and first_deriv[i+1] < 0) or
                (first_deriv[i-1] < 0 and first_deriv[i+1] > 0)):
                zero_crossings.append({
                    'index': i,
                    'wavelength': region_wl[i],
                    'intensity': region_int[i],
                    'transition': 'pos_to_neg' if first_deriv[i-1] > 0 else 'neg_to_pos'
                })
        
        print(f"\n🔄 CRUCES POR CERO EN 1ª DERIVADA:")
        for zc in zero_crossings:
            print(f"   🔸 {zc['wavelength']:.1f} nm - {zc['transition']} (intensidad: {zc['intensity']:.2f})")
        
        # Ejecutar la función oficial y comparar
        print(f"\n🎯 RESULTADO DE LA FUNCIÓN OFICIAL:")
        results = find_shoulder_in_region(df, shoulder_region, sensitivity=sensitivity)
        
        if results.get('best_shoulder'):
            best = results['best_shoulder']
            print(f"✅ Mejor candidato detectado:")
            print(f"   Posición: {best['wavelength']:.1f} nm")
            print(f"   Intensidad: {best['intensity']:.2f}")
            print(f"   Método: {best['detection_method']}")
            
            # Verificar si coincide con nuestros máximos locales
            found_match = False
            for candidate in max_candidates:
                if abs(candidate['wavelength'] - best['wavelength']) < 1:  # Dentro de 1nm
                    print(f"✅ Coincide con máximo local detectado manualmente")
                    found_match = True
                    break
            
            if not found_match:
                print(f"⚠️  NO coincide con los máximos locales encontrados manualmente")
                print(f"   Esto sugiere que está detectando una inflexión, no el pico del hombro")
        else:
            print(f"❌ La función oficial no detectó ningún hombro")
        
        return results
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {data_file}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def suggest_shoulder_position(data_file, shoulder_region):
    """
    Sugiere dónde debería estar el pico del hombro basado en máximos locales.
    """
    print(f"\n💡 SUGERENCIA DE POSICIÓN DEL HOMBRO:")
    
    try:
        import pandas as pd
        import numpy as np
        
        df = pd.read_csv(data_file)
        wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
        intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
        
        sort_indices = np.argsort(wavelength)
        wavelength = wavelength[sort_indices]
        intensity = intensity[sort_indices]
        
        mask = (wavelength >= shoulder_region[0]) & (wavelength <= shoulder_region[1])
        region_wl = wavelength[mask]
        region_int = intensity[mask]
        
        if len(region_int) == 0:
            print("❌ No hay datos en la región especificada")
            return None
        
        # Encontrar el máximo absoluto en la región
        max_idx = np.argmax(region_int)
        max_wavelength = region_wl[max_idx]
        max_intensity = region_int[max_idx]
        
        print(f"📍 Máximo absoluto en región: {max_wavelength:.1f} nm (intensidad: {max_intensity:.2f})")
        
        # Buscar todos los máximos locales
        local_maxima = []
        for i in range(1, len(region_int) - 1):
            if (region_int[i] > region_int[i-1] and region_int[i] > region_int[i+1]):
                local_maxima.append({
                    'wavelength': region_wl[i],
                    'intensity': region_int[i],
                    'prominence': region_int[i] - min(region_int[max(0, i-3):min(len(region_int), i+4)])
                })
        
        if local_maxima:
            print(f"📍 Máximos locales encontrados:")
            local_maxima.sort(key=lambda x: x['intensity'], reverse=True)
            for i, lm in enumerate(local_maxima):
                print(f"   {i+1}. {lm['wavelength']:.1f} nm - intensidad: {lm['intensity']:.2f}, prominencia: {lm['prominence']:.2f}")
            
            print(f"\n💡 Sugerencia: El pico del hombro probablemente esté en {local_maxima[0]['wavelength']:.1f} nm")
            return local_maxima[0]['wavelength']
        else:
            print(f"❌ No se encontraron máximos locales en la región")
            return max_wavelength
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    # ===== CONFIGURA AQUÍ TUS DATOS =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    shoulder_region = (365, 375)   # <<<< CAMBIAR ESTO
    sensitivity = 0.05             # <<<< CAMBIAR SI ES NECESARIO
    
    print("🔬 HERRAMIENTA DE DEBUG PARA HOMBROS")
    print("=" * 60)
    
    # Debug detallado
    results = debug_shoulder_detection(data_file, shoulder_region, sensitivity)
    
    # Sugerencia de posición
    suggested_pos = suggest_shoulder_position(data_file, shoulder_region)
    
    print(f"\n" + "=" * 60)
    print("💡 INSTRUCCIONES:")
    print("1. Modifica las variables al inicio del script")
    print("2. Compara el resultado de la función oficial con los máximos locales")
    print("3. Si no coinciden, el algoritmo está detectando una inflexión, no el pico")
    print("4. Usa la posición sugerida como referencia para el verdadero pico del hombro")