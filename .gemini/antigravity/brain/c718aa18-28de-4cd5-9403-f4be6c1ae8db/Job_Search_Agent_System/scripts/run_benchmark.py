#!/usr/bin/env python3
"""
Script de benchmark data-driven — exécute les tests avec métriques de temps.
Usage: python scripts/run_benchmark.py
"""
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_benchmark() -> dict:
    """Lance pytest sur les tests de benchmark et récupère les métriques."""
    start = time.perf_counter()
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_benchmark_matching.py",
            "tests/test_benchmark_atv.py",
            "tests/test_benchmark_sprint.py",
            "tests/test_matching.py",
            "tests/test_orchestrator.py",
            "-v", "--tb=no", "-q",
            "-o", "addopts=",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    elapsed = time.perf_counter() - start
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration_seconds": round(elapsed, 3),
        "passed": result.returncode == 0,
    }


def main():
    print("=== Benchmark Sprint Corrections ===\n")
    data = run_benchmark()
    print(data["stdout"])
    if data["stderr"]:
        print("STDERR:", data["stderr"])
    print(f"\nDurée totale: {data['duration_seconds']}s")
    print(f"Résultat: {'PASSED' if data['passed'] else 'FAILED'}")
    return 0 if data["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
