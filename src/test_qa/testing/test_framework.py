import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.config import load_config
from .data_collector import DataCollector
from .result_analyzer import ResultAnalyzer
from .visualizer import DataVisualizer


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/test_config.yaml"):
        self.config: Dict[str, Any] = load_config(config_path)
        self.data_collector: DataCollector = DataCollector(self.config)
        self.result_analyzer: ResultAnalyzer = ResultAnalyzer(self.config)
        self.visualizer: DataVisualizer = DataVisualizer(self.config)
        self.test_id: str = str(uuid.uuid4())

    def run_test(self, ammeter_type: str) -> Dict[str, Any]:
        """
        הרצת בדיקה מלאה על אמפרמטר ספציפי
        """
        # Validate ammeter type before starting
        valid_types: List[str] = list(self.config["ammeters"].keys())
        if ammeter_type.lower() not in valid_types:
            raise ValueError(
                f"Invalid ammeter type: {ammeter_type}. Must be one of {valid_types}")

        # איסוף נתונים
        measurements: List[Dict[str, Any]] = self.data_collector.collect_measurements(
            ammeter_type=ammeter_type,
            test_id=self.test_id
        )

        # ניתוח התוצאות
        analysis_results: Dict[str, Any] = self.result_analyzer.analyze(
            measurements)

        # יצירת ויזואליזציה
        if self.config["analysis"]["visualization"]["enabled"]:
            self.visualizer.create_visualizations(
                measurements,
                test_id=self.test_id,
                ammeter_type=ammeter_type
            )

        # הכנת המטא-דאטה
        metadata: Dict[str, Any] = {
            "test_id": self.test_id,
            "timestamp": datetime.now().isoformat(),
            "ammeter_type": ammeter_type,
            "test_duration": self.config["testing"]["sampling"]["total_duration_seconds"],
            "sampling_frequency": self.config["testing"]["sampling"]["sampling_frequency_hz"]
        }

        # שמירת התוצאות
        results: Dict[str, Any] = {
            "metadata": metadata,
            "measurements": measurements,
            "analysis": analysis_results
        }

        self._save_results(results)
        return results

    def _save_results(self, results: Dict[str, Any]) -> None:
        """
        שמירת תוצאות הבדיקה
        """
        import json
        import os

        save_path: str = self.config["result_management"]["save_path"]
        filename: str = f"{save_path}/{results['metadata']['test_id']}.json"

        os.makedirs(save_path, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
