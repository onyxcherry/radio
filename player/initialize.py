from src.infrastructure.persistence import dbinit


def main():
    dbinit.main()


if __name__ == "__main__":
    main()
    print("Initialized player successfully")
