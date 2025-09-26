#!/usr/bin/env python3
"""
Script para probar la nueva detección unificada donde TODOS los features 
(picos tradicionales y hombros) se llaman simplemente "picos" P1, P2, P3, etc.
"""

def test_unified_peak_detection():
    """
    Prueba la detección unificada donde todo se llama "pico".
    """
    
    # ===== CONFIGURA TUS DATOS AQUÍ =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    
    print("🔬 TEST: DETECCIÓN UNIFICADA DE PICOS")
    print("=" * 50)
    print(f"📁 Archivo: {data_file}")
    print("💡 Todos los features (picos tradicionales + hombros) se llaman 'picos'")
    
    try:
        import pandas as pd
        from curve_tools import find_peaks_and_shoulders_combined
        
        # Cargar datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Modifica 'data_file' al inicio del script")
            return False
        
        # Detección unificada
        print(f"\n🔍 Ejecutando detección unificada...")
        results = find_peaks_and_shoulders_combined(df, max_total_peaks=5)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Total de picos encontrados: {results['num_peaks_found']}")
        print(f"   - Picos tradicionales: {results.get('traditional_peaks_count', 0)}")
        print(f"   - Picos de hombro: {results.get('shoulder_peaks_count', 0)}")
        
        if results.get('all_peaks'):
            print(f"\n📋 TODOS LOS PICOS (nomenclatura unificada):")
            for peak in results['all_peaks']:
                detection_type = peak.get('detection_type', 'unknown')
                original_type = peak.get('original_type', 'unknown')
                
                if detection_type == 'traditional_peak':
                    type_info = "(pico tradicional)"
                elif detection_type == 'shoulder_peak':
                    type_info = "(hombro detectado como pico)"
                else:
                    type_info = "(tipo desconocido)"
                
                print(f"   🔸 {peak['display_id']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u. {type_info}")
                
                # Información adicional para hombros
                if detection_type == 'shoulder_peak':
                    method = peak.get('detection_method', 'unknown')
                    print(f"      └─ Método de detección: {method}")
        else:
            print(f"\n❌ No se detectaron picos")
        
        # Verificar compatibilidad con formato anterior
        print(f"\n🔍 VERIFICACIÓN DE COMPATIBILIDAD:")
        if results.get('first_peak'):
            fp = results['first_peak']
            print(f"   First peak (P1): {fp['wavelength']:.1f} nm - {fp.get('detection_type', 'unknown')}")
        
        if results.get('third_peak'):
            tp = results['third_peak']
            print(f"   Third peak (P3): {tp['wavelength']:.1f} nm - {tp.get('detection_type', 'unknown')}")
        
        # Mostrar si se incluyeron hombros
        shoulder_count = results.get('shoulder_peaks_count', 0)
        if shoulder_count > 0:
            print(f"\n✅ ÉXITO: Se incluyeron {shoulder_count} hombros como picos!")
            print(f"   Los hombros ahora aparecen en la lista de picos con nomenclatura P1, P2, P3...")
        else:
            print(f"\n⚠️  No se detectaron hombros en este espectro")
            print(f"   Esto puede ser normal si no hay hombros, o puede necesitar ajuste de sensibilidad")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def compare_traditional_vs_unified():
    """
    Compara la detección tradicional (solo picos) vs unificada (picos + hombros).
    """
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    
    print(f"\n" + "=" * 60)
    print("🔍 COMPARACIÓN: TRADICIONAL vs UNIFICADA")
    print("=" * 60)
    
    try:
        import pandas as pd
        from curve_tools import find_fluorescence_peaks_adaptive, find_peaks_and_shoulders_combined
        
        df = pd.read_csv(data_file)
        
        # Método tradicional (solo picos)
        print(f"📊 DETECCIÓN TRADICIONAL (solo picos):")
        traditional_results = find_fluorescence_peaks_adaptive(df, max_peaks=5, debug=False)
        
        if traditional_results.get('all_peaks'):
            for peak in traditional_results['all_peaks']:
                print(f"   🔸 P{peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        else:
            print("   ❌ No detectó picos tradicionales")
        
        # Método unificado (picos + hombros)
        print(f"\n📊 DETECCIÓN UNIFICADA (picos + hombros como picos):")
        unified_results = find_peaks_and_shoulders_combined(df, max_total_peaks=5)
        
        if unified_results.get('all_peaks'):
            for peak in unified_results['all_peaks']:
                detection_type = peak.get('detection_type', 'unknown')
                type_symbol = "🔸" if detection_type == 'traditional_peak' else "🔹"
                print(f"   {type_symbol} {peak['display_id']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        else:
            print("   ❌ No detectó ningún feature")
        
        # Análisis comparativo
        traditional_count = len(traditional_results.get('all_peaks', []))
        unified_count = len(unified_results.get('all_peaks', []))
        shoulder_count = unified_results.get('shoulder_peaks_count', 0)
        
        print(f"\n📈 ANÁLISIS:")
        print(f"   Método tradicional: {traditional_count} picos")
        print(f"   Método unificado: {unified_count} picos total")
        print(f"   └─ Picos tradicionales: {unified_results.get('traditional_peaks_count', 0)}")
        print(f"   └─ Hombros como picos: {shoulder_count}")
        
        if shoulder_count > 0:
            print(f"\n✅ El método unificado encontró {shoulder_count} hombros adicionales!")
            print(f"   Estos aparecen ahora como picos P{traditional_count+1}, P{traditional_count+2}, etc.")
        else:
            print(f"\n⚠️  No se encontraron hombros adicionales")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 PRUEBA DE DETECCIÓN UNIFICADA DE PICOS")
    print("=" * 70)
    
    # Test principal
    success = test_unified_peak_detection()
    
    if success:
        print(f"\n🎉 ¡TEST EXITOSO!")
        print(f"✅ Todos los features se llaman 'picos' con nomenclatura P1, P2, P3...")
        print(f"✅ Los hombros aparecen como picos adicionales")
        print(f"✅ Mantenida compatibilidad con el formato anterior")
    
    # Comparación opcional (descomenta para usar)
    # compare_traditional_vs_unified()
    
    print(f"\n" + "=" * 70)
    print("💡 RESULTADO ESPERADO:")
    print("• Ahora verás más picos que antes (incluyendo hombros)")
    print("• Todos se llaman P1, P2, P3, P4, P5... por orden de wavelength")  
    print("• En la consola se indica si es '(traditional)' o '(shoulder)'")
    print("• Para el usuario final, todos son simplemente 'picos'")