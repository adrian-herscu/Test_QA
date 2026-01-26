"""
Example demonstrating error simulation capabilities

This example shows how the framework handles various measurement errors:
- Timeouts
- Corrupt data
- Connection failures
- Empty responses
- Invalid values

Run this after starting the ammeter emulators with: python main.py
"""

# fmt: off
# isort: off
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
import time
from src.testing.error_simulator import ErrorSimulator
from src.testing.data_collector import DataCollector
from src.utils.config import load_config

# fmt: on
# isort: on


def run_error_simulation_demo():
    """Demonstrate error handling with simulated failures"""

    print("=" * 60)
    print("ERROR SIMULATION DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo shows how the framework handles measurement errors.\n")

    # Load config
    config = load_config("config/test_config.yaml")

    # Configure error simulator with 20% error rate
    error_config = {
        "enabled": True,
        "error_rate": 0.2,  # 20% of measurements will fail
        "error_types": {
            "timeout": 0.3,
            "corrupt_data": 0.3,
            "connection_refused": 0.1,
            "empty_response": 0.2,
            "invalid_value": 0.1
        }
    }

    error_sim = ErrorSimulator(error_config)
    collector = DataCollector(config, error_simulator=error_sim)

    # Try to collect 20 measurements from each ammeter
    print("Attempting to collect 20 measurements from each ammeter...")
    print("(with 20% simulated error rate)\n")

    for ammeter_type in ["greenlee", "entes", "circutor"]:
        print(f"\n{'-' * 60}")
        print(f"Testing {ammeter_type.upper()} ammeter")
        print('-' * 60)

        successes = 0
        failures = 0

        for i in range(20):
            try:
                ammeter_config = config["ammeters"][ammeter_type]
                measurement = collector._get_measurement(
                    ammeter_type, ammeter_config)
                successes += 1
                print(f"  ✓ Measurement {i+1}: {measurement:.2f}A")
            except Exception as e:
                failures += 1
                print(
                    f"  ✗ Measurement {i+1}: ERROR - {type(e).__name__}: {str(e)[:50]}")

            time.sleep(0.05)  # Small delay between measurements

        print(f"\nResults for {ammeter_type}:")
        print(f"  Successful: {successes}/20 ({successes/20*100:.1f}%)")
        print(f"  Failed: {failures}/20 ({failures/20*100:.1f}%)")

    # Show error statistics
    print(f"\n{'=' * 60}")
    print("ERROR SIMULATOR STATISTICS")
    print('=' * 60)

    stats = error_sim.get_statistics()
    print(f"Total measurement attempts: {stats['total_calls']}")
    print(f"Errors injected: {stats['errors_injected']}")
    print(f"Actual error rate: {stats['error_rate_actual']*100:.1f}%")
    print(f"Configured error rate: {stats['error_rate_configured']*100:.1f}%")

    # Show error breakdown
    if collector.errors_encountered:
        print(f"\nError breakdown by type:")
        error_types = {}
        for error in collector.errors_encountered:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1

        for error_type, count in sorted(error_types.items()):
            print(f"  {error_type}: {count}")

    print(f"\n{'=' * 60}")
    print("CONCLUSION")
    print('=' * 60)
    print("The framework successfully handles measurement errors by:")
    print("  1. Catching exceptions from failed measurements")
    print("  2. Logging error details for debugging")
    print("  3. Allowing the test to continue despite failures")
    print("  4. Providing statistics about error rates")
    print("\nIn production, you could implement retry logic or")
    print("fallback mechanisms based on these error patterns.")
    print('=' * 60)


if __name__ == "__main__":
    print("\nStarting error simulation demo...")
    print("Make sure ammeter emulators are running (python main.py)\n")

    try:
        run_error_simulation_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed: {type(e).__name__}: {str(e)}")
        print("\nMake sure the ammeter emulators are running:")
        print("  python main.py")
