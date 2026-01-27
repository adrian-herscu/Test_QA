import time
from typing import List, Dict, Optional, Any
import threading
import queue
from .error_simulator import ErrorSimulator


class DataCollector:
    def __init__(self, config: Dict[str, Any], error_simulator: Optional[ErrorSimulator] = None) -> None:
        self.config: Dict[str, Any] = config
        self.measurement_queue: queue.Queue[float] = queue.Queue()
        self.error_simulator: Optional[ErrorSimulator] = error_simulator
        self.errors_encountered: List[Dict[str, Any]] = []

    def collect_measurements(self, ammeter_type: str, test_id: str) -> List[Dict[str, Any]]:
        """
        איסוף מדידות מהאמפרמטר
        """
        measurements: List[Dict[str, Any]] = []
        sampling_config: Dict[str, Any] = self.config["testing"]["sampling"]

        # חישוב מרווח הזמן בין דגימות
        interval: float = 1.0 / float(sampling_config["sampling_frequency_hz"])
        total_measurements: int = int(sampling_config["measurements_count"])

        # הפעלת תהליכון נפרד לדגימה
        sampling_thread = threading.Thread(
            target=self._sampling_worker,
            args=(ammeter_type, interval, total_measurements)
        )
        sampling_thread.start()

        # איסוף התוצאות
        for _ in range(total_measurements):
            measurement: float = self.measurement_queue.get()
            measurements.append({
                "timestamp": time.time(),
                "value": measurement,
                "test_id": test_id
            })

        sampling_thread.join()
        return measurements

    def _sampling_worker(self, ammeter_type: str, interval: float, total_measurements: int) -> None:
        """
        עובד שאוסף את המדידות בתהליכון נפרד
        """
        ammeter_config: Dict[str, Any] = self.config["ammeters"][ammeter_type]

        for _ in range(total_measurements):
            start_time: float = time.time()

            # קבלת מדידה מהאמפרמטר
            # כאן צריך להשתמש בקוד הקיים של האמפרמטרים
            measurement: float = self._get_measurement(
                ammeter_type, ammeter_config)

            self.measurement_queue.put(measurement)

            # המתנה עד לדגימה הבאה
            elapsed: float = time.time() - start_time
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def _get_measurement(self, ammeter_type: str, config: Dict[str, Any]) -> float:
        """
        קבלת מדידה מהאמפרמטר הספציפי
        """
        import socket

        port: int = int(config["port"])
        command: bytes = str(config["command"]).encode('utf-8')

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # 5 second timeout
                s.connect(('localhost', port))
                s.sendall(command)
                data: bytes = s.recv(1024)
                if data:
                    value: float = float(data.decode('utf-8'))

                    # Apply error simulation if enabled
                    if self.error_simulator:
                        try:
                            simulated_value: Any = self.error_simulator.inject_error(
                                value)
                            if simulated_value is None:
                                raise ValueError(
                                    "Empty response from error simulator")
                            if not isinstance(simulated_value, (int, float)):
                                raise ValueError(
                                    f"Invalid data type from error simulator: {type(simulated_value)}")
                            value = float(simulated_value)
                        except (TimeoutError, ConnectionRefusedError, ValueError) as e:
                            # Log error but allow retry mechanism to handle it
                            error_info: Dict[str, Any] = {
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

    def get_single_measurement(self, ammeter_type: str) -> float:
        """Public helper for fetching one measurement from an ammeter."""
        ammeter_config: Dict[str, Any] = self.config["ammeters"][ammeter_type]
        return self._get_measurement(ammeter_type, ammeter_config)
