import time
from typing import List, Dict, Optional
import threading
import queue
from .error_simulator import ErrorSimulator


class DataCollector:
    def __init__(self, config: Dict, error_simulator: Optional[ErrorSimulator] = None):
        self.config = config
        self.measurement_queue = queue.Queue()
        self.error_simulator = error_simulator
        self.errors_encountered = []

    def collect_measurements(self, ammeter_type: str, test_id: str) -> List[Dict]:
        """
        איסוף מדידות מהאמפרמטר
        """
        measurements = []
        sampling_config = self.config["testing"]["sampling"]

        # חישוב מרווח הזמן בין דגימות
        interval = 1.0 / sampling_config["sampling_frequency_hz"]
        total_measurements = sampling_config["measurements_count"]

        # הפעלת תהליכון נפרד לדגימה
        sampling_thread = threading.Thread(
            target=self._sampling_worker,
            args=(ammeter_type, interval, total_measurements)
        )
        sampling_thread.start()

        # איסוף התוצאות
        for _ in range(total_measurements):
            measurement = self.measurement_queue.get()
            measurements.append({
                "timestamp": time.time(),
                "value": measurement,
                "test_id": test_id
            })

        sampling_thread.join()
        return measurements

    def _sampling_worker(self, ammeter_type: str, interval: float, total_measurements: int):
        """
        עובד שאוסף את המדידות בתהליכון נפרד
        """
        ammeter_config = self.config["ammeters"][ammeter_type]

        for _ in range(total_measurements):
            start_time = time.time()

            # קבלת מדידה מהאמפרמטר
            # כאן צריך להשתמש בקוד הקיים של האמפרמטרים
            measurement = self._get_measurement(ammeter_type, ammeter_config)

            self.measurement_queue.put(measurement)

            # המתנה עד לדגימה הבאה
            elapsed = time.time() - start_time
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def _get_measurement(self, ammeter_type: str, config: Dict) -> float:
        """
        קבלת מדידה מהאמפרמטר הספציפי
        """
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
                    value = float(data.decode('utf-8'))

                    # Apply error simulation if enabled
                    if self.error_simulator:
                        try:
                            value = self.error_simulator.inject_error(value)
                            if value is None:
                                raise ValueError(
                                    "Empty response from error simulator")
                            if not isinstance(value, (int, float)):
                                raise ValueError(
                                    f"Invalid data type from error simulator: {type(value)}")
                        except (TimeoutError, ConnectionRefusedError, ValueError) as e:
                            # Log error but allow retry mechanism to handle it
                            error_info = {
                                "ammeter_type": ammeter_type,
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "timestamp": time.time()
                            }
                            self.errors_encountered.append(error_info)
                            raise

                    return value
                else:
                    raise ValueError(f"No data received from {ammeter_type}")
        except (socket.error, ValueError) as e:
            raise RuntimeError(
                f"Failed to get measurement from {ammeter_type}: {str(e)}")
