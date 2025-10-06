# Agent Guidelines for Spectra Viewer

## Build/Test Commands
- **Run single test**: `python3 test_<name>.py` (e.g., `python3 test_peak_detection.py`)
- **Run main apps**: `python3 main_fluo.py` or `python3 main_UV.py` or `python3 launcher.py`
- **No linting/type checking configured** - ensure code runs without errors

## Code Style

### Imports
- Standard library first, then third-party (numpy, pandas, scipy, PyQt5, plotly), then local modules
- Group related imports: `from module import (func1, func2, func3)` with parentheses for multiline
- Local imports: `from module import function` (specific imports preferred)

### Formatting & Structure
- Functions use docstrings with description and Parameters/Returns sections
- Snake_case for functions/variables, PascalCase for classes
- 4-space indentation, no tabs
- Keep functions focused and well-documented with clear parameter descriptions

### Error Handling
- Use try/except blocks with specific error messages
- Return dicts with 'error' key for function failures: `{'error': 'message'}`
- Validate inputs early (check None, empty DataFrames, column counts)
- Raise ValueError/RuntimeError with descriptive messages

### Data Patterns
- DataFrames have wavelength in column 0, intensity in column 1
- Access by position: `df.iloc[:, 0]` and `df.iloc[:, 1]`
- Always sort by wavelength: `sort_indices = np.argsort(wavelength)`
- Return copies, never modify input DataFrames in-place
