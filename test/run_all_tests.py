from test_python_project import main as python_test
from test_arduino_project import main as arduino_test
from test_react_project import main as react_test


def main():

    print("=" * 80)
    print("PROJECT INTELLIGENCE TEST SUITE")
    print("=" * 80)

    python_test()

    arduino_test()

    react_test()

    print("\nAll tests finished.")


if __name__ == "__main__":
    main()