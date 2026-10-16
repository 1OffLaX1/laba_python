from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    failed = []
    for number in range(6, 10):
        print(f"\n=== Практика {number}, вариант 7 ===", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-v"],
            cwd=root / f"Практика {number}")
        if result.returncode:
            failed.append(number)
    if failed:
        print("Не прошли проверку:", failed)
        return 1
    print("\nВсе автоматические тесты прошли проверку.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
