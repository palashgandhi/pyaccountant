import configparser
import json
import os


class PyAccountantOptions(object):

    @staticmethod
    def store_plaid_item_credentials(plaid_item):
        config = configparser.ConfigParser()
        defaults_file = os.path.abspath(os.path.join(__file__, "..", "..", "defaults.ini"))
        config.read(defaults_file)

        print("Saving plaid item credentials for {}".format(plaid_item.item_id))
        with open(config.get("PLAID", "CREDENTIALS_JSON_PATH"), "w+") as creds_file:
            credentials = json.load(creds_file)
            if plaid_item.item_id not in credentials:
                credentials[plaid_item.item_id] = {
                    "public_token": plaid_item.public_token, "access_token": plaid_item.access_token
                }
            json.dump(credentials, creds_file)


options = PyAccountantOptions()
