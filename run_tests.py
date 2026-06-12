"""
run_tests.py
============
Convenience runner script — executes the full QA login test suite
and prints a summarised result table to the console.

Usage:
    # Run all tests (headed browser):
    python run_tests.py

    # Run headless (CI-friendly):
    python run_tests.py --headless

    # Run only a specific suite:
    python run_tests.py --suite ui
    python run_tests.py --suite positive
    python run_tests.py --suite negative
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="QA Login Test Runner")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode (no window shown)",
    )
    parser.add_argument(
        "--suite",
        choices=["ui", "positive", "negative", "all"],
        default="all",
        help="Which test suite to run (default: all)",
    )
    args = parser.parse_args()

    # Map suite name → file
    suite_map = {
        "ui":       "tests/test_ui_elements.py",
        "positive": "tests/test_positive_login.py",
        "negative": "tests/test_negative_login.py",
        "all":      "tests/",
    }

    # ── Build pytest command ───────────────────────────────────────────
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join("reports", f"report_{timestamp}.html")
    os.makedirs("reports", exist_ok=True)

    cmd = [
        sys.executable, "-m", "pytest",
        suite_map[args.suite],
        "-v",
        "-s",
        "--tb=short",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    if args.headless:
        cmd.append("--headless")

    # ── Banner ─────────────────────────────────────────────────────────
    print("\n" + "═" * 65)
    print("  🧪  QA LOGIN TEST SUITE  —  qa-test-manager.netlify.app")
    print("═" * 65)
    print(f"  Suite   : {args.suite.upper()}")
    print(f"  Mode    : {'Headless' if args.headless else 'Headed (browser visible)'}")
    print(f"  Report  : {report_path}")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 65 + "\n")

    # ── Run tests ──────────────────────────────────────────────────────
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))

    # ── Footer ─────────────────────────────────────────────────────────
    print("\n" + "═" * 65)
    if result.returncode == 0:
        print("  ✅  All tests PASSED")
    else:
        print("  ❌  Some tests FAILED — review the report above")
    print(f"  📊  Full HTML report: {os.path.abspath(report_path)}")
    print("═" * 65 + "\n")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
