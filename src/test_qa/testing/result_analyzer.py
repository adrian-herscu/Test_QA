import numpy as np
from typing import Any, Dict, List, Tuple, cast
from scipy import stats


class ResultAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = config["analysis"]["statistical_metrics"]

    def analyze(self, measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ניתוח סטטיסטי של המדידות
        """
        values = [m["value"] for m in measurements]
        results: Dict[str, Any] = {}

        # חישוב מדדים סטטיסטיים בסיסיים
        if "mean" in self.metrics:
            results["mean"] = float(np.mean(values))
        if "median" in self.metrics:
            results["median"] = float(np.median(values))
        if "std_dev" in self.metrics:
            results["std_dev"] = float(np.std(values))
        if "min" in self.metrics:
            results["min"] = float(np.min(values))
        if "max" in self.metrics:
            results["max"] = float(np.max(values))

        # ניתוח מתקדם
        results.update(self._advanced_analysis(values))

        return results

    def _advanced_analysis(self, values: List[float]) -> Dict[str, Any]:
        """
        ניתוח סטטיסטי מתקדם
        """
        skewness_value: float = float(stats.skew(values))  # type: ignore[arg-type]
        kurtosis_value: float = float(stats.kurtosis(values))  # type: ignore[arg-type]
        
        ci_tuple: Tuple[float, float] = cast(
            Tuple[float, float],
            stats.t.interval(
                confidence=0.95,
                df=len(values)-1,
                loc=np.mean(values),
                scale=stats.sem(values)
            )
        )
        
        advanced_results: Dict[str, Any] = {
            "skewness": skewness_value,  # א-סימטריה
            "kurtosis": kurtosis_value,  # התפלגות
            "confidence_interval_95": list(ci_tuple),
        }

        # בדיקת נורמליות
        _, normality_p_value = stats.normaltest(values)
        advanced_results["is_normal_distribution"] = bool(
            normality_p_value > 0.05)

        # זיהוי חריגים
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        outlier_bounds = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        outliers = [v for v in values if v <
                    outlier_bounds[0] or v > outlier_bounds[1]]
        advanced_results["outliers_count"] = len(outliers)

        return advanced_results
