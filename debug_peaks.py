#!/usr/bin/env python3
"""
Debug script for peak detection - creates synthetic data and tests peak finding.
"""

import numpy as np
import pandas as pd

def create_test_spectrum_with_weak_375():
    """Create a test spectrum with a weak peak at 375nm and other peaks."""
    # Create wavelength range that includes 375nm
    wavelength = np.linspace(350, 600, 500)  # 500 points for good resolution
    
    # Create a baseline with some slope
    baseline = 100 + 0.02 * wavelength + np.random.normal(0, 2, len(wavelength))
    
    # Add peaks including the problematic weak one at 375nm
    peak1 = 800 * np.exp(-((wavelength - 360) / 8)**2)    # Peak 1 at 360nm (strong)
    peak2 = 80 * np.exp(-((wavelength - 375) / 6)**2)     # Peak 2 at 375nm (WEAK - the problematic one)
    peak3 = 500 * np.exp(-((wavelength - 420) / 12)**2)   # Peak 3 at 420nm (medium)
    peak4 = 300 * np.exp(-((wavelength - 480) / 15)**2)   # Peak 4 at 480nm (will be ignored - only first 3)
    peak5 = 400 * np.exp(-((wavelength - 540) / 18)**2)   # Peak 5 at 540nm (will be ignored)
    
    # Combine all components
    intensity = baseline + peak1 + peak2 + peak3 + peak4 + peak5
    
    # Add realistic noise that could hide weak peaks
    intensity += np.random.normal(0, 8, len(wavelength))
    
    # Ensure no negative values
    intensity = np.maximum(intensity, baseline * 0.8)
    
    return pd.DataFrame({
        'Wavelength': wavelength,
        'Intensity': intensity
    })

def create_simple_test_spectrum():
    """Legacy function - now calls the new one with weak 375nm peak."""
    return create_test_spectrum_with_weak_375()

def test_peak_detection_simple():
    """Test peak detection with synthetic data."""
    print("🧪 Testing Peak Detection with Simple Synthetic Data")
    print("=" * 60)
    
    try:
        # Import the function - this will work only if dependencies are available
        from curve_tools import find_fluorescence_peaks
        
        # Create test data
        df = create_simple_test_spectrum()
        print(f"📊 Created test spectrum with {len(df)} data points")
        print(f"   Wavelength range: {df['Wavelength'].min():.1f} - {df['Wavelength'].max():.1f} nm")
        print(f"   Intensity range: {df['Intensity'].min():.1f} - {df['Intensity'].max():.1f}")
        
        # Test peak detection with different parameters
        print("\n🔍 Testing peak detection...")
        
        # Test 1: Default parameters
        print("\n--- Test 1: Default parameters ---")
        results1 = find_fluorescence_peaks(df)
        print(f"Peaks found: {results1['num_peaks_found']}")
        
        if results1.get('all_peaks'):
            print("All peaks by wavelength order:")
            for peak in results1['all_peaks']:
                print(f"  Peak {peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.1f} a.u.")
        
        if results1.get('first_peak'):
            fp = results1['first_peak']
            print(f"First peak: {fp['wavelength']:.1f} nm, {fp['intensity']:.1f} a.u.")
        else:
            print("❌ First peak not identified")
            
        if results1.get('third_peak'):
            tp = results1['third_peak']
            print(f"Third peak: {tp['wavelength']:.1f} nm, {tp['intensity']:.1f} a.u.")
        else:
            print("❌ Third peak not identified")
        
        # Test 2: More sensitive parameters
        print("\n--- Test 2: More sensitive parameters ---")
        results2 = find_fluorescence_peaks(df, prominence=0.02, min_distance=3)
        print(f"Peaks found: {results2['num_peaks_found']}")
        
        if results2.get('all_peaks'):
            print("All peaks by wavelength order:")
            for peak in results2['all_peaks']:
                print(f"  Peak {peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.1f} a.u.")
        
        # Test 3: Show debug info
        if 'debug_info' in results1:
            print(f"\n📋 Debug Info:")
            debug = results1['debug_info']
            print(f"   Data points: {debug['total_data_points']}")
            print(f"   Wavelength range: {debug['wavelength_range']}")
            print(f"   Intensity range: {debug['intensity_range']}")
            params = debug['detection_params']
            print(f"   Min height used: {params['min_height_used']:.2f}")
            print(f"   Prominence used: {params['prominence_used']:.2f}")
            print(f"   Min distance used: {params['min_distance_used']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
        print("This test requires numpy, pandas, and scipy to be installed.")
        return False
    except Exception as e:
        print(f"❌ Error during peak detection test: {e}")
        return False

if __name__ == "__main__":
    success = test_peak_detection_simple()
    
    if success:
        print("\n✅ Peak detection test completed!")
        print("\n💡 Expected results with new ultra-sensitive detection:")
        print("   - Peak 1 should be around 360 nm (strongest)")
        print("   - Peak 2 should be around 375 nm (WEAK - previously missed!)") 
        print("   - Peak 3 should be around 420 nm (medium)")
        print("   - Should find EXACTLY 3 peaks (first 3 by wavelength)")
        print("   - Peak 2 at 375nm is the critical test case")
        print("   - Peaks at 480nm and 540nm should be IGNORED (only first 3)")
    else:
        print("\n❌ Peak detection test failed.")
        print("   The function might not be finding peaks correctly.")
        print("   Try adjusting the detection parameters.")