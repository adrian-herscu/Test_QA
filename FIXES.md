# Bug Fixes and Code Corrections

This document lists all bugs found in the provided skeleton code and the fixes applied.

## Summary

During the implementation of the ammeter testing framework, several bugs were identified and fixed to ensure proper functionality. These issues ranged from incorrect port configurations to library API compatibility problems.

---

## Bug #1: Incorrect Port Numbers

**File:** `main.py`

**Issue:**
The port numbers used in `main.py` did not match the specifications in `README.md`:
- README specified: Greenlee (5000), ENTES (5001), CIRCUTOR (5002)
- Code used: Greenlee (5001), ENTES (5002), CIRCUTOR (5003)

**Impact:**
Client code attempting to connect to ammeters using README specifications would fail to establish connections.

**Fix:**
Updated port assignments in `main.py`:
```python
# Before
greenlee = GreenleeAmmeter(5001)
entes = EntesAmmeter(5002)
circutor = CircutorAmmeter(5003)

# After
greenlee = GreenleeAmmeter(5000)
entes = EntesAmmeter(5001)
circutor = CircutorAmmeter(5002)
```

**Root Cause:**
Mismatch between documentation and implementation, likely from copy-paste error.

---

## Bug #2: Incomplete Ammeter Commands

**File:** `main.py` (commented code)

**Issue:**
The commented test code used incomplete commands that didn't match the ammeter implementations:
- Used: `MEASURE_GREENLEE`, `MEASURE_ENTES`, `MEASURE_CIRCUTOR`
- Required: Full commands with parameters as defined in ammeter classes

**Impact:**
Commands would not match the expected patterns in `base_ammeter.py`, causing connection to succeed but no response.

**Fix:**
Updated commands to match ammeter implementations:
```python
# Greenlee
b'MEASURE_GREENLEE -get_measurement'

# ENTES
b'MEASURE_ENTES -get_data'

# CIRCUTOR
b'MEASURE_CIRCUTOR -get_measurement -current'
```

**Root Cause:**
Incomplete command strings missing required parameters.

---

## Bug #3: Scipy API Compatibility Issue

**File:** `src/testing/result_analyzer.py`

**Issue:**
Code used old scipy API parameter `alpha` in `stats.t.interval()`, but newer scipy versions (≥1.11) renamed it to `confidence`:
```python
stats.t.interval(
    alpha=0.95,  # Old API, deprecated in scipy 1.11+
    df=len(values)-1,
    loc=np.mean(values),
    scale=stats.sem(values)
)
```

**Error Message:**
```
TypeError: rv_generic.interval() missing 1 required positional argument: 'confidence'
```

**Impact:**
Statistical analysis would crash when calculating confidence intervals, preventing test completion.

**Fix:**
Updated parameter name to match current scipy API:
```python
stats.t.interval(
    confidence=0.95,  # New API (scipy ≥1.11)
    df=len(values)-1,
    loc=np.mean(values),
    scale=stats.sem(values)
)
```

**Root Cause:**
Python 3.13 removed `distutils`, which older numpy/scipy versions depend on for building. This forced use of newer library versions that support Python 3.13. The requirements.txt specified `scipy>=1.7.0`, allowing any version - but only scipy ≥1.17 supports Python 3.13.

**Solution:**
Pinned to scipy 1.17.0 (tested with Python 3.13) and updated code to use the modern API.

---

## Bug #4: Numpy Boolean JSON Serialization

**File:** `src/testing/result_analyzer.py`

**Issue:**
Direct assignment of numpy comparison result to dictionary:
```python
advanced_results["is_normal_distribution"] = normality_p_value > 0.05
```

This creates a `numpy.bool_` type, which is not JSON serializable.

**Error Message:**
```
TypeError: Object of type bool is not JSON serializable
```

**Impact:**
Test results could not be saved to JSON files, causing `_save_results()` to fail.

**Fix:**
Explicitly convert to Python native bool:
```python
advanced_results["is_normal_distribution"] = bool(normality_p_value > 0.05)
```

**Root Cause:**
Numpy operations return numpy types, not Python native types. JSON encoder only handles Python native types.

---

## Bug #5: Missing Socket Implementation

**File:** `src/testing/data_collector.py`

**Issue:**
The `_get_measurement()` method was incomplete:
```python
def _get_measurement(self, ammeter_type: str, config: Dict) -> float:
    """
    קבלת מדידה מהאמפרמטר הספציפי
    """
    # כאן צריך לממש את הקריאה לאמפרמטר הספציפי
    # using existing ammeter code
    pass
```

**Impact:**
No actual measurements could be collected from ammeters, framework was non-functional.

**Fix:**
Implemented socket-based communication:
```python
def _get_measurement(self, ammeter_type: str, config: Dict) -> float:
    import socket

    port = config["port"]
    command = config["command"].encode('utf-8')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5 second timeout
            s.connect(('localhost', port))
            s.sendall(command)
            data = s.recv(1024)
            if data:
                return float(data.decode('utf-8'))
            else:
                raise ValueError(f"No data received from {ammeter_type}")
    except (socket.error, ValueError) as e:
        raise RuntimeError(
            f"Failed to get measurement from {ammeter_type}: {str(e)}")
```

**Root Cause:**
Skeleton code intentionally left incomplete for implementation.

---

## Bug #6: Main Script Exits Immediately

**File:** `main.py`

**Issue:**
The main script would start ammeter threads and immediately exit:
```python
threading.Thread(target=run_greenlee_emulator, daemon=True).start()
threading.Thread(target=run_entes_emulator, daemon=True).start()
threading.Thread(target=run_circutor_emulator, daemon=True).start()

# Script exits here, killing daemon threads
```

**Impact:**
Daemon threads would be terminated when main thread exits, making ammeters unavailable for testing framework.

**Fix:**
Added infinite loop to keep main thread alive:
```python
# Keep the program running to serve requests from the testing framework
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down emulators...")
```

**Root Cause:**
Daemon threads only run while main program is running. Need to keep main thread alive.

---

## Bug #7: CIRCUTOR Command Configuration

**File:** `config/test_config.yaml`

**Issue:**
CIRCUTOR ammeter command missing required `-current` parameter:
```yaml
circutor:
  port: 5002
  command: "MEASURE_CIRCUTOR -get_measurement"  # Incomplete
```

But implementation expects:
```python
# In Circutor_Ammeter.py
return b'MEASURE_CIRCUTOR -get_measurement -current'
```

**Impact:**
Commands wouldn't match, CIRCUTOR measurements would fail.

**Fix:**
Updated config with complete command:
```yaml
circutor:
  port: 5002
  command: "MEASURE_CIRCUTOR -get_measurement -current"
```

**Root Cause:**
Config file didn't match actual ammeter implementation.

---

## Bug #8: Import Path Issues

**File:** `examples/run_tests.py`

**Issue:**
Module imports failed because project root wasn't in Python path:
```python
from test_qa.testing.test_framework import AmmeterTestFramework
# ModuleNotFoundError: No module named 'test_qa'
```

**Impact:**
Example scripts couldn't import framework modules.

**Fix:**
Added path manipulation before imports:
```python
import sys
import os

# Add parent directory to path so we can import src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_qa.testing.test_framework import AmmeterTestFramework
```

**Note:** Used formatter disable comments to prevent auto-sorting from breaking the fix:
```python
# fmt: off
# isort: off
# ... path manipulation and imports ...
# fmt: on
# isort: on
```

**Root Cause:**
Python doesn't automatically include parent directories in module search path.

---

## Bug #9: Socket Address Reuse Issue

**File:** `Ammeters/base_ammeter.py`

**Issue:**
After stopping `main.py` with Ctrl+C, the sockets remained in TIME_WAIT state, preventing immediate restart:
```
OSError: [Errno 98] Address already in use
```

**Impact:**
Could not restart emulators without waiting 30-60 seconds or manually killing processes. Made development/testing workflow cumbersome.

**Fix:**
Added `SO_REUSEADDR` socket option before binding:
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Allow socket reuse to prevent "Address already in use" errors
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', self.port))
    s.listen()
```

**Root Cause:**
When a TCP connection closes, the socket enters TIME_WAIT state to ensure all packets are properly handled. Without SO_REUSEADDR, binding to the same port fails until TIME_WAIT expires.

---

## Bug #10: Async Error in Invalid Ammeter Validation

**File:** `src/testing/test_framework.py`

**Issue:**
Invalid ammeter type validation happened in background thread (`_sampling_worker`), causing:
- KeyError thrown in thread, not caught by main code
- Tests would hang indefinitely waiting for queue data
- No clear error message to user

**Impact:**
`test_invalid_ammeter_type` unit test would hang forever instead of properly catching the exception.

**Fix:**
Added validation at the start of `run_test()` before spawning threads:
```python
def run_test(self, ammeter_type: str) -> Dict:
    # Validate ammeter type before starting
    valid_types = list(self.config["ammeters"].keys())
    if ammeter_type.lower() not in valid_types:
        raise ValueError(f"Invalid ammeter type: {ammeter_type}. Must be one of {valid_types}")
    
    # Now safe to proceed with data collection
    measurements = self.data_collector.collect_measurements(...)
```

**Root Cause:**
Errors in background threads don't propagate to the calling code unless explicitly handled. Validation must happen synchronously before async operations begin.

---

## Additional Improvements

### Dependency Management

**Initial Configuration:**
Pinned all library versions in requirements.txt for reproducibility:
```
numpy==1.24.3
scipy==1.10.1
matplotlib==3.7.2
seaborn==0.12.2
pyyaml==6.0.1
pandas==2.0.3
```

**Python 3.13 Compatibility Issue:**

When using Python 3.13, the original requirements.txt caused installation failures:

**Problem 1: Missing distutils module**
```
ModuleNotFoundError: No module named 'distutils'
```
- The `distutils` module was removed in Python 3.12+
- numpy 1.24.3 requires distutils for building from source
- No pre-built wheels available for numpy 1.24.3 on Python 3.13

**Problem 2: Missing C++ compiler**
```
ERROR: Unknown compiler(s): [['c++'], ['g++'], ['clang++']]
```
- numpy 1.26.4 attempted to build from source
- Requires C++ compiler not installed on the system

**Solution:**
Updated to newer versions with pre-built wheels for Python 3.13:
```
numpy==2.4.1
scipy==1.17.0
matplotlib==3.10.8
seaborn==0.13.2
pyyaml==6.0.3
pandas==3.0.0
```

**Key Changes:**
- numpy: 1.24.3 → 2.4.1 (has pre-built wheels for Python 3.13)
- scipy: 1.10.1 → 1.17.0 (compatible with numpy 2.x)
- matplotlib: 3.7.2 → 3.10.8 (Python 3.13 support)
- seaborn: 0.12.2 → 0.13.2 (compatible with updated dependencies)
- pandas: 2.0.3 → 3.0.0 (Python 3.13 compatible)

**Compatibility Note:**
These versions install without requiring compilation or additional system packages. The code remains compatible as all core APIs are stable across these version updates.

### Added Missing Package Files
Created `__init__.py` files for proper Python package structure:
- `src/__init__.py`
- `src/testing/__init__.py`
- `src/utils/__init__.py`
- `src/ammeters/__init__.py`

### Updated .gitignore
- Added `.venv/` directory
- Simplified results exclusion pattern
- Added test coverage and log file patterns

### Pylance / Pyright

- Issue: Pylance reported missing imports for `test_qa` modules in `src`.
- Fix: Configured [pyrightconfig.json](pyrightconfig.json) with `include` for `src`, `examples`, `tests` and `extraPaths` set to `./src`; set `pythonVersion` to `3.13` and `typeCheckingMode` to `strict`.
- Impact: Editor resolves imports correctly and provides consistent type checking.

---

## Testing

All fixes were verified by:
1. Starting ammeter emulators: `python main.py`
2. Running test framework: `python examples/run_tests.py`
3. Verifying output shows successful measurements from all three ammeters
4. Confirming JSON results saved to `results/` directory
5. Checking generated plots in `results/plots/` directories

## Lessons Learned

1. **Always verify port configurations** match across all documentation and code
2. **Library version pinning** is critical when using specific APIs
3. **Type conversions** are necessary when bridging numpy and Python stdlib
4. **Daemon threads** require main thread to stay alive
5. **Command specifications** must be validated against actual implementations
6. **Import paths** need explicit configuration for non-standard project structures
