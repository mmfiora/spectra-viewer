import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter


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


def find_fluorescence_peaks(df, max_peaks=3, min_height=None, min_distance=2, 
                          prominence=0.003, smooth=False, window_length=3):
    """
    Find the first 3 peaks in fluorescence spectra ordered by wavelength.
    Uses balanced sensitivity to detect real peaks while avoiding noise.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - max_peaks: Maximum number of peaks to return (default: 3)
    - min_height: Minimum peak height (auto-calculated if None)
    - min_distance: Minimum distance between peaks in data points (balanced for real peaks)
    - prominence: Minimum prominence for peak detection (balanced to avoid noise)
    - smooth: Apply Savitzky-Golay smoothing (disabled by default to preserve small peaks)
    - window_length: Window length for smoothing filter (must be odd)
    
    Returns:
    - dict with peak analysis results containing exactly the first 3 peaks by wavelength
    """
    # Input validation
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")
    
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least 2 columns (wavelength, intensity)")
    
    if df.shape[0] < 10:
        raise ValueError("Not enough data points for peak analysis (minimum 10 required)")
    
    # Extract wavelength and intensity data
    wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
    intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
    
    # Check for NaN values
    if np.any(np.isnan(wavelength)) or np.any(np.isnan(intensity)):
        raise ValueError("Data contains non-numeric values")
    
    # Ensure data is sorted by wavelength
    sort_indices = np.argsort(wavelength)
    wavelength = wavelength[sort_indices]
    intensity = intensity[sort_indices]
    
    # Apply smoothing to reduce noise if requested
    if smooth and len(intensity) >= window_length:
        try:
            # Ensure window_length is odd and valid
            if window_length % 2 == 0:
                window_length += 1
            window_length = min(window_length, len(intensity) // 2)
            if window_length >= 3:
                intensity = savgol_filter(intensity, window_length, polyorder=2)
        except Exception:
            # If smoothing fails, continue with original data
            pass
    
    # Calculate automatic parameters if not provided
    max_intensity = np.max(intensity)
    min_intensity = np.min(intensity)
    intensity_range = max_intensity - min_intensity
    
    if min_height is None:
        # Umbral más permisivo para detectar picos pequeños
        q05 = float(np.quantile(intensity, 0.05))
        min_height = q05 + 0.005 * intensity_range
    
    # Calculate absolute prominence from relative value (balanced for real peaks)
#    abs_prominence = max(prominence * max_intensity, 2.0)
    abs_prominence = max(prominence * (max_intensity - min_intensity), 1e-6)
    wlen = max(11, min(len(intensity)//6, 61))

    # Find peaks using scipy
    try:
        peaks, properties = find_peaks(
            intensity,
            height=min_height,
            distance=max(1, int(min_distance)),
            prominence=(abs_prominence, None),
            width=(1, None),  # Minimum width of 2 points to reject noise spikes,
            plateau_size=(1, None),
            wlen=wlen
        )
    except Exception as e:
        raise RuntimeError(f"Peak detection failed: {e}")
    
    # Prepare results
    results = {
        'num_peaks_found': len(peaks),
        'all_peaks': [],
        'first_peak': None,
        'third_peak': None,
        'analysis_params': {
            'min_height': min_height,
            'min_distance': min_distance,
            'prominence_abs': abs_prominence,
            'smoothed': smooth
        }
    }
    
    # Process detected peaks and limit to first 3 by wavelength
    if len(peaks) > 0:
        peak_intensities = intensity[peaks]
        peak_wavelengths = wavelength[peaks]
        
        # Create list of all candidate peaks
        peak_candidates = []
        for peak_idx, peak_int, peak_wl in zip(peaks, peak_intensities, peak_wavelengths):
            peak_candidates.append({
                'wavelength': float(peak_wl),
                'intensity': float(peak_int),
                'data_index': int(peak_idx)
            })
        
        # Sort by wavelength (left to right on spectrum)
        peak_candidates.sort(key=lambda x: x['wavelength'])
        
        # Take only the first 3 peaks by wavelength
        selected_peaks = peak_candidates[:max_peaks]
        
        # Assign final indices (1, 2, 3)
        for i, peak in enumerate(selected_peaks):
            peak['index'] = i + 1
        
        results['all_peaks'] = selected_peaks
        results['num_peaks_found'] = len(selected_peaks)
        
        # Extract Peak 1 (first by wavelength)
        if len(results['all_peaks']) >= 1:
            results['first_peak'] = {
                'wavelength': results['all_peaks'][0]['wavelength'],
                'intensity': results['all_peaks'][0]['intensity'],
                'position': 'peak_1'
            }
        
        # Extract Peak 3 (third by wavelength)
        if len(results['all_peaks']) >= 3:
            results['third_peak'] = {
                'wavelength': results['all_peaks'][2]['wavelength'],
                'intensity': results['all_peaks'][2]['intensity'],
                'position': 'peak_3'
            }
    
    # Add debug information
    results['debug_info'] = {
        'total_data_points': len(intensity),
        'wavelength_range': f"{wavelength.min():.1f} - {wavelength.max():.1f} nm",
        'intensity_range': f"{min_intensity:.2f} - {max_intensity:.2f}",
        'detection_params': {
            'min_height_used': min_height,
            'prominence_used': abs_prominence,
            'min_distance_used': min_distance
        }
    }
    
    return results


def find_fluorescence_peaks_sensitive(df, max_peaks=3):
    """
    Alternative function with more sensitive parameters for difficult cases.
    Use this when the standard function misses weak peaks.
    
    Returns:
    - dict with peak analysis results containing exactly the first 3 peaks by wavelength
    """
    return find_fluorescence_peaks(
        df, 
        max_peaks=max_peaks,
        min_height=None,  # Auto-calculated
        min_distance=1,   # Closer peaks allowed
        prominence=0.0001, # Ultra sensitive for small peaks
        smooth=False,     # No smoothing
        window_length=5
    )


def find_fluorescence_peaks_ultra_sensitive(df, max_peaks=3):
    """
    Ultra-sensitive peak detection for very weak peaks.
    Use this when even the sensitive function misses peaks.
    
    Returns:
    - dict with peak analysis results containing exactly the first 3 peaks by wavelength
    """
    return find_fluorescence_peaks(
        df, 
        max_peaks=max_peaks,
        min_height=None,  # Auto-calculated with very low threshold
        min_distance=1,   # Allow very close peaks
        prominence=0.00001, # Extremely sensitive
        smooth=False,     # No smoothing to preserve weak signals
        window_length=3
    )


def find_fluorescence_peaks_force_detect(df, max_peaks=3):
    """
    ÚLTIMO RECURSO: Detección forzada con parámetros extremadamente permisivos.
    Usa esto cuando todos los otros métodos fallen.
    ADVERTENCIA: Puede detectar ruido como picos.
    
    Returns:
    - dict with peak analysis results containing exactly the first 3 peaks by wavelength
    """
    # Extraer datos
    wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce").values
    intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce").values
    
    # Ordenar por longitud de onda
    sort_indices = np.argsort(wavelength)
    wavelength = wavelength[sort_indices]
    intensity = intensity[sort_indices]
    
    # Parámetros ultra permisivos
    global_range = np.max(intensity) - np.min(intensity)
    min_height_force = np.min(intensity) + 0.0001 * global_range  # Casi cualquier cosa por encima del mínimo
    prominence_force = 0.000001  # Prácticamente cualquier variación
    
    try:
        peaks, properties = find_peaks(
            intensity,
            height=min_height_force,
            distance=1,  # Picos pueden estar muy cerca
            prominence=(prominence_force, None),
            width=(1, None)  # Mínimo ancho de 1 punto
        )
        
        # Preparar resultados
        results = {
            'num_peaks_found': len(peaks),
            'all_peaks': [],
            'first_peak': None,
            'third_peak': None,
            'warning': 'DETECCIÓN FORZADA - Puede incluir ruido como picos',
            'analysis_params': {
                'min_height': min_height_force,
                'prominence_abs': prominence_force,
                'method': 'force_detect'
            }
        }
        
        if len(peaks) > 0:
            peak_intensities = intensity[peaks]
            peak_wavelengths = wavelength[peaks]
            
            # Crear lista de candidatos
            peak_candidates = []
            for peak_idx, peak_int, peak_wl in zip(peaks, peak_intensities, peak_wavelengths):
                peak_candidates.append({
                    'wavelength': float(peak_wl),
                    'intensity': float(peak_int),
                    'data_index': int(peak_idx)
                })
            
            # Ordenar por longitud de onda
            peak_candidates.sort(key=lambda x: x['wavelength'])
            
            # Tomar solo los primeros max_peaks
            selected_peaks = peak_candidates[:max_peaks]
            
            # Asignar índices
            for i, peak in enumerate(selected_peaks):
                peak['index'] = i + 1
            
            results['all_peaks'] = selected_peaks
            results['num_peaks_found'] = len(selected_peaks)
            
            # Extraer Peak 1 y Peak 3
            if len(results['all_peaks']) >= 1:
                results['first_peak'] = {
                    'wavelength': results['all_peaks'][0]['wavelength'],
                    'intensity': results['all_peaks'][0]['intensity'],
                    'position': 'peak_1'
                }
            
            if len(results['all_peaks']) >= 3:
                results['third_peak'] = {
                    'wavelength': results['all_peaks'][2]['wavelength'],
                    'intensity': results['all_peaks'][2]['intensity'],
                    'position': 'peak_3'
                }
        
        return results
        
    except Exception as e:
        return {
            'num_peaks_found': 0,
            'all_peaks': [],
            'error': f'Even forced detection failed: {e}'
        }


def find_fluorescence_peaks_adaptive(df, max_peaks=3, debug=False):
    """
    Adaptive peak detection that automatically tries more sensitive parameters
    if not enough peaks are found with standard settings.
    
    Returns:
    - dict with peak analysis results containing exactly the first 3 peaks by wavelength
    """
    if debug:
        print(f"🔍 Starting adaptive peak detection (target: {max_peaks} peaks)")
    
    # Try standard detection first
    results = find_fluorescence_peaks(df, max_peaks=max_peaks)
    if debug:
        print(f"📊 Standard detection: {results['num_peaks_found']} peaks found")
    
    # If we found fewer than expected peaks, try more sensitive detection
    if results['num_peaks_found'] < max_peaks:
        if debug:
            print(f"⚠️  Only found {results['num_peaks_found']} peaks, trying sensitive detection...")
        sensitive_results = find_fluorescence_peaks_sensitive(df, max_peaks=max_peaks)
        
        if debug:
            print(f"📊 Sensitive detection: {sensitive_results['num_peaks_found']} peaks found")
        
        # Use sensitive results if they found more peaks
        if sensitive_results['num_peaks_found'] > results['num_peaks_found']:
            if debug:
                print(f"✅ Using sensitive results ({sensitive_results['num_peaks_found']} peaks)")
            results = sensitive_results
        
        # If still not enough, try ultra-sensitive
        if results['num_peaks_found'] < max_peaks:
            if debug:
                print(f"⚠️  Still only {results['num_peaks_found']} peaks, trying ultra-sensitive detection...")
            ultra_results = find_fluorescence_peaks_ultra_sensitive(df, max_peaks=max_peaks)
            
            if debug:
                print(f"📊 Ultra-sensitive detection: {ultra_results['num_peaks_found']} peaks found")
            
            if ultra_results['num_peaks_found'] > results['num_peaks_found']:
                if debug:
                    print(f"✅ Using ultra-sensitive results ({ultra_results['num_peaks_found']} peaks)")
                results = ultra_results
            
            # ÚLTIMO RECURSO: Detección forzada
            if results['num_peaks_found'] < max_peaks:
                if debug:
                    print(f"🚨 ÚLTIMO RECURSO: Still only {results['num_peaks_found']} peaks, trying forced detection...")
                    print(f"⚠️  WARNING: This may detect noise as peaks!")
                
                force_results = find_fluorescence_peaks_force_detect(df, max_peaks=max_peaks)
                
                if debug:
                    print(f"📊 Forced detection: {force_results['num_peaks_found']} peaks found")
                
                if force_results['num_peaks_found'] > results['num_peaks_found']:
                    if debug:
                        print(f"🔶 Using forced detection results ({force_results['num_peaks_found']} peaks)")
                        print(f"⚠️  REVIEW MANUALLY: These results may include noise!")
                    results = force_results
    
    if debug:
        print(f"🎯 Final result: {results['num_peaks_found']} peaks detected")
        if results.get('warning'):
            print(f"⚠️  {results['warning']}")
        if results.get('all_peaks'):
            for peak in results['all_peaks']:
                print(f"   Peak {peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u.")
    
    return results


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


def find_true_shoulders_excluding_peaks(df, max_features=5, sensitivity=0.05):
    """
    Detecta hombros con algoritmo ULTRA AGRESIVO.
    Versión simplificada que encuentra prácticamente cualquier máximo local que no sea un pico principal.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - max_features: Maximum number of shoulders to find
    - sensitivity: Sensitivity for detecting changes (0.001-1.0, lower = more sensitive)
    
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
        
        original_intensity = intensity.copy()
        
        # Paso 1: Detectar solo los picos MUY prominentes para excluir
        print("🔍 Detectando solo picos principales para excluir...")
        
        # Usar criterios balanceados para picos principales
        traditional_peaks, _ = find_peaks(
            intensity,
            height=np.min(intensity) + 0.2 * (np.max(intensity) - np.min(intensity)),  # Picos medios-altos
            distance=10,  # Distancia razonable entre picos principales
            prominence=0.1 * (np.max(intensity) - np.min(intensity)),  # Prominencia moderada
            width=2
        )
        
        # Crear zonas de exclusión alrededor de picos principales
        excluded_zones = []
        for peak_idx in traditional_peaks:
            peak_wl = wavelength[peak_idx]
            exclusion_radius = 6  # Radio balanceado de exclusión
            excluded_zones.append((peak_wl - exclusion_radius, peak_wl + exclusion_radius))
            print(f"🚫 Excluyendo zona {peak_wl - exclusion_radius:.1f}-{peak_wl + exclusion_radius:.1f} nm (pico principal en {peak_wl:.1f} nm)")
        
        print(f"🔍 Buscando hombros con criterios ULTRA AGRESIVOS...")
        
        # Suavizar mínimamente
        if len(intensity) >= 5:
            smoothed_intensity = savgol_filter(intensity, 5, polyorder=2)
        else:
            smoothed_intensity = intensity.copy()
        
        global_range = np.max(intensity) - np.min(intensity)
        shoulder_candidates = []
        
        # MÉTODO ULTRA AGRESIVO: Buscar TODOS los máximos locales
        for i in range(3, len(intensity) - 3):
            current_wl = wavelength[i]
            
            # Verificar que NO esté en zona excluida (picos principales)
            in_excluded_zone = any(start <= current_wl <= end for start, end in excluded_zones)
            
            if not in_excluded_zone:
                # Verificar si es un máximo local (criterio muy permisivo)
                is_local_max = (intensity[i] >= intensity[i-1] and 
                               intensity[i] >= intensity[i+1] and
                               intensity[i] >= intensity[i-2] and 
                               intensity[i] >= intensity[i+2])
                
                if is_local_max:
                    shoulder_intensity = intensity[i]
                    
                    # Criterio muy permisivo para altura mínima
                    min_intensity = np.min(intensity) + sensitivity * global_range
                    
                    if shoulder_intensity >= min_intensity:
                        # Calcular prominencia local
                        local_window = 5
                        start_idx = max(0, i - local_window)
                        end_idx = min(len(intensity), i + local_window + 1)
                        local_min = np.min(intensity[start_idx:end_idx])
                        prominence = shoulder_intensity - local_min
                        
                        # Criterio MUY permisivo para prominencia
                        min_prominence = 0.001 * global_range  # Casi cualquier cosa
                        
                        if prominence >= min_prominence:
                            # Verificar que no esté muy cerca de candidatos existentes
                            too_close = any(abs(wavelength[i] - existing['wavelength']) < 2 
                                          for existing in shoulder_candidates)
                            
                            if not too_close:
                                shoulder_candidates.append({
                                    'wavelength': float(wavelength[i]),
                                    'intensity': float(original_intensity[i]),
                                    'prominence': float(prominence),
                                    'data_index': int(i),
                                    'type': 'shoulder',
                                    'detection_method': 'ultra_aggressive_local_max'
                                })
        
        # MÉTODO 2: Buscar usando derivadas con criterios muy permisivos
        first_derivative = np.gradient(smoothed_intensity, wavelength)
        
        for i in range(5, len(first_derivative) - 5):
            current_wl = wavelength[i]
            
            # Verificar que NO esté en zona excluida
            in_excluded_zone = any(start <= current_wl <= end for start, end in excluded_zones)
            
            if not in_excluded_zone:
                # Buscar cruces por cero en la primera derivada (cambios de pendiente)
                if ((first_derivative[i-1] > 0 and first_derivative[i+1] < 0) or
                    (abs(first_derivative[i]) < 0.1 * np.std(first_derivative))):
                    
                    shoulder_intensity = intensity[i]
                    min_intensity = np.min(intensity) + sensitivity * global_range
                    
                    if shoulder_intensity >= min_intensity:
                        # Verificar que no esté muy cerca de candidatos existentes
                        too_close = any(abs(wavelength[i] - existing['wavelength']) < 2 
                                      for existing in shoulder_candidates)
                        
                        if not too_close:
                            prominence = shoulder_intensity - np.min(intensity[max(0, i-5):min(len(intensity), i+6)])
                            
                            if prominence > 0.001 * global_range:
                                shoulder_candidates.append({
                                    'wavelength': float(wavelength[i]),
                                    'intensity': float(original_intensity[i]),
                                    'prominence': float(prominence),
                                    'first_derivative': float(first_derivative[i]),
                                    'data_index': int(i),
                                    'type': 'shoulder',
                                    'detection_method': 'derivative_zero_cross'
                                })
        
        # Filtrar y seleccionar los mejores candidatos
        shoulder_candidates.sort(key=lambda x: x['prominence'], reverse=True)
        selected_shoulders = shoulder_candidates[:max_features]
        
        # Ordenar por longitud de onda y asignar IDs
        selected_shoulders.sort(key=lambda x: x['wavelength'])
        for i, shoulder in enumerate(selected_shoulders):
            shoulder['index'] = f'S{i + 1}'
        
        print(f"✅ Encontrados {len(selected_shoulders)} hombros con detección ultra agresiva")
        for shoulder in selected_shoulders:
            print(f"   🔹 {shoulder['index']}: {shoulder['wavelength']:.1f} nm, prominencia: {shoulder['prominence']:.2f}")
        
        results = {
            'num_shoulders_found': len(selected_shoulders),
            'all_shoulders': selected_shoulders,
            'excluded_peak_zones': excluded_zones,
            'traditional_peaks_excluded': len(traditional_peaks),
            'analysis_params': {
                'sensitivity': sensitivity,
                'method': 'ultra_aggressive'
            }
        }
        
        return results
        
    except Exception as e:
        return {
            'num_shoulders_found': 0,
            'all_shoulders': [],
            'error': f'Ultra aggressive shoulder detection failed: {e}'
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


def find_peaks_and_shoulders_combined(df, max_total_peaks=3):
    """
    Combina detección de picos tradicionales y hombros, pero los llama a TODOS "picos".
    Nomenclatura unificada: P1, P2, P3, etc. para todos los features ordenados por wavelength.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - max_total_peaks: Maximum total features (peaks + shoulders) to return
    
    Returns:
    - dict with combined results where all features are called "peaks"
    """
    # Detectar picos tradicionales
    peak_results = find_fluorescence_peaks_adaptive(df, max_peaks=8, debug=False)
    
    # Detectar hombros (excluyendo regiones con picos)
    shoulder_results = find_true_shoulders_excluding_peaks(df, max_features=5, sensitivity=0.05)
    
    print(f"🔍 Detección combinada:")
    print(f"   Picos tradicionales encontrados: {len(peak_results.get('all_peaks', []))}")
    print(f"   Hombros encontrados: {len(shoulder_results.get('all_shoulders', []))}")
    
    # Combinar TODOS los features en una sola lista
    all_features = []
    
    # Agregar picos tradicionales
    for peak in peak_results.get('all_peaks', []):
        feature = peak.copy()
        feature['detection_type'] = 'traditional_peak'
        feature['original_type'] = 'peak'
        all_features.append(feature)
    
    # Agregar hombros como "picos"
    for shoulder in shoulder_results.get('all_shoulders', []):
        feature = shoulder.copy()
        feature['detection_type'] = 'shoulder_peak'
        feature['original_type'] = 'shoulder'
        # Mantener toda la información del hombro pero tratarlo como pico
        all_features.append(feature)
    
    # Comentado temporalmente para evitar detección de ruido
    # Si aún no encuentra hombros, usar solo métodos más balanceados
    if len(shoulder_results.get('all_shoulders', [])) == 0:
        print("⚠️  No se encontraron hombros con método estándar")
        # Probar con sensibilidad ligeramente mayor
        sensitive_shoulder_results = find_true_shoulders_excluding_peaks(df, max_features=3, sensitivity=0.02)
        
        for shoulder in sensitive_shoulder_results.get('all_shoulders', []):
            feature = shoulder.copy()
            feature['detection_type'] = 'sensitive_shoulder_peak'
            feature['original_type'] = 'sensitive_shoulder'
            all_features.append(feature)
        
        print(f"   Hombros con mayor sensibilidad: {len(sensitive_shoulder_results.get('all_shoulders', []))}")
    
    # Ordenar TODOS por longitud de onda
    all_features.sort(key=lambda x: x['wavelength'])
    
    # Asignar nomenclatura unificada P1, P2, P3... para TODOS
    for i, feature in enumerate(all_features):
        feature['index'] = i + 1  # 1, 2, 3...
        feature['display_id'] = f"P{i + 1}"  # P1, P2, P3...
        feature['type'] = 'peak'  # TODOS son "peaks" ahora
    
    # Tomar solo los primeros max_total_peaks
    selected_features = all_features[:max_total_peaks]
    
    # Estadísticas para debug
    traditional_peaks_count = len([f for f in selected_features if f['detection_type'] == 'traditional_peak'])
    shoulder_peaks_count = len([f for f in selected_features if f['detection_type'] in ['shoulder_peak', 'sensitive_shoulder_peak']])
    
    print(f"📊 Resultado final: {len(selected_features)} picos totales")
    print(f"   - Tradicionales: {traditional_peaks_count}")
    print(f"   - Hombros: {shoulder_peaks_count}")
    
    combined_results = {
        'num_peaks_found': len(selected_features),
        'all_peaks': selected_features,
        'traditional_peaks_count': traditional_peaks_count,
        'shoulder_peaks_count': shoulder_peaks_count,
        'total_features_detected': len(all_features),
        'analysis_method': 'ultra_aggressive_combined'
    }
    
    # Mantener compatibilidad con formato anterior
    if len(selected_features) >= 1:
        combined_results['first_peak'] = {
            'wavelength': selected_features[0]['wavelength'],
            'intensity': selected_features[0]['intensity'],
            'position': 'peak_1',
            'detection_type': selected_features[0]['detection_type']
        }
    
    if len(selected_features) >= 3:
        combined_results['third_peak'] = {
            'wavelength': selected_features[2]['wavelength'],
            'intensity': selected_features[2]['intensity'],
            'position': 'peak_3',
            'detection_type': selected_features[2]['detection_type']
        }
    
    return combined_results


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


def find_peaks_in_region(df, wavelength_range, max_peaks=1):
    """
    Find peaks specifically in a wavelength range using ultra-sensitive parameters.
    
    Parameters:
    - df: DataFrame with wavelength and intensity columns
    - wavelength_range: tuple (min_wl, max_wl) to search
    - max_peaks: Maximum peaks to find in region
    
    Returns:
    - dict with peak results for the specified region
    """
    # First diagnose the region
    diagnosis = diagnose_missing_peak(df, wavelength_range, debug=False)
    
    if 'error' in diagnosis:
        return diagnosis
    
    # Use custom parameters based on diagnosis
    custom_params = diagnosis['suggested_params']
    
    try:
        results = find_fluorescence_peaks(
            df,
            max_peaks=max_peaks,
            min_height=custom_params['custom_min_height'],
            min_distance=1,
            prominence=custom_params['custom_prominence'],
            smooth=False
        )
        
        # Filter results to only include peaks in the specified range
        region_peaks = []
        for peak in results.get('all_peaks', []):
            if wavelength_range[0] <= peak['wavelength'] <= wavelength_range[1]:
                region_peaks.append(peak)
        
        results['all_peaks'] = region_peaks
        results['num_peaks_found'] = len(region_peaks)
        results['region_analyzed'] = wavelength_range
        results['diagnosis'] = diagnosis
        
        return results
        
    except Exception as e:
        return {'error': f'Peak detection failed: {e}', 'diagnosis': diagnosis}


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