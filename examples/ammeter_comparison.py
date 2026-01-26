import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np


class AmmeterComparison:
    """Compare ammeter accuracy and analyze historical test results"""

    def __init__(self, results_path: str = "results/"):
        self.results_path = results_path

    def load_result(self, test_id: str) -> Dict:
        """Load a single test result by ID"""
        filepath = os.path.join(self.results_path, f"{test_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Test result not found: {test_id}")

        with open(filepath, 'r') as f:
            return json.load(f)

    def find_tests(self,
                   ammeter_type: Optional[str] = None,
                   from_date: Optional[str] = None,
                   to_date: Optional[str] = None) -> List[Dict]:
        """
        Find tests matching criteria

        Args:
            ammeter_type: Filter by ammeter type (greenlee, entes, circutor)
            from_date: ISO format date string (e.g., "2026-01-26")
            to_date: ISO format date string

        Returns:
            List of test result dictionaries
        """
        results = []

        # Get all JSON files
        json_files = Path(self.results_path).glob("*.json")

        for filepath in json_files:
            try:
                with open(filepath, 'r') as f:
                    result = json.load(f)
            except json.JSONDecodeError:
                # Skip corrupted/incomplete JSON files
                print(f"Warning: Skipping corrupted file: {filepath.name}")
                continue

            # Apply filters
            if ammeter_type and result['metadata']['ammeter_type'] != ammeter_type.lower():
                continue

            if from_date:
                test_date = result['metadata']['timestamp'].split('T')[0]
                if test_date < from_date:
                    continue

            if to_date:
                test_date = result['metadata']['timestamp'].split('T')[0]
                if test_date > to_date:
                    continue

            results.append(result)

        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['metadata']['timestamp'], reverse=True)
        return results

    def compare_tests(self, test_ids: List[str]) -> Dict:
        """
        Compare multiple tests and return statistical summary

        Args:
            test_ids: List of test IDs to compare

        Returns:
            Comparison dictionary with statistics for each test
        """
        comparison = {
            'test_count': len(test_ids),
            'tests': []
        }

        for test_id in test_ids:
            result = self.load_result(test_id)

            comparison['tests'].append({
                'test_id': test_id,
                'ammeter_type': result['metadata']['ammeter_type'],
                'timestamp': result['metadata']['timestamp'],
                'mean': result['analysis']['mean'],
                'std_dev': result['analysis']['std_dev'],
                'median': result['analysis']['median'],
                'outliers': result['analysis']['outliers_count'],
                'is_normal': result['analysis']['is_normal_distribution']
            })

        return comparison

    def compare_ammeter_types(self) -> Dict:
        """
        Compare all ammeter types to determine relative accuracy

        Returns:
            Dictionary with comparison metrics for each ammeter type
        """
        all_tests = self.find_tests()

        # Group by ammeter type
        by_type = {}
        for test in all_tests:
            ammeter_type = test['metadata']['ammeter_type']
            if ammeter_type not in by_type:
                by_type[ammeter_type] = []
            by_type[ammeter_type].append(test)

        # Calculate aggregate statistics
        comparison = {}
        for ammeter_type, tests in by_type.items():
            means = [t['analysis']['mean'] for t in tests]
            std_devs = [t['analysis']['std_dev'] for t in tests]
            outlier_counts = [t['analysis']['outliers_count'] for t in tests]

            comparison[ammeter_type] = {
                'test_count': len(tests),
                'avg_mean': float(np.mean(means)),
                'avg_std_dev': float(np.mean(std_devs)),
                # Consistency across tests
                'std_dev_of_means': float(np.std(means)),
                'avg_outliers': float(np.mean(outlier_counts)),
                'reliability_score': self._calculate_reliability(std_devs, outlier_counts)
            }

        return comparison

    def _calculate_reliability(self, std_devs: List[float], outliers: List[int]) -> float:
        """
        Calculate reliability score (0-100)
        Lower std_dev and fewer outliers = higher reliability
        """
        avg_std = np.mean(std_devs)
        avg_outliers = np.mean(outliers)

        # Simple scoring: penalize high std dev and outliers
        # This is a simplified metric - could be more sophisticated
        std_penalty = min(avg_std / 10, 50)  # Cap at 50 points
        outlier_penalty = min(avg_outliers * 5, 50)  # Cap at 50 points

        score = 100 - std_penalty - outlier_penalty
        return max(0, float(score))

    def generate_summary_report(self) -> str:
        """Generate a text summary of all test results"""
        all_tests = self.find_tests()

        if not all_tests:
            return "No test results found."

        report = []
        report.append("=" * 60)
        report.append("AMMETER TEST RESULTS SUMMARY")
        report.append("=" * 60)
        report.append(f"\nTotal tests: {len(all_tests)}")

        # Count by type
        by_type = {}
        for test in all_tests:
            ammeter_type = test['metadata']['ammeter_type']
            by_type[ammeter_type] = by_type.get(ammeter_type, 0) + 1

        report.append(f"\nTests by ammeter type:")
        for ammeter_type, count in sorted(by_type.items()):
            report.append(f"  {ammeter_type.upper()}: {count} tests")

        # Ammeter comparison
        report.append(f"\n{'-' * 60}")
        report.append("AMMETER TYPE COMPARISON")
        report.append('-' * 60)

        comparison = self.compare_ammeter_types()
        for ammeter_type, stats in sorted(comparison.items()):
            report.append(f"\n{ammeter_type.upper()}:")
            report.append(f"  Average Mean Current: {stats['avg_mean']:.2f}A")
            report.append(f"  Average Std Dev: {stats['avg_std_dev']:.2f}A")
            report.append(
                f"  Consistency (std of means): {stats['std_dev_of_means']:.2f}A")
            report.append(f"  Average Outliers: {stats['avg_outliers']:.1f}")
            report.append(
                f"  Reliability Score: {stats['reliability_score']:.1f}/100")

        # Most reliable ammeter
        if comparison:
            best_ammeter = max(comparison.items(),
                               key=lambda x: x[1]['reliability_score'])
            report.append(f"\n{'-' * 60}")
            report.append(f"MOST RELIABLE: {best_ammeter[0].upper()} "
                          f"(Score: {best_ammeter[1]['reliability_score']:.1f}/100)")
            report.append('=' * 60)

        return '\n'.join(report)


if __name__ == "__main__":
    # Example usage
    comparison = AmmeterComparison()

    print("\n📊 Generating summary report...\n")
    print(comparison.generate_summary_report())

    print("\n\n🔍 Finding all ENTES tests:")
    entes_tests = comparison.find_tests(ammeter_type="entes")
    for test in entes_tests[:3]:  # Show first 3
        print(
            f"  - {test['metadata']['test_id']}: Mean={test['analysis']['mean']:.2f}A")
