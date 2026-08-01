from brain.developer import Developer
from brain.developer import __version__


def main():

    developer = Developer()

    print("Developer Loaded")

    print("Version:", __version__)

    print(type(developer).__name__)

    print("Foundation OK")


if __name__ == "__main__":

    main()