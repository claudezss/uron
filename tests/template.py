import json


def sample_func() -> None:
    import requests

    print(requests.__version__)

    with open("./result.json", "+w") as f:
        json.dump({"version": requests.__version__}, f)


if __name__ == "__main__":
    sample_func()
