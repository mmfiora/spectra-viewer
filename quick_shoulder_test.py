#!/usr/bin/env python3
"""
Script rápido para buscar un hombro en una región específica.
Útil cuando sabes aproximadamente dónde debería estar el hombro.
"""

def test_shoulder_in_specific_region():
    """
    Busca un hombro en una región específica de tus datos.
    MODIFICA LAS VARIABLES ABAJO PARA TUS DATOS.
    """
    
    # ===== CONFIGURA AQUÍ TUS DATOS =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    shoulder_region = (365, 375)   # <<<< CAMBIAR ESTO: rango donde esperas el hombro
    sensitivity = 0.05             # <<<< CAMBIAR SI NECESARIO: menor = más sensible
    
    print("🔍 BÚSQUEDA ESPECÍFICA DE HOMBRO")
    print("=" * 40)
    print(f"📁 Archivo: {data_file}")
    print(f"🎯 Región de búsqueda: {shoulder_region[0]}-{shoulder_region[1]} nm")
    print(f"🔧 Sensibilidad: {sensitivity}")
    
    try:
        import pandas as pd
        from curve_tools import find_shoulder_in_region
        
        # Intentar cargar datos
        try:
            df = pd.read_csv(data_file)
            print(f"✅ Datos cargados: {len(df)} puntos")
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {data_file}")
            print("💡 Para usar este script:")
            print("   1. Modifica 'data_file' con la ruta a tu archivo CSV")
            print("   2. Modifica 'shoulder_region' con el rango donde esperas el hombro")
            print("   3. Ajusta 'sensitivity' si es necesario (0.01-0.5)")
            return False
        
        # Buscar hombro en la región específica
        print(f"\n🔍 Buscando hombro en región específica...")
        
        results = find_shoulder_in_region(df, shoulder_region, sensitivity=sensitivity)
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return False
        
        print(f"\n📊 Resultados:")
        print(f"   Candidatos encontrados: {results['num_candidates']}")
        
        if results['best_shoulder']:
            best = results['best_shoulder']
            print(f"\n✅ MEJOR CANDIDATO A HOMBRO:")
            print(f"   🔹 Posición: {best['wavelength']:.1f} nm")
            print(f"   📈 Intensidad: {best['intensity']:.2f} a.u.")
            print(f"   🔧 Método: {best['detection_method']}")
            
            if 'curvature' in best:
                print(f"   📏 Curvatura: {best['curvature']:.2e}")
            if 'prominence' in best:
                print(f"   🎯 Prominencia: {best['prominence']:.2f}")
            if 'slope_change' in best:
                print(f"   📐 Cambio de pendiente: {best['slope_change']:.2e}")
        
        if results['num_candidates'] > 1:
            print(f"\n📋 Otros candidatos:")
            for i, candidate in enumerate(results['all_candidates'][1:], 2):
                print(f"   {i}. {candidate['wavelength']:.1f} nm - {candidate['detection_method']}")
        
        return results['best_shoulder'] is not None
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Este script requiere pandas y las funciones de curve_tools.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_multiple_sensitivities():
    """
    Prueba diferentes niveles de sensibilidad para encontrar el hombro.
    """
    # ===== CONFIGURA AQUÍ TUS DATOS =====
    data_file = "tu_archivo.csv"  # <<<< CAMBIAR ESTO
    shoulder_region = (365, 375)   # <<<< CAMBIAR ESTO
    
    print("\n" + "=" * 50)
    print("🧪 PRUEBA MÚLTIPLES SENSIBILIDADES")
    print("=" * 50)
    
    try:
        import pandas as pd
        from curve_tools import find_shoulder_in_region
        
        df = pd.read_csv(data_file)
        sensitivities = [0.01, 0.03, 0.05, 0.1, 0.2]
        
        print(f"Probando sensibilidades: {sensitivities}")
        
        for sens in sensitivities:
            print(f"\n--- Sensibilidad {sens} ---")
            results = find_shoulder_in_region(df, shoulder_region, sensitivity=sens)
            
            if results.get('best_shoulder'):
                best = results['best_shoulder']
                print(f"✅ Encontrado: {best['wavelength']:.1f} nm, {best['detection_method']}")
            else:
                print(f"❌ No encontrado con sensibilidad {sens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 HERRAMIENTA DE BÚSQUEDA ESPECÍFICA DE HOMBROS")
    print("=" * 60)
    
    # Test principal
    success = test_shoulder_in_specific_region()
    
    if not success:
        print(f"\n💡 INSTRUCCIONES DE USO:")
        print("1. Edita las variables al inicio de test_shoulder_in_specific_region():")
        print("   - data_file: ruta a tu archivo CSV")
        print("   - shoulder_region: rango (min_nm, max_nm) donde esperas el hombro")
        print("   - sensitivity: 0.01-0.5 (menor = más sensible)")
        print("")
        print("2. Si no encuentra nada, descomenta test_multiple_sensitivities()")
        print("   para probar diferentes niveles de sensibilidad")
    
    # Descomenta la siguiente línea para probar múltiples sensibilidades:
    # test_multiple_sensitivities()
    
    print(f"\n" + "=" * 60)
    print("💡 CONSEJOS:")
    print("• Si encuentra hombros falsos, AUMENTA la sensibilidad (ej: 0.1)")
    print("• Si no encuentra nada, DISMINUYE la sensibilidad (ej: 0.01)")
    print("• El hombro debe estar en una región con cambio de curvatura visible")
    print("• Usa un rango pequeño (5-10 nm) para mejor precisión")