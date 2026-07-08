import json


def load_client_profile(path):

    with open(path, "r") as file:
        return json.load(file)
