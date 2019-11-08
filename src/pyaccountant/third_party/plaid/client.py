import datetime

from plaid import Client, errors

from pyaccountant.utils.options import options


class PlaidItem(object):
    def __init__(self, plaid_client, public_token, access_token, item_id):
        self.plaid_client = plaid_client
        self.public_token = public_token
        self.access_token = access_token
        self.item_id = item_id
        self.institution_id = plaid_client.Item.get(access_token)["item"]["institution_id"]
        self.institution_name = plaid_client.Institutions.get_by_id(self.institution_id)["institution"]["name"]

    def save_plaid_item_credentials(self):
        options.store_plaid_item_credentials(self)

    def get_identity(self):
        """
        Retrieve Identity data for an Item
        https://plaid.com/docs/#identity

        :return:
        """
        try:
            identity_response = self.plaid_client.Identity.get(self.access_token)
        except errors.PlaidError as e:
            raise Exception({
                "error": {
                    "display_message": e.display_message,
                    "error_code": e.code,
                    "error_type": e.type,
                }
            })
        return {"error": None, "identity": identity_response}

    def get_balance(self):
        """
        Retrieve real-time balance data for each of an Item's accounts
        https://plaid.com/docs/#balance

        :return:
        """
        try:
            balance_response = self.plaid_client.Accounts.balance.get(self.access_token)
        except errors.PlaidError as e:
            raise Exception({
                "error": {
                    "display_message": e.display_message,
                    "error_code": e.code,
                    "error_type": e.type,
                }
            })
        return {"error": None, "balance": balance_response}

    def get_accounts(self):
        """
        Retrieve an Item's accounts
        https://plaid.com/docs/#accounts

        :return:
        """
        try:
            accounts_response = self.plaid_client.Accounts.get(self.access_token)
        except errors.PlaidError as e:
            raise Exception({
                "error": {
                    "display_message": e.display_message,
                    "error_code": e.code,
                    "error_type": e.type,
                }
            })
        return accounts_response["accounts"]

    def get_transactions(
        self,
        start_date="{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30)),
        end_date="{:%Y-%m-%d}".format(datetime.datetime.now())
    ):
        """
        Retrieve Transactions for an Item
        https://plaid.com/docs/#transactions

        :return:
        """
        print("Fetching transactions for item {} from {} to {}...".format(self.institution_name, start_date, end_date))
        return self.plaid_client.Transactions.get(
            self.access_token, start_date, end_date
        )


class PlaidAccountant(object):
    def __init__(self):
        self.client_id = "5d97d9a5f75ad900116dc7a6"
        self.public_key = "1ee26b4daa8011009b7c3d3cea4d58"
        self.secret = "17fcd7d3955fbc23b8012ff078af78"
        self.env = "development"
        self.country_codes = "US,CA,GB,FR,ES"

        self.products = "transactions"
        self.client = Client(
            client_id=self.client_id,
            secret=self.secret,
            public_key=self.public_key,
            environment=self.env,
        )
        self.plaid_items = set()
        self.get_existing_plaid_items_from_credentials_file()

    def get_access_token(self, public_token):
        """
        Exchange token flow - exchange a Link public_token for
        an API access_token
        https://plaid.com/docs/#exchange-token-flow

        :param public_token: The public token of a Plaid `Item`.
        :type public_token: ``str```
        :return:
        """
        try:
            exchange_response = self.client.Item.public_token.exchange(public_token)
        except errors.PlaidError as e:
            raise e

        item = self.client.Item.get(exchange_response["access_token"])
        plaid_item = PlaidItem(
            self.client, public_token, exchange_response["access_token"], item["item"]["item_id"]
        )
        plaid_item.save_plaid_item_credentials()
        self.plaid_items.add(plaid_item)

    def get_plaid_item(self, item_id):
        """
        Returns a plaid item from the list of connected items.

        :param item_id:
        :return:
        """
        for item in self.plaid_items:
            if item.item_id == item_id:
                return item

    def get_accounts_of_all_items(self):
        """
        Returns all the accounts of all plaid items.
        """
        accounts = []
        for item in self.plaid_items:
            accounts.extend(item.get_accounts())
        return accounts

    def get_transactions_of_all_items(self):
        all_transactions = []
        for item in self.plaid_items:
            transactions = item.get_transactions()
            transactions["item_id"] = item.item_id
            all_transactions.append(transactions)
        return all_transactions

    def get_existing_plaid_items_from_credentials_file(self):
        existing_items = options.get_existing_plaid_item_credentials()
        if existing_items is None:
            return None
        for item in existing_items:
            self.plaid_items.add(
                PlaidItem(
                    self.client, item["public_token"], item["access_token"], item["id"]
                )
            )
