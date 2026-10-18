"""First script: confirms that Python runs inside the project's virtual environment."""

import sys


def main() -> None:
    print("Hello from AI Test Copilot!")
    print("Python version:", sys.version.split()[0])
    print("Running inside:", sys.prefix)


if __name__ == "__main__":
    main()

# python hello.py
