from test_qa.ammeters.base_ammeter import BaseAmmeter
from test_qa.utils.utils import generate_random_float


class EntesAmmeter(BaseAmmeter):
    @property
    def get_current_command(self) -> bytes:
        # Define the command to get the current from ENTES
        return b'MEASURE_ENTES -get_data'

    def measure_current(self) -> float:
        # Magnetic field strength (0.01T - 0.1T)
        magnetic_field = generate_random_float(0.01, 0.1)
        calibration_factor = generate_random_float(
            500, 2000)  # Calibration factor (500 - 2000)
        current = magnetic_field * calibration_factor
        print(
            f"ENTES Ammeter - Magnetic Field: {magnetic_field}T, Calibration Factor: {calibration_factor}, Current: {current}A")
        return current
