import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def normalize_curve(df):
    """Return a normalized copy of a curve."""
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")
    
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least 2 columns (X, Y)")
    
    df_new = df.copy()
    y_values = pd.to_numeric(df_new.iloc[:, 1], errors="coerce")
    
    if np.any(np.isnan(y_values)):
        raise ValueError("Y values contain non-numeric data")
    
    max_value = y_values.max()
    if max_value == 0:
        raise ValueError("Cannot normalize: maximum Y value is zero")
    
    df_new.iloc[:, 1] = y_values / max_value
    return df_new


def add_offset(df, offset):
    """Return a copy of a curve with an offset applied."""
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")
    
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least 2 columns (X, Y)")
    
    df_new = df.copy()
    y_values = pd.to_numeric(df_new.iloc[:, 1], errors="coerce")
    
    if np.any(np.isnan(y_values)):
        raise ValueError("Y values contain non-numeric data")
    
    df_new.iloc[:, 1] = y_values + offset
    return df_new

def subtract_curves(df1, df2, factor):
    """Subtract two curves with a multiplication factor applied to the second curve."""
    try:
        # Validate inputs
        if df1 is None or df2 is None:
            raise ValueError("Both curves must be provided")
        
        if df1.shape[1] < 2 or df2.shape[1] < 2:
            raise ValueError("Both curves must have at least 2 columns (X, Y)")
        
        # Get column names dynamically (first = X, second = Y)
        x_col_1, y_col_1 = df1.columns[0], df1.columns[1]
        x_col_2, y_col_2 = df2.columns[0], df2.columns[1]

        # Convert X to numeric
        x1 = pd.to_numeric(df1[x_col_1], errors="coerce").values
        x2 = pd.to_numeric(df2[x_col_2], errors="coerce").values

        # Remove NaN values
        if np.any(np.isnan(x1)) or np.any(np.isnan(x2)):
            raise ValueError("X values contain non-numeric data")
        
        # Check if curves have the same length
        if len(x1) != len(x2):
            raise ValueError(f"Curves have different lengths: {len(x1)} vs {len(x2)}")

        # Check if X values match within tolerance
        if not np.allclose(x1, x2, rtol=1e-5, atol=1e-8):
            raise ValueError("X values do not match between curves")

        # Convert Y values to numeric
        y1 = pd.to_numeric(df1[y_col_1], errors="coerce")
        y2 = pd.to_numeric(df2[y_col_2], errors="coerce")
        
        if np.any(np.isnan(y1)) or np.any(np.isnan(y2)):
            raise ValueError("Y values contain non-numeric data")

        # Subtract Y values
        result = pd.DataFrame({
            x_col_1: x1,
            y_col_1: y1 - factor * y2
        })
        return result

    except Exception as e:
        raise RuntimeError(f"Subtraction failed: {e}")













def find_shoulders_and_inflections(df, max_features=5, sensitivity=0.1, min_shoulder_prominence=0.02):
    """
    Detecta hombros e inflexiones usando análisis mejorado de derivadas.
    Los hombros son cambios en la pendiente que no forman picos tradicionales.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - max_features: Maximum number of shoulders/inflections to find
    - sensitivity: Sensitivity for detecting changes (0.01-1.0, lower = more sensitive)
    - min_shoulder_prominence: Minimum prominence for a real shoulder (relative to total range)
    
    Returns:
    - dict with shoulder detection results
    """
    try:
        # Extraer datos
        wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
        intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
        
        # Ordenar por longitud de onda
        sort_indices = np.argsort(wavelength)
        wavelength = wavelength[sort_indices]
        intensity = intensity[sort_indices]
        
        # Suavizar ligeramente para reducir ruido en las derivadas
        original_intensity = intensity.copy()
        if len(intensity) >= 7:
            intensity = savgol_filter(intensity, 7, polyorder=3)
        
        # Calcular primera derivada (pendiente)
        first_derivative = np.gradient(intensity, wavelength)
        
        # Calcular segunda derivada (curvatura)
        second_derivative = np.gradient(first_derivative, wavelength)
        
        # Mejorar detección de hombros usando múltiples criterios
        global_range = np.max(intensity) - np.min(intensity)
        min_prominence_abs = min_shoulder_prominence * global_range
        
        shoulder_candidates = []
        
        # Método 1: Buscar PICOS de hombros (máximos locales de intensidad con cambio de curvatura)
        for i in range(3, len(intensity) - 3):
            # Verificar si es un máximo local en INTENSIDAD (esto encuentra el pico del hombro)
            is_local_max = (intensity[i] > intensity[i-1] and 
                           intensity[i] > intensity[i+1] and
                           intensity[i] >= intensity[i-2] and 
                           intensity[i] >= intensity[i+2])
            
            if is_local_max:
                # Verificar que haya cambio de curvatura (característica de hombro)
                left_curvature = np.mean(second_derivative[max(0, i-2):i])
                right_curvature = np.mean(second_derivative[i:min(len(second_derivative), i+3)])
                curvature_change = abs(right_curvature - left_curvature)
                
                # Verificar que la intensidad esté en un rango razonable
                shoulder_intensity = intensity[i]
                min_intensity = np.min(intensity) + sensitivity * global_range
                
                if shoulder_intensity >= min_intensity and curvature_change > min_prominence_abs / 50:
                    # Calcular prominencia del máximo local
                    local_window = 7
                    start_idx = max(0, i - local_window)
                    end_idx = min(len(intensity), i + local_window + 1)
                    
                    local_min = np.min(intensity[start_idx:end_idx])
                    local_prominence = shoulder_intensity - local_min
                    
                    # Solo considerar como hombro si tiene suficiente prominencia
                    if local_prominence > min_prominence_abs * 0.3:  # Más permisivo para hombros
                        shoulder_candidates.append({
                            'wavelength': float(wavelength[i]),
                            'intensity': float(original_intensity[i]),
                            'curvature_change': float(curvature_change),
                            'local_prominence': float(local_prominence),
                            'first_derivative': float(first_derivative[i]),
                            'data_index': int(i),
                            'type': 'shoulder',
                            'detection_method': 'intensity_maximum_with_curvature'
                        })
        
        # Método 2: Buscar cambios significativos en la pendiente
        for i in range(5, len(first_derivative) - 5):
            # Calcular cambio en la pendiente en una ventana
            window = 3
            left_slope = np.mean(first_derivative[i-window:i])
            right_slope = np.mean(first_derivative[i:i+window])
            slope_change = abs(right_slope - left_slope)
            
            # Si hay un cambio significativo en la pendiente
            if slope_change > sensitivity * global_range / 10:
                shoulder_intensity = intensity[i]
                min_intensity = np.min(intensity) + sensitivity * global_range
                
                if shoulder_intensity >= min_intensity:
                    # Verificar que no esté demasiado cerca de un candidato existente
                    too_close = False
                    for existing in shoulder_candidates:
                        if abs(wavelength[i] - existing['wavelength']) < 5:  # Menos de 5nm de distancia
                            too_close = True
                            break
                    
                    if not too_close:
                        shoulder_candidates.append({
                            'wavelength': float(wavelength[i]),
                            'intensity': float(original_intensity[i]),
                            'curvature': float(second_derivative[i]),
                            'first_derivative': float(first_derivative[i]),
                            'slope_change': float(slope_change),
                            'data_index': int(i),
                            'type': 'shoulder',
                            'detection_method': 'slope_change'
                        })
        
        # Filtrar y ordenar candidatos
        # Ordenar por prominencia/intensidad y tomar los mejores
        shoulder_candidates.sort(key=lambda x: x.get('local_prominence', x['intensity']), reverse=True)
        selected_shoulders = shoulder_candidates[:max_features]
        
        # Reordenar por longitud de onda y asignar índices únicos para hombros
        selected_shoulders.sort(key=lambda x: x['wavelength'])
        for i, shoulder in enumerate(selected_shoulders):
            shoulder['index'] = f'S{i + 1}'  # S1, S2, S3... para distinguir de picos P1, P2, P3
        
        results = {
            'num_shoulders_found': len(selected_shoulders),
            'all_shoulders': selected_shoulders,
            'analysis_params': {
                'sensitivity': sensitivity,
                'min_shoulder_prominence': min_shoulder_prominence,
                'smoothing_applied': len(intensity) >= 7,
                'min_prominence_abs': min_prominence_abs
            },
            'debug_info': {
                'total_candidates': len(shoulder_candidates),
                'candidates_before_filtering': len(shoulder_candidates)
            }
        }
        
        return results
        
    except Exception as e:
        return {
            'num_shoulders_found': 0,
            'all_shoulders': [],
            'error': f'Shoulder detection failed: {e}'
        }




def find_shoulder_in_region(df, wavelength_range, sensitivity=0.05):
    """
    Busca específicamente un hombro en una región determinada.
    Útil cuando sabes aproximadamente dónde debería estar el hombro.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - wavelength_range: tuple (min_wl, max_wl) to search for shoulder
    - sensitivity: Lower values = more sensitive detection
    
    Returns:
    - dict with shoulder detection results for the specific region
    """
    try:
        # Extraer datos
        wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
        intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
        
        # Ordenar por longitud de onda
        sort_indices = np.argsort(wavelength)
        wavelength = wavelength[sort_indices]
        intensity = intensity[sort_indices]
        
        # Filtrar región de interés
        mask = (wavelength >= wavelength_range[0]) & (wavelength <= wavelength_range[1])
        region_wl = wavelength[mask]
        region_int = intensity[mask]
        region_indices = np.where(mask)[0]
        
        if len(region_wl) < 5:
            return {'error': f'Not enough data points in range {wavelength_range[0]}-{wavelength_range[1]} nm'}
        
        print(f"🔍 Searching for shoulder in {wavelength_range[0]:.1f}-{wavelength_range[1]:.1f} nm")
        print(f"📊 Region has {len(region_wl)} data points")
        
        # Suavizar datos de la región
        if len(region_int) >= 5:
            smoothed_int = savgol_filter(region_int, min(len(region_int)//2*2-1, 7), polyorder=2)
        else:
            smoothed_int = region_int.copy()
        
        # Calcular derivadas
        first_deriv = np.gradient(smoothed_int, region_wl)
        second_deriv = np.gradient(first_deriv, region_wl)
        
        # Buscar hombros usando múltiples criterios
        shoulder_candidates = []
        
        # Criterio 1: Buscar MÁXIMOS LOCALES de intensidad en la región (picos de hombros)
        for i in range(2, len(region_int) - 2):
            # Verificar si es un máximo local en intensidad
            is_local_max = (region_int[i] > region_int[i-1] and 
                           region_int[i] > region_int[i+1] and
                           region_int[i] >= region_int[i-2] and 
                           region_int[i] >= region_int[i+2])
            
            if is_local_max:
                # Verificar que haya características de hombro (cambio de curvatura)
                if i < len(second_deriv):
                    curvature = second_deriv[i]
                    
                    # Calcular prominencia del máximo local
                    window = min(4, len(region_int)//3)
                    start = max(0, i - window)
                    end = min(len(region_int), i + window + 1)
                    local_min = np.min(region_int[start:end])
                    prominence = region_int[i] - local_min
                    
                    # Verificar cambio de pendiente alrededor del máximo
                    left_slope = np.mean(first_deriv[max(0, i-2):i]) if i >= 2 else first_deriv[i]
                    right_slope = np.mean(first_deriv[i:min(len(first_deriv), i+3)]) if i < len(first_deriv)-2 else first_deriv[i]
                    slope_change = abs(left_slope - right_slope)
                    
                    # Criterio más permisivo para hombros en región específica
                    min_prominence = sensitivity * (np.max(region_int) - np.min(region_int)) * 0.1
                    
                    if prominence > min_prominence:
                        shoulder_candidates.append({
                            'wavelength': float(region_wl[i]),
                            'intensity': float(region_int[i]),
                            'curvature': float(curvature),
                            'prominence': float(prominence),
                            'slope_change': float(slope_change),
                            'first_derivative': float(first_deriv[i]),
                            'detection_method': 'region_intensity_maximum',
                            'confidence': float(prominence * (1 + slope_change))
                        })
        
        # Criterio 2: Cambios en la pendiente
        for i in range(2, len(first_deriv) - 2):
            left_slope = np.mean(first_deriv[max(0, i-2):i])
            right_slope = np.mean(first_deriv[i:min(len(first_deriv), i+2)])
            slope_change = abs(right_slope - left_slope)
            
            if slope_change > sensitivity * (np.max(region_int) - np.min(region_int)):
                # Evitar duplicados
                too_close = any(abs(region_wl[i] - existing['wavelength']) < 2 
                               for existing in shoulder_candidates)
                
                if not too_close:
                    shoulder_candidates.append({
                        'wavelength': float(region_wl[i]),
                        'intensity': float(region_int[i]),
                        'slope_change': float(slope_change),
                        'first_derivative': float(first_deriv[i]),
                        'detection_method': 'region_slope_change',
                        'confidence': float(slope_change)
                    })
        
        # Ordenar por confianza y tomar el mejor
        shoulder_candidates.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        results = {
            'region_searched': wavelength_range,
            'num_candidates': len(shoulder_candidates),
            'best_shoulder': shoulder_candidates[0] if shoulder_candidates else None,
            'all_candidates': shoulder_candidates,
            'analysis_params': {
                'sensitivity': sensitivity,
                'data_points_in_region': len(region_wl)
            }
        }
        
        if results['best_shoulder']:
            print(f"✅ Best shoulder candidate found:")
            best = results['best_shoulder']
            print(f"   🔹 {best['wavelength']:.1f} nm, intensity: {best['intensity']:.2f}")
            print(f"   Method: {best['detection_method']}, confidence: {best.get('confidence', 0):.2e}")
        else:
            print(f"❌ No shoulder candidates found in region")
            print(f"💡 Try increasing sensitivity (current: {sensitivity})")
        
        return results
        
    except Exception as e:
        return {'error': f'Shoulder region search failed: {e}'}


def find_extreme_shoulders(df, max_features=5):
    """
    MÉTODO EXTREMO: Detecta prácticamente cualquier variación como hombro.
    Usa este método solo cuando todos los otros fallen.
    """
    try:
        # Extraer datos
        wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
        intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
        
        # Ordenar por longitud de onda
        sort_indices = np.argsort(wavelength)
        wavelength = wavelength[sort_indices]
        intensity = intensity[sort_indices]
        
        print("🚨 Ejecutando detección EXTREMA de hombros...")
        
        shoulder_candidates = []
        global_range = np.max(intensity) - np.min(intensity)
        
        # Detectar CUALQUIER máximo local mínimo
        for i in range(2, len(intensity) - 2):
            # Condición ultra permisiva para máximo local
            if (intensity[i] >= intensity[i-1] and 
                intensity[i] >= intensity[i+1]):
                
                    # Altura mínima más robusta
                    min_intensity = np.min(intensity) + 0.05 * global_range
                    
                    if intensity[i] >= min_intensity:
                        # Prominencia más robusta
                        local_window = 5
                        start_idx = max(0, i - local_window)
                        end_idx = min(len(intensity), i + local_window + 1)
                        local_min = np.min(intensity[start_idx:end_idx])
                        prominence = intensity[i] - local_min
                        
                        if prominence > 0.02 * global_range:
                            # Verificar que no esté muy cerca de otros candidatos
                            too_close = any(abs(wavelength[i] - existing['wavelength']) < 3 
                                          for existing in shoulder_candidates)
                            
                            if not too_close:
                                shoulder_candidates.append({
                                    'wavelength': float(wavelength[i]),
                                    'intensity': float(intensity[i]),
                                    'prominence': float(prominence),
                                    'data_index': int(i),
                                    'type': 'extreme_shoulder',
                                    'detection_method': 'extreme_any_local_max'
                                })
        
        # Seleccionar los mejores
        shoulder_candidates.sort(key=lambda x: x['prominence'], reverse=True)
        selected_shoulders = shoulder_candidates[:max_features]
        
        # Ordenar por wavelength y asignar IDs
        selected_shoulders.sort(key=lambda x: x['wavelength'])
        for i, shoulder in enumerate(selected_shoulders):
            shoulder['index'] = f'ES{i + 1}'  # Extreme Shoulder
        
        print(f"🚨 Detección extrema encontró {len(selected_shoulders)} candidatos")
        
        return {
            'num_shoulders_found': len(selected_shoulders),
            'all_shoulders': selected_shoulders
        }
        
    except Exception as e:
        return {
            'num_shoulders_found': 0,
            'all_shoulders': [],
            'error': f'Extreme shoulder detection failed: {e}'
        }




def diagnose_missing_peak(df, wavelength_range, debug=True):
    """
    Diagnose why a peak might not be detected in a specific wavelength range.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - wavelength_range: tuple (min_wl, max_wl) to analyze
    - debug: Print diagnostic information
    
    Returns:
    - dict with diagnostic information and suggested parameters
    """
    # Extract data
    wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
    intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
    
    # Sort by wavelength
    sort_indices = np.argsort(wavelength)
    wavelength = wavelength[sort_indices]
    intensity = intensity[sort_indices]
    
    # Find data in the specified range
    mask = (wavelength >= wavelength_range[0]) & (wavelength <= wavelength_range[1])
    region_wl = wavelength[mask]
    region_int = intensity[mask]
    
    if len(region_wl) == 0:
        return {'error': f'No data points in range {wavelength_range[0]}-{wavelength_range[1]} nm'}
    
    # Analyze the region
    max_int_in_region = np.max(region_int)
    min_int_in_region = np.min(region_int)
    mean_int_in_region = np.mean(region_int)
    
    # Global statistics
    global_max = np.max(intensity)
    global_min = np.min(intensity)
    global_range = global_max - global_min
    
    # Calculate what the detection thresholds would be
    q05 = float(np.quantile(intensity, 0.05))
    current_min_height = q05 + 0.005 * global_range
    
    # Prominence analysis
    relative_prominence = (max_int_in_region - min_int_in_region) / global_range
    abs_prominence_needed = 0.003 * global_range
    
    diagnosis = {
        'region_analysis': {
            'wavelength_range': wavelength_range,
            'data_points': len(region_wl),
            'max_intensity': max_int_in_region,
            'min_intensity': min_int_in_region,
            'mean_intensity': mean_int_in_region,
            'intensity_range': max_int_in_region - min_int_in_region
        },
        'global_context': {
            'global_max': global_max,
            'global_min': global_min,
            'global_range': global_range
        },
        'detection_thresholds': {
            'current_min_height': current_min_height,
            'height_met': max_int_in_region >= current_min_height,
            'relative_prominence': relative_prominence,
            'prominence_threshold': 0.003,
            'prominence_met': relative_prominence >= 0.003
        },
        'suggested_params': {
            'custom_min_height': min_int_in_region + 0.001 * global_range,
            'custom_prominence': max(0.0001, relative_prominence * 0.5),
            'needs_ultra_sensitive': max_int_in_region < current_min_height or relative_prominence < 0.001
        }
    }
    
    if debug:
        print(f"\n🔍 DIAGNÓSTICO PARA REGIÓN {wavelength_range[0]}-{wavelength_range[1]} nm")
        print(f"📊 Puntos de datos: {len(region_wl)}")
        print(f"📈 Intensidad máxima en región: {max_int_in_region:.2f}")
        print(f"📉 Intensidad mínima en región: {min_int_in_region:.2f}")
        print(f"🎯 Umbral actual de altura: {current_min_height:.2f}")
        print(f"✅ Altura suficiente: {'SÍ' if diagnosis['detection_thresholds']['height_met'] else 'NO'}")
        print(f"📏 Prominencia relativa: {relative_prominence:.6f}")
        print(f"✅ Prominencia suficiente: {'SÍ' if diagnosis['detection_thresholds']['prominence_met'] else 'NO'}")
        
        if diagnosis['suggested_params']['needs_ultra_sensitive']:
            print(f"⚠️  REQUIERE DETECCIÓN ULTRA-SENSIBLE")
            print(f"💡 Altura mínima sugerida: {diagnosis['suggested_params']['custom_min_height']:.4f}")
            print(f"💡 Prominencia sugerida: {diagnosis['suggested_params']['custom_prominence']:.6f}")
    
    return diagnosis




def calculate_peak_statistics(peak_results):
    """
    Calculate additional statistics from peak analysis results.
    
    Parameters:
    - peak_results: Results dictionary from find_fluorescence_peaks()
    
    Returns:
    - dict with additional peak statistics
    """
    if not peak_results or not peak_results.get('all_peaks'):
        return {'error': 'No peaks found for statistical analysis'}
    
    peaks = peak_results['all_peaks']
    intensities = [p['intensity'] for p in peaks]
    wavelengths = [p['wavelength'] for p in peaks]
    
    stats = {
        'total_peaks': len(peaks),
        'intensity_stats': {
            'max': float(np.max(intensities)),
            'min': float(np.min(intensities)),
            'mean': float(np.mean(intensities)),
            'std': float(np.std(intensities))
        },
        'wavelength_stats': {
            'range_nm': float(np.max(wavelengths) - np.min(wavelengths)),
            'mean_wavelength': float(np.mean(wavelengths))
        }
    }
    
    # Calculate first to third peak ratio if both exist
    if peak_results.get('first_peak') and peak_results.get('third_peak'):
        first_intensity = peak_results['first_peak']['intensity']
        third_intensity = peak_results['third_peak']['intensity']
        stats['first_to_third_ratio'] = float(first_intensity / third_intensity)
        stats['wavelength_separation'] = float(
            peak_results['third_peak']['wavelength'] - peak_results['first_peak']['wavelength']
        )
    
    return stats