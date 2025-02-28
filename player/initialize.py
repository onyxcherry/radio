from bootstrap import bootstrap_config
from src.infrastructure.persistence import dbinit


def main():
    bootstrap_config()
    dbinit.main()


if __name__ == "__main__":
    main()
    print("Initialized player successfully")
