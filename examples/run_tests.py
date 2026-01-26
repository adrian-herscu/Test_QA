import sys
import os

# Check Python version
if sys.version_info < (3, 13):
    print("Error: This project requires Python 3.13 or higher.")
    print(f"Current version: {sys.version}")
    print("\nThe dependencies (numpy 2.4.1, scipy 1.17.0, etc.) require Python 3.13+.")
    print("Please upgrade your Python version or use a compatible virtual environment.")
    sys.exit(1)

from test_qa.testing.test_framework import AmmeterTestFramework


def main():
    # יצירת מסגרת הבדיקות
    framework = AmmeterTestFramework()

    # הרצת בדיקות לכל סוגי האמפרמטרים
    ammeter_types = ["greenlee", "entes", "circutor"]
    results = {}

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
