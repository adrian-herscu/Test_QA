import random
from typing import Optional, Dict, Any
from enum import Enum


class ErrorType(Enum):
    """Types of errors that can be simulated"""
    TIMEOUT = "timeout"
    CORRUPT_DATA = "corrupt_data"
    CONNECTION_REFUSED = "connection_refused"
    EMPTY_RESPONSE = "empty_response"
    INVALID_VALUE = "invalid_value"


class ErrorSimulator:
    """
    Simulates various measurement errors for testing error handling capabilities
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize error simulator

        Args:
            config: Configuration dict with error probabilities
                {
                    "enabled": True/False,
                    "error_rate": 0.1,  # 10% error rate
                    "error_types": {
                        "timeout": 0.3,
                        "corrupt_data": 0.4,
                        "connection_refused": 0.1,
                        "empty_response": 0.1,
                        "invalid_value": 0.1
                    }
                }
        """
        if config is None:
            config = {
                "enabled": False,
                "error_rate": 0.1,
                "error_types": {
                    "timeout": 0.3,
                    "corrupt_data": 0.4,
                    "connection_refused": 0.1,
                    "empty_response": 0.1,
                    "invalid_value": 0.1
                }
            }

        self.enabled = config.get("enabled", False)
        self.error_rate = config.get("error_rate", 0.1)
        self.error_types = config.get("error_types", {})
        self.error_count = 0
        self.total_calls = 0

    def should_inject_error(self) -> bool:
        """Determine if an error should be injected based on error_rate"""
        self.total_calls += 1

        if not self.enabled:
            return False

        return random.random() < self.error_rate

    def get_error_type(self) -> ErrorType:
        """Select which type of error to inject based on configured probabilities"""
        error_weights: list[float] = []
        error_values: list[ErrorType] = []

        for error_name, probability in self.error_types.items():
            try:
                error_values.append(ErrorType[error_name.upper()])
                error_weights.append(probability)
            except KeyError:
                continue

        # Normalize weights to sum to 1.0
        total_weight = sum(error_weights)
        if total_weight > 0:
            error_weights = [w / total_weight for w in error_weights]

        return random.choices(error_values, weights=error_weights)[0]

    def inject_error(self, data: Any) -> Any:
        """
        Inject an error into measurement data

        Args:
            data: The measurement data to potentially corrupt

        Returns:
            Modified data or raises exception

        Raises:
            TimeoutError: Simulates timeout
            ConnectionRefusedError: Simulates connection failure
            ValueError: Simulates invalid/corrupt data
        """
        if not self.should_inject_error():
            return data

        self.error_count += 1
        error_type = self.get_error_type()

        if error_type == ErrorType.TIMEOUT:
            raise TimeoutError("Simulated measurement timeout")

        elif error_type == ErrorType.CONNECTION_REFUSED:
            raise ConnectionRefusedError("Simulated connection refused")

        elif error_type == ErrorType.EMPTY_RESPONSE:
            return None

        elif error_type == ErrorType.CORRUPT_DATA:
            # Return invalid data type
            return "CORRUPT_DATA_NOT_A_FLOAT"

        elif error_type == ErrorType.INVALID_VALUE:
            # Return out-of-range value
            return -999.99

        return data

    def get_statistics(self) -> Dict[str, Any]:
        """Get error injection statistics"""
        return {
            "total_calls": self.total_calls,
            "errors_injected": self.error_count,
            "error_rate_actual": self.error_count / self.total_calls if self.total_calls > 0 else 0,
            "error_rate_configured": self.error_rate,
            "enabled": self.enabled
        }
