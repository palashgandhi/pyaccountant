import configparser
import json
import os


class PyAccountantOptions(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        defaults_file = os.path.abspath(
            os.path.join(__file__, "..", "..", "defaults.ini")
        )
        self.config.read(defaults_file)

    def get_option(self, section, option):
        """
        Returns the value of the key from the section.

        :param section: The section in which to look for.
        :type section: ``str``
        :param option: The option to fetch.
        :type option: ``str``
        :return: The option value.
        :rtype: ``str``
        """
        return self.config.get(section, option)

    def store_plaid_item_credentials(self, plaid_item):
        """
        Stores the plaid credentials of an item
        :param plaid_item:
        :return:
        """
        credentials_file_path = self.get_option("PLAID", "CREDENTIALS_JSON_PATH")
        credentials_file_exists = os.path.exists(credentials_file_path)
        credentials = {}
        if credentials_file_exists:
            with open(credentials_file_path, "r") as credentials_file:
                credentials = json.load(credentials_file)
        print(
            "Saving plaid item credentials for {} to {}".format(
                plaid_item.item_id, credentials_file_path
            )
        )
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

    def get_existing_plaid_item_credentials(self):
        credentials_file_path = self.get_option("PLAID", "CREDENTIALS_JSON_PATH")
        if not os.path.exists(credentials_file_path):
            return None
        print(
            "Reading all existing plaid items from credentials file at {}".format(
                credentials_file_path
            )
        )
        with open(credentials_file_path, "r") as credentials_file:
            return json.load(credentials_file)["plaid_items"]


options = PyAccountantOptions()
