import sys
from typing import Any, Dict

# Check Python version
if sys.version_info < (3, 10):
    print("Error: This project requires Python 3.10 or higher.")
    print(f"Current version: {sys.version}")
    print("\nThe project uses Python 3.10+ features (like union type syntax with |).")
    print("Please upgrade your Python version or use a compatible virtual environment.")
    sys.exit(1)

from test_qa.testing.test_framework import AmmeterTestFramework


def main():
    # יצירת מסגרת הבדיקות
    framework = AmmeterTestFramework()

    # הרצת בדיקות לכל סוגי האמפרמטרים
    ammeter_types = ["greenlee", "entes", "circutor"]
    results: Dict[str, Dict[str, Any]] = {}

    for ammeter_type in ammeter_types:
        print(f"Testing {ammeter_type} ammeter...")
        results[ammeter_type] = framework.run_test(ammeter_type)

    # השוואת תוצאות
    for ammeter_type, result in results.items():
        print(f"\nResults for {ammeter_type}:")
        print(f"Mean current: {result['analysis']['mean']:.3f} A")
        print(f"Standard deviation: {result['analysis']['std_dev']:.3f} A")


if __name__ == "__main__":
    main()
