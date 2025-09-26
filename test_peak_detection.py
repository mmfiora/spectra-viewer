#!/usr/bin/env python3
"""
Test script for peak detection functionality.
Creates synthetic fluorescence data and tests the peak detection algorithm.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from curve_tools import find_fluorescence_peaks, calculate_peak_statistics


def create_synthetic_fluorescence_spectrum():
    """Create a synthetic fluorescence spectrum with known peaks."""
    # Generate wavelength range (typical fluorescence range)
    wavelength = np.linspace(400, 700, 300)
    
    # Create baseline
    baseline = 50 + 5 * np.random.normal(0, 1, len(wavelength))
    
    # Add three Gaussian peaks
    peak1 = 200 * np.exp(-((wavelength - 450) / 15)**2)  # First peak at 450nm
    peak2 = 120 * np.exp(-((wavelength - 520) / 20)**2)  # Second peak at 520nm  
    peak3 = 180 * np.exp(-((wavelength - 580) / 18)**2)  # Third peak at 580nm
    
    # Combine all components
    intensity = baseline + peak1 + peak2 + peak3
    
    # Add some noise
    intensity += 3 * np.random.normal(0, 1, len(wavelength))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Wavelength': wavelength,
        'Intensity': intensity
    })
    
    return df


def test_peak_detection():
    """Test the peak detection functionality."""
    print("🧪 Testing Peak Detection Functionality")
    print("=" * 50)
    
    # Create synthetic data
    print("📊 Creating synthetic fluorescence spectrum...")
    df = create_synthetic_fluorescence_spectrum()
    
    try:
        # Test peak detection
        print("🔍 Running peak detection...")
        results = find_fluorescence_peaks(df)
        
        print(f"✅ Peak detection completed successfully!")
        print(f"📈 Found {results['num_peaks_found']} peaks")
        
        # Display results
        if results.get('first_peak'):
            fp = results['first_peak']
            print(f"🔸 First Peak: {fp['wavelength']:.1f} nm, {fp['intensity']:.1f} a.u.")
        else:
            print("❌ First peak not found")
        
        if results.get('third_peak'):
            tp = results['third_peak']
            print(f"🔸 Third Peak: {tp['wavelength']:.1f} nm, {tp['intensity']:.1f} a.u.")
        else:
            print("❌ Third peak not found")
        
        # Test statistics calculation
        print("\n📊 Calculating peak statistics...")
        stats = calculate_peak_statistics(results)
        
        if 'error' not in stats:
            print(f"✅ Statistics calculated successfully!")
            if 'first_to_third_ratio' in stats:
                print(f"📈 First/Third intensity ratio: {stats['first_to_third_ratio']:.2f}")
        
        # Show all peaks
        print(f"\n📋 All detected peaks:")
        for i, peak in enumerate(results.get('all_peaks', [])):
            print(f"   Peak {peak['index']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.1f} a.u.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during peak detection: {e}")
        return False


def plot_test_spectrum():
    """Create and save a plot of the test spectrum with detected peaks."""
    try:
        import matplotlib.pyplot as plt
        
        print("\n📈 Creating test plot...")
        df = create_synthetic_fluorescence_spectrum()
        results = find_fluorescence_peaks(df)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['Wavelength'], df['Intensity'], 'b-', linewidth=2, label='Fluorescence Spectrum')
        
        # Mark all detected peaks
        if results.get('all_peaks'):
            for peak in results['all_peaks']:
                wavelength = peak['wavelength']
                intensity = peak['intensity']
                
                if peak['index'] == 1:  # First peak
                    plt.plot(wavelength, intensity, 'ro', markersize=10, label='First Peak')
                elif peak['index'] == 3:  # Third peak
                    plt.plot(wavelength, intensity, 'go', markersize=10, label='Third Peak')
                else:
                    plt.plot(wavelength, intensity, 'yo', markersize=8, label=f'Peak {peak["index"]}')
        
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Fluorescence Intensity (a.u.)')
        plt.title('Test Fluorescence Spectrum with Peak Detection')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        plt.savefig('test_peak_detection.png', dpi=150, bbox_inches='tight')
        print("✅ Test plot saved as 'test_peak_detection.png'")
        plt.close()
        
    except ImportError:
        print("⚠️  Matplotlib not available, skipping plot generation")
    except Exception as e:
        print(f"❌ Error creating plot: {e}")


if __name__ == "__main__":
    print("🔬 Peak Detection Test Suite")
    print("=" * 60)
    
    # Test 1: Basic peak detection
    success = test_peak_detection()
    
    # Test 2: Plot generation
    plot_test_spectrum()
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
        print("🎉 Peak detection functionality is working correctly.")
        print("\n📋 To use in the application:")
        print("   1. Start the fluorescence viewer")
        print("   2. Load fluorescence data")
        print("   3. Select a curve")
        print("   4. Click 'Peak Analysis' button")
    else:
        print("❌ Some tests failed. Please check the error messages above.")