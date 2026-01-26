# Ammeter Emulators

This project provides emulators for different types of ammeters: Greenlee, ENTES, and CIRCUTOR. Each ammeter emulator runs on a separate thread and can respond to current measurement requests.

## Project Structure

- `Ammeters/`
  - `main.py`: Main script to start the ammeter emulators and request current measurements.
  - `Circutor_Ammeter.py`: Emulator for the CIRCUTOR ammeter.
  - `Entes_Ammeter.py`: Emulator for the ENTES ammeter.
  - `Greenlee_Ammeter.py`: Emulator for the Greenlee ammeter.
  - `base_ammeter.py`: Base class for all ammeter emulators.
  - `client.py`: Client to request current measurements from the ammeter emulators.
- `Utiles/`
  - `Utils.py`: Utility functions, including `generate_random_float`.

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

To start the ammeter emulators and request current measurements, run the `main.py` script:
```sh
python main.py
```

---

## Testing Framework

### Installation

**Requirements**: Python 3.13 or higher

Install the project in development mode:
```bash
pip install -e .
```

This will install all dependencies and make the project modules importable.

### Running Tests

1. Start the ammeter emulators:
```bash
python main.py
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
from src.utils.ammeter_comparison import AmmeterComparison

comparison = AmmeterComparison()

# Get summary report
print(comparison.generate_summary_report())

# Find specific tests
greenlee_tests = comparison.find_tests(ammeter_type="greenlee")

# Compare specific test runs
results = comparison.compare_tests(["test-id-1", "test-id-2"])
```

See [FIXES.md](FIXES.md) for bugs found and fixed.