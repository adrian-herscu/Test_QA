import sys

# Check Python version
if sys.version_info < (3, 10):
    print("Error: This project requires Python 3.10 or higher.")
    print(f"Current version: {sys.version}")
    print("\nThe project uses Python 3.10+ features (like union type syntax with |).")
    print("Please upgrade your Python version or use a compatible virtual environment.")
    sys.exit(1)

import threading
import time

from test_qa.ammeters.circutor_ammeter import CircutorAmmeter
from test_qa.ammeters.entes_ammeter import EntesAmmeter
from test_qa.ammeters.greenlee_ammeter import GreenleeAmmeter


def run_greenlee_emulator():
    greenlee = GreenleeAmmeter(5000)
    greenlee.start_server()


def run_entes_emulator():
    entes = EntesAmmeter(5001)
    entes.start_server()


def run_circutor_emulator():
    circutor = CircutorAmmeter(5002)
    circutor.start_server()


if __name__ == "__main__":
    # Start each ammeter in a separate thread
    threading.Thread(target=run_greenlee_emulator, daemon=True).start()
    threading.Thread(target=run_entes_emulator, daemon=True).start()
    threading.Thread(target=run_circutor_emulator, daemon=True).start()

    # Wait for the servers to start
    time.sleep(2)
    print("\nAmmeter emulators are running. Press Ctrl+C to stop.\n")

    # Optional: Test with a single measurement to verify connectivity
    # from test_qa.ammeters.client import request_current_from_ammeter
    # request_current_from_ammeter(5000, b'MEASURE_GREENLEE -get_measurement')
    # request_current_from_ammeter(5001, b'MEASURE_ENTES -get_data')
    # request_current_from_ammeter(5002, b'MEASURE_CIRCUTOR -get_measurement -current')

    # Keep the program running to serve requests from the testing framework
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down emulators...")
