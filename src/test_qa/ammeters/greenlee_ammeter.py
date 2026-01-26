from test_qa.ammeters.base_ammeter import BaseAmmeter
from test_qa.utils.utils import generate_random_float


class GreenleeAmmeter(BaseAmmeter):
    @property
    def get_current_command(self) -> bytes:
        # Define the command to get the current from Greenlee
        return b'MEASURE_GREENLEE -get_measurement'

    def measure_current(self) -> float:
        voltage = generate_random_float(1.0, 10.0)  # Random voltage (1V - 10V)
        # Random resistance (0.1Ω - 100Ω)
        resistance = generate_random_float(0.1, 100.0)
        current = voltage / resistance
        print(
            f"Greenlee Ammeter - Voltage: {voltage}V, Resistance: {resistance}Ω, Current: {current}A")
        return current
