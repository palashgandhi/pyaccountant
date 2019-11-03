import configparser
import json
import os


class PyAccountantOptions(object):
    @staticmethod
    def store_plaid_item_credentials(plaid_item):
        config = configparser.ConfigParser()
        defaults_file = os.path.abspath(
            os.path.join(__file__, "..", "..", "defaults.ini")
        )
        config.read(defaults_file)

        credentials_file_path = config.get("PLAID", "CREDENTIALS_JSON_PATH")
        credentials_file_exists = os.path.exists(credentials_file_path)
        credentials = {}
        if credentials_file_exists:
            with open(credentials_file_path, "r") as credentials_file:
                credentials = json.load(credentials_file)
        print("Saving plaid item credentials for {} to {}".format(plaid_item.item_id, credentials_file_path))
        with open(credentials_file_path, "w+") as credentials_file:
            if "plaid_items" not in credentials:
                credentials["plaid_items"] = []
            if plaid_item.item_id not in credentials["plaid_items"]:
                credentials["plaid_items"].append(
                    {
                        "id": plaid_item.item_id,
                        "public_token": plaid_item.public_token,
                        "access_token": plaid_item.access_token,
                    }
                )
            json.dump(credentials, credentials_file)

    @staticmethod
    def get_existing_plaid_item_credentials():
        config = configparser.ConfigParser()
        defaults_file = os.path.abspath(
            os.path.join(__file__, "..", "..", "defaults.ini")
        )
        config.read(defaults_file)

        credentials_file_path = config.get("PLAID", "CREDENTIALS_JSON_PATH")
        if not os.path.exists(credentials_file_path):
            return None
        print("Reading all existing plaid items from credentials file at {}".format(credentials_file_path))
        with open(credentials_file_path, "r") as credentials_file:
            return json.load(credentials_file)["plaid_items"]


options = PyAccountantOptions()
