import subprocess


def run_black():
    """Run black to format Python files."""
    print("Running Black formatter...")
    subprocess.run(["black", "src/"], check=True)


def run_pylint():
    """Run pylint to check for linting errors."""
    print("Running Pylint...")
    result = subprocess.run(["pylint", "src/"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Lint errors detected. Fix them before proceeding.")
        exit(result.returncode)


if __name__ == "__main__":
    print("Starting formatting and linting...")
    try:
        run_black()
        run_pylint()
        print("Formatting and linting complete. No issues found!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        exit(1)
