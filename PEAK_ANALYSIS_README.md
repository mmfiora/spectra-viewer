# 🔬 Peak Analysis Functionality

## Overview
The fluorescence spectra viewer now includes simplified peak detection capabilities with an interactive interface for analyzing peaks in your fluorescence data.

## ✨ New Features

### 🎯 Peak Detection Algorithm
- **Automatic peak detection** using scipy's robust signal processing
- **Smart baseline correction** to handle noisy data
- **Configurable sensitivity** for different spectrum types
- **First and third peak identification** with precise intensity measurements

### 🖥️ User Interface
- **"Peak Analysis" button** - Only visible in the fluorescence viewer
- **Simple peak table** showing all detected peaks
- **Visual peak markers** displayed directly on the plot
- **Click-to-remove** functionality for individual peaks

### 📊 Results Display
- **Peak wavelengths** (in nm)
- **Peak intensities** (in arbitrary units)
- **Peak markers** on the plot with labels
- **Interactive peak removal** with ✕ buttons
- **Real-time plot updates** when peaks are removed

### 💾 Export Options
- **CSV export** - Peak data for further analysis
- **Plot export** - Includes peak markers in saved images

## 🚀 How to Use

### Step-by-Step Instructions

1. **Launch the Fluorescence Viewer**
   ```bash
   python main_fluo.py
   ```

2. **Load Your Data**
   - Click "Load Files"
   - Select your fluorescence data files (.txt or .csv)

3. **Select and Plot Curves**
   - Choose curves from "Loaded Columns"
   - Click "Plot Selected Columns"

4. **Analyze Peaks**
   - Select ONE curve from "Plotted Curves" 
   - Click "**Peak Analysis**" button
   - View peaks in the simple table and on the plot

5. **Manage Peaks**
   - **Remove unwanted peaks**: Click the ✕ button in the table
   - **View peak info**: See wavelength and intensity in the table
   - **Export peaks**: Use "Export to CSV" for data analysis

6. **Interactive Features**
   - Peak markers appear on the plot automatically
   - Peak table stays open for easy management
   - Plot updates in real-time when peaks are removed

### 📋 Example Interface

The peak analysis shows exactly the first 3 peaks by wavelength:
```
First 3 Peaks - sample_fluorescence: Emission
=============================================

| Peak # | Wavelength (nm) | Intensity (a.u.) | Remove |
|--------|-----------------|------------------|--------|
|   1    |      360.2      |      1547.5      |   ✕    |  <- Peak 1 (green highlight)
|   2    |      375.1      |        87.3      |   ✕    |  <- Peak 2 (weak, previously missed!)
|   3    |      420.9      |       892.3      |   ✕    |  <- Peak 3 (blue highlight)
```

Plus visual markers on the plot showing each peak position (P1, P2, P3).
Note: Only the first 3 peaks by wavelength are detected and displayed.

## ⚙️ Algorithm Parameters

The peak detection algorithm uses ultra-sensitive parameters to capture weak peaks:

- **Minimum Height**: Auto-calculated (0.1% above baseline) - ultra-sensitive
- **Minimum Distance**: 1 data point between peaks - allows adjacent peaks
- **Prominence**: 0.1% of maximum intensity - detects very small peaks
- **Smoothing**: Disabled by default - preserves all peak details
- **Peak Limit**: Exactly 3 peaks maximum (first 3 by wavelength)
- **Minimum Prominence**: Absolute minimum of 0.5 intensity units

These parameters are optimized specifically to catch weak peaks like the one at 375nm that was previously missed.

## 🔧 Technical Details

### Dependencies Added
- **scipy.signal**: For robust peak detection
- **PeakAnalysisDialog**: Custom Qt dialog for results display

### Files Modified
- `curve_tools.py`: Added `find_fluorescence_peaks()` and `calculate_peak_statistics()`
- `base_spectra_viewer.py`: Added peak analysis button and functionality
- `spectra_viewer_fluo.py`: Enabled peak analysis button
- `peak_analysis_dialog.py`: New results display dialog

### Peak Detection Process
1. **Data validation** and cleaning
2. **Optional smoothing** to reduce noise
3. **Automatic parameter calculation**
4. **Peak detection** using scipy.signal.find_peaks
5. **Peak sorting** by wavelength position
6. **Results formatting** and statistics calculation

## 🎯 Best Practices

### For Optimal Results
- **Clean data**: Remove baseline drift before analysis
- **Sufficient resolution**: At least 100+ data points
- **Clear peaks**: Prominence > 10% of max intensity
- **Single curve analysis**: Analyze one curve at a time

### Troubleshooting
- **No peaks found**: Try reducing detection sensitivity or check data quality
- **Too many peaks**: Increase minimum distance or prominence threshold
- **Wrong peaks identified**: Consider data smoothing or manual inspection

### When to Use Peak Analysis
- ✅ **Quantitative fluorescence analysis**
- ✅ **Comparison of emission intensities**
- ✅ **Quality control of fluorescent samples**
- ✅ **Research data analysis and reporting**
- ❌ **Broad, featureless spectra**
- ❌ **Very noisy data without clear peaks**

## 📈 Applications

### Scientific Research
- **Fluorescent protein characterization**
- **Quantum dot analysis**
- **Dye concentration studies**
- **FRET efficiency calculations**

### Quality Control
- **Product consistency testing**
- **Batch-to-batch comparison**
- **Contamination detection**
- **Standards verification**

## 🔮 Future Enhancements

Potential future additions:
- **Peak fitting** with Gaussian/Lorentzian curves
- **Automatic baseline correction**
- **Batch analysis** of multiple files
- **Peak area integration**
- **Advanced statistical analysis**

---

## 📞 Support

For questions or issues with the peak analysis functionality:
1. Check that your data has clear, distinguishable peaks
2. Verify that you're using the fluorescence viewer (not UV viewer)
3. Ensure your data format is compatible (.txt or .csv)
4. Try the test script: `python test_peak_detection.py`

---

**Happy analyzing! 🧪✨**