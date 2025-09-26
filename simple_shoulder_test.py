#!/usr/bin/env python3
"""
Script simple para probar que la detección funciona paso a paso.
"""

def test_basic_detection():
    """Prueba detección básica paso a paso."""
    
    print("🔬 TEST BÁSICO DE DETECCIÓN")
    print("=" * 40)
    
    try:
        import pandas as pd
        from curve_tools import (find_fluorescence_peaks_adaptive,
                                find_peaks_and_shoulders_combined)
        
        # Usar datos de prueba
        data_file = "test_shoulder_data.csv"
        
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
            print(f"   Rango wavelength: {df['Wavelength'].min():.1f} - {df['Wavelength'].max():.1f} nm")
            print(f"   Rango intensidad: {df['Intensity'].min():.1f} - {df['Intensity'].max():.1f}")
        except FileNotFoundError:
            print(f"❌ No se encontró {data_file}")
            return False
        
        # Paso 1: Solo picos tradicionales
        print(f"\n1️⃣  DETECCIÓN TRADICIONAL:")
        traditional_results = find_fluorescence_peaks_adaptive(df, max_peaks=5, debug=False)
        
        print(f"   Picos encontrados: {traditional_results['num_peaks_found']}")
        if traditional_results.get('all_peaks'):
            for peak in traditional_results['all_peaks']:
                print(f"   🔸 P{peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
        
        # Paso 2: Detección combinada balanceada
        print(f"\n2️⃣  DETECCIÓN COMBINADA (balanceada):")
        combined_results = find_peaks_and_shoulders_combined(df, max_total_peaks=5)
        
        print(f"   Total picos: {combined_results['num_peaks_found']}")
        print(f"   - Tradicionales: {combined_results.get('traditional_peaks_count', 0)}")
        print(f"   - Hombros: {combined_results.get('shoulder_peaks_count', 0)}")
        
        if combined_results.get('all_peaks'):
            print(f"\n📋 Lista de picos unificada:")
            for peak in combined_results['all_peaks']:
                detection_type = peak.get('detection_type', 'unknown')
                type_indicator = "(trad)" if detection_type == 'traditional_peak' else "(hombro)"
                print(f"   🔸 {peak['display_id']}: {peak['wavelength']:.1f} nm {type_indicator}")
        
        # Verificar si mejoró
        traditional_count = traditional_results['num_peaks_found']
        combined_count = combined_results['num_peaks_found']
        
        print(f"\n📊 COMPARACIÓN:")
        print(f"   Solo tradicional: {traditional_count} picos")
        print(f"   Combinado: {combined_count} picos")
        
        if combined_count > traditional_count:
            print(f"✅ ¡Mejoró! Se encontraron {combined_count - traditional_count} features adicionales")
            return True
        elif combined_count == traditional_count:
            print(f"⚠️  Mismo número de picos (no se encontraron hombros)")
            return False
        else:
            print(f"❌ Problema: se perdieron picos")
            return False
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 PRUEBA SIMPLE DE DETECCIÓN")
    print("=" * 50)
    
    success = test_basic_detection()
    
    if success:
        print(f"\n🎉 ¡DETECCIÓN FUNCIONANDO!")
        print(f"✅ Se detectaron features adicionales (hombros)")
    else:
        print(f"\n⚠️  La detección necesita más ajuste")
        print(f"💡 Puede que los criterios sean muy restrictivos")
    
    print(f"\n" + "=" * 50)
    print("💡 PRÓXIMOS PASOS:")
    print("1. Si funciona: usar en el visor principal")
    print("2. Si no: ajustar sensibilidad en curve_tools.py")
    print("3. Revisar que no detecte ruido en datos reales")