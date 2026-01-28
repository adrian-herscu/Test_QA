# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `src/test_qa/` - Main package (installed with `pip install -e .`)
  - `ammeters/` - Ammeter emulator implementations
    - `base_ammeter.py` - Base class for all ammeter emulators
    - `circutor_ammeter.py` - CIRCUTOR ammeter emulator
    - `entes_ammeter.py` - ENTES ammeter emulator
    - `greenlee_ammeter.py` - Greenlee ammeter emulator
    - `client.py` - Client to request current measurements
  - `testing/` - Testing framework components
    - `test_framework.py` - Core testing infrastructure
    - `data_collector.py` - Data collection utilities
    - `error_simulator.py` - Error simulation for testing
    - `result_analyzer.py` - Result analysis tools
    - `visualizer.py` - Data visualization
  - `utils/` - Utility functions
    - `utils.py` - Common utilities including `generate_random_float`
    - `config.py` - Configuration management
    - `logger.py` - Logging utilities
    - `ammeter_comparison.py` - Ammeter comparison tools
- `examples/` - Usage examples and demos
- `tests/` - Unit tests
- `config/` - Configuration files

## Usage

# Ammeter Emulators

## Greenlee Ammeter

- **Port**: 5000
- **Command**: `MEASURE_GREENLEE -get_measurement`
- **Measurement Logic**: Calculates current using voltage (1V - 10V) and (0.1Ω - 100Ω).
- **Measurement method** : Ohm's Law: I = V / R

## ENTES Ammeter

- **Port**: 5001
- **Command**: `MEASURE_ENTES -get_data`
- **Measurement Logic**: Calculates current using magnetic field strength (0.01T - 0.1T) and calibration factor (500 - 2000).
- **Measurement method** : Hall Effect: I = B * K

## CIRCUTOR Ammeter

- **Port**: 5002
- **Command**: `MEASURE_CIRCUTOR -get_measurement -current`
- **Measurement Logic**: Calculates current using voltage values (0.1V - 1.0V) over a number of samples and a random time step (0.001s - 0.01s).
- **Measurement method** : Rogowski Coil Integration: I = ∫V dt

To start the ammeter emulators and request current measurements, run:
```sh
python examples/run_emulators.py
```

---

## Testing Framework

### Installation

**Requirements**: Python 3.10 or higher

#### Quick Setup (Recommended)

Use the automated setup script to create a virtual environment and install all dependencies in one command:

**Linux/macOS:**
```bash
python3 setup_dev.py
```

**Windows:**
```bash
python setup_dev.py
```

This script will:
1. Verify Python 3.10+ is installed
2. Create a virtual environment (`.venv/`)
3. Upgrade pip
4. Install the project in editable mode

Then activate the virtual environment:

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

#### Manual Setup

If you prefer manual setup, follow these steps:

**1. Create a virtual environment:**
```bash
python -m venv .venv
```

**2. Activate the virtual environment:**

Linux/macOS:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

**3. Install the project:**
```bash
pip install -e .
```

This will install all dependencies and make the project modules importable.

### Running Tests

1. Start the ammeter emulators:
```bash
python examples/run_emulators.py
```

2. In a separate terminal, run the testing framework:
```bash
python examples/run_tests.py
```

Or run unit tests:
```bash
python -m unittest tests/test_cases.py
```

Results are saved to `results/` directory. Configuration can be adjusted in `config/test_config.yaml`.

### Error Simulation

To test error handling capabilities with simulated measurement failures:

```bash
python examples/error_simulation_demo.py
```

This demonstrates how the framework handles:
- Measurement timeouts
- Corrupt data responses
- Connection failures
- Empty responses
- Invalid measurement values

The error simulator can be integrated into tests by configuring error rates and failure types.

### Comparing Ammeter Accuracy

To compare results across different ammeter types and identify the most reliable:

```bash
python src/utils/ammeter_comparison.py
```

This generates a summary report showing:
- Statistics for each ammeter type (mean, std dev, consistency)
- Reliability scores based on precision and outlier frequency
- Identification of the most reliable ammeter

Or use programmatically:
```python
from test_qa.utils.ammeter_comparison import AmmeterComparison

comparison = AmmeterComparison()

# Get summary report
print(comparison.generate_summary_report())

# Find specific tests
greenlee_tests = comparison.find_tests(ammeter_type="greenlee")

# Compare specific test runs
results = comparison.compare_tests(["test-id-1", "test-id-2"])
```

See [FIXES.md](FIXES.md) for bugs found and fixed.

---

## Adding a New Ammeter Emulator

To add a new ammeter emulator (e.g., "KUKU"), follow these steps:

### 1. Create the Emulator Class

Create a new file `src/test_qa/ammeters/kuku_ammeter.py`:

```python
from test_qa.ammeters.base_ammeter import BaseAmmeter
from test_qa.utils.utils import generate_random_float


class KukuAmmeter(BaseAmmeter):
    @property
    def get_current_command(self) -> bytes:
        # Define the unique command to get current from KUKU
        return b'MEASURE_KUKU -read_current'

    def measure_current(self) -> float:
        # Implement your measurement logic here
        # Example: Temperature-based sensor
        temperature = generate_random_float(20.0, 80.0)  # Temperature (20-80°C)
        coefficient = generate_random_float(0.05, 0.15)  # Temp coefficient
        current = temperature * coefficient
        print(
            f"KUKU Ammeter - Temperature: {temperature}°C, Coefficient: {coefficient}, Current: {current}A")
        return current
```

**Requirements:**
- Inherit from `BaseAmmeter`
- Implement `get_current_command` property (returns unique command bytes)
- Implement `measure_current()` method (returns float)
- Use a different measurement principle for variety

### 2. Register in Package

Update `src/test_qa/ammeters/__init__.py`:

```python
from .kuku_ammeter import KukuAmmeter

__all__ = [
    'BaseAmmeter',
    'CircutorAmmeter',
    'EntesAmmeter',
    'GreenleeAmmeter',
    'KukuAmmeter',  # Add here
    'request_current_from_ammeter',
]
```

### 3. Add to Emulator Runner

Update `examples/run_emulators.py`:

```python
from test_qa.ammeters.kuku_ammeter import KukuAmmeter

def run_kuku_emulator():
    kuku = KukuAmmeter(5003)  # Use unique port number
    kuku.start_server()

# In main block:
if __name__ == "__main__":
    threading.Thread(target=run_greenlee_emulator, daemon=True).start()
    threading.Thread(target=run_entes_emulator, daemon=True).start()
    threading.Thread(target=run_circutor_emulator, daemon=True).start()
    threading.Thread(target=run_kuku_emulator, daemon=True).start()  # Add here
```

### 4. Update Test Configuration

Add to `config/test_config.yaml`:

```yaml
ammeters:
  greenlee:
    port: 5000
    command: "MEASURE_GREENLEE -get_measurement"
  entes:
    port: 5001
    command: "MEASURE_ENTES -get_data"
  circutor:
    port: 5002
    command: "MEASURE_CIRCUTOR -get_measurement -current"
  kuku:  # Add this section
    port: 5003
    command: "MEASURE_KUKU -read_current"
```

### 5. Update Test Cases

Update `tests/test_cases.py`:

**Import the runner function:**
```python
from examples.run_emulators import (
    run_greenlee_emulator,
    run_entes_emulator,
    run_circutor_emulator,
    run_kuku_emulator,  # Add import
)
```

**Add to test setup:**
```python
@classmethod
def setUpClass(cls):
    cls.threads = [
        threading.Thread(target=run_greenlee_emulator, daemon=True),
        threading.Thread(target=run_entes_emulator, daemon=True),
        threading.Thread(target=run_circutor_emulator, daemon=True),
        threading.Thread(target=run_kuku_emulator, daemon=True)  # Add thread
    ]
```

**Add test method:**
```python
def test_kuku_measurements(self):
    """
    Testing KUKU measurements
    """
    results = self.framework.run_test("kuku")
    self.assertIn("metadata", results)
    self.assertIn("measurements", results)
    self.assertIn("analysis", results)
    
    # Verify measurement range based on your formula
    for measurement in results["measurements"]:
        self.assertGreater(measurement["value"], 0)
        self.assertLess(measurement["value"], 15)  # Adjust based on expected range
```

### Summary Checklist

- [ ] Create ammeter class file
- [ ] Register in `__init__.py`
- [ ] Add runner function in `run_emulators.py`
- [ ] Start thread in `run_emulators.py` main
- [ ] Add configuration in `test_config.yaml`
- [ ] Import runner in `test_cases.py`
- [ ] Add thread in test setup
- [ ] Add test method


The framework validates ammeter types against the configuration, so all steps are required for proper integration.
