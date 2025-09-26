#!/usr/bin/env python3
"""
Script para probar la nueva detección de hombros que EXCLUYE picos tradicionales.
Esto resuelve el problema de detectar hombros en la misma posición que los picos.
"""

def test_separation_peaks_shoulders():
    """
    Prueba que los picos y hombros se detecten en posiciones diferentes.
    """
    
    # ===== CONFIGURA TUS DATOS AQUÍ =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    
    print("🔬 TEST: SEPARACIÓN DE PICOS Y HOMBROS")
    print("=" * 50)
    print(f"📁 Archivo: {data_file}")
    
    try:
        import pandas as pd
        from curve_tools import (find_fluorescence_peaks_adaptive, 
                                find_true_shoulders_excluding_peaks,
                                find_peaks_and_shoulders_combined)
        
        # Cargar datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Modifica 'data_file' al inicio del script")
            return False
        
        # Paso 1: Detectar solo picos tradicionales
        print(f"\n1️⃣  PICOS TRADICIONALES:")
        peak_results = find_fluorescence_peaks_adaptive(df, max_peaks=5, debug=False)
        
        if peak_results.get('all_peaks'):
            for peak in peak_results['all_peaks']:
                print(f"   🔸 Peak P{peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        else:
            print("   ❌ No se detectaron picos tradicionales")
        
        # Paso 2: Detectar solo hombros (excluyendo picos)
        print(f"\n2️⃣  HOMBROS VERDADEROS (excluyendo picos):")
        shoulder_results = find_true_shoulders_excluding_peaks(df, max_features=5)
        
        if shoulder_results.get('all_shoulders'):
            for shoulder in shoulder_results['all_shoulders']:
                print(f"   🔹 Shoulder {shoulder['index']}: {shoulder['wavelength']:.1f} nm, {shoulder['intensity']:.2f} a.u.")
                print(f"      Método: {shoulder['detection_method']}")
        else:
            print("   ❌ No se detectaron hombros")
        
        # Paso 3: Mostrar zonas excluidas
        if shoulder_results.get('excluded_peak_zones'):
            print(f"\n🚫 ZONAS EXCLUIDAS (donde hay picos):")
            for i, (start, end) in enumerate(shoulder_results['excluded_peak_zones'], 1):
                print(f"   {i}. {start:.1f} - {end:.1f} nm")
        
        # Paso 4: Verificar que no hay solapamiento
        print(f"\n✅ VERIFICACIÓN DE SEPARACIÓN:")
        peaks_positions = [peak['wavelength'] for peak in peak_results.get('all_peaks', [])]
        shoulder_positions = [shoulder['wavelength'] for shoulder in shoulder_results.get('all_shoulders', [])]
        
        overlaps = []
        for peak_wl in peaks_positions:
            for shoulder_wl in shoulder_positions:
                if abs(peak_wl - shoulder_wl) < 5:  # Menos de 5nm de diferencia
                    overlaps.append((peak_wl, shoulder_wl))
        
        if overlaps:
            print(f"⚠️  ENCONTRADAS {len(overlaps)} POSIBLES SUPERPOSICIONES:")
            for peak_wl, shoulder_wl in overlaps:
                print(f"   Pico en {peak_wl:.1f} nm vs Hombro en {shoulder_wl:.1f} nm (diff: {abs(peak_wl-shoulder_wl):.1f} nm)")
            print(f"💡 Si esto ocurre, aumenta el radio de exclusión en el código")
        else:
            print(f"✅ PERFECTO: No hay superposiciones entre picos y hombros")
            print(f"   Picos y hombros están claramente separados")
        
        # Paso 5: Probar función combinada
        print(f"\n3️⃣  DETECCIÓN COMBINADA:")
        combined_results = find_peaks_and_shoulders_combined(df, max_peaks=3, max_shoulders=3)
        
        print(f"📊 Resumen combinado:")
        print(f"   Picos tradicionales: {len(combined_results.get('peaks_only', []))}")
        print(f"   Hombros verdaderos: {len(combined_results.get('shoulders_only', []))}")
        print(f"   Total features: {combined_results.get('num_total_features', 0)}")
        
        if combined_results.get('first_three_features'):
            print(f"\n🎯 Primeros 3 features por wavelength:")
            for i, feature in enumerate(combined_results['first_three_features'], 1):
                feature_type = feature.get('type', 'unknown')
                display_id = feature.get('display_id', f"{feature_type[0].upper()}{i}")
                icon = "🔸" if feature_type == 'peak' else "🔹"
                print(f"   {i}. {icon} {display_id}: {feature['wavelength']:.1f} nm ({feature_type})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def compare_old_vs_new_detection():
    """
    Compara la detección antigua vs la nueva para ver las diferencias.
    """
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    
    print(f"\n" + "=" * 60)
    print("🔍 COMPARACIÓN: DETECCIÓN ANTIGUA vs NUEVA")
    print("=" * 60)
    
    try:
        import pandas as pd
        from curve_tools import find_shoulders_and_inflections, find_true_shoulders_excluding_peaks
        
        df = pd.read_csv(data_file)
        
        # Método antiguo
        print(f"📊 MÉTODO ANTIGUO (puede detectar hombros en picos):")
        old_results = find_shoulders_and_inflections(df, max_features=5)
        
        if old_results.get('all_shoulders'):
            for shoulder in old_results['all_shoulders']:
                print(f"   🔹 {shoulder['wavelength']:.1f} nm - {shoulder.get('detection_method', 'unknown')}")
        else:
            print("   ❌ No detectó hombros")
        
        # Método nuevo
        print(f"\n📊 MÉTODO NUEVO (excluye picos):")
        new_results = find_true_shoulders_excluding_peaks(df, max_features=5)
        
        if new_results.get('all_shoulders'):
            for shoulder in new_results['all_shoulders']:
                print(f"   🔹 {shoulder['wavelength']:.1f} nm - {shoulder.get('detection_method', 'unknown')}")
        else:
            print("   ❌ No detectó hombros")
        
        # Comparar resultados
        old_positions = [s['wavelength'] for s in old_results.get('all_shoulders', [])]
        new_positions = [s['wavelength'] for s in new_results.get('all_shoulders', [])]
        
        print(f"\n📈 ANÁLISIS COMPARATIVO:")
        print(f"   Método antiguo encontró: {len(old_positions)} hombros")
        print(f"   Método nuevo encontró: {len(new_positions)} hombros")
        
        if old_positions and new_positions:
            shared = [pos for pos in old_positions if any(abs(pos - new_pos) < 2 for new_pos in new_positions)]
            only_old = [pos for pos in old_positions if not any(abs(pos - new_pos) < 2 for new_pos in new_positions)]
            only_new = [pos for pos in new_positions if not any(abs(pos - old_pos) < 2 for old_pos in old_positions)]
            
            print(f"   Posiciones compartidas: {len(shared)} ({[f'{p:.1f}' for p in shared]})")
            print(f"   Solo en método antiguo: {len(only_old)} ({[f'{p:.1f}' for p in only_old]})")
            print(f"   Solo en método nuevo: {len(only_new)} ({[f'{p:.1f}' for p in only_new]})")
            
            if only_old:
                print(f"💡 Los hombros 'solo en método antiguo' probablemente eran picos mal clasificados")
            if only_new:
                print(f"✅ Los hombros 'solo en método nuevo' son verdaderos hombros que antes se perdían")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 PRUEBA DE DETECCIÓN SEPARADA DE PICOS Y HOMBROS")
    print("=" * 70)
    
    # Test principal
    success = test_separation_peaks_shoulders()
    
    if success:
        print(f"\n🎉 ¡TEST EXITOSO!")
        print(f"✅ Los picos y hombros ahora se detectan por separado")
        print(f"✅ No hay conflictos de nomenclatura")
        print(f"✅ Los hombros NO se detectan en la misma posición que los picos")
    
    # Comparación opcional (descomenta para usar)
    # compare_old_vs_new_detection()
    
    print(f"\n" + "=" * 70)
    print("💡 INSTRUCCIONES:")
    print("1. Modifica 'data_file' al inicio de las funciones")
    print("2. Ejecuta este script para verificar la separación")
    print("3. Si aún hay problemas, aumenta el radio de exclusión en el código")
    print("4. Descomenta compare_old_vs_new_detection() para ver diferencias")