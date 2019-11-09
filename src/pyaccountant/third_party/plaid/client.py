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
        """
        Saves the plaid Item credentials in the credentials file.
        """
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

        :return: The list of dictionaries of each account in current item.
        :rtype: ``list`` of ``dict``
        """
        print("Fetching accounts for item {}.".format(self.institution_name))
        return self.plaid_client.Accounts.get(self.access_token)["accounts"]

    def get_transactions(self, start_date, end_date):
        """
        Retrieve Transactions for an Item
        https://plaid.com/docs/#transactions

        :param start_date: The date from which to fetch the transactions in the YYYY-MM-DD format.
        :type start_date: ``str``
        :param end_date: The date to which to fetch the transactions in the YYYY-MM-DD format.
        :type end_date: ``str``
        :return: The transactions of each account in this item.
        :rtyppe: ```dict``
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
        self.initialize_existing_plaid_items_from_credentials_file()

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

        :param item_id: The Item ID.
        :type item_id: ``str``
        :return: The Item object corresponding to the ID.
        :rtype: :py:class:`Item`
        """
        for item in self.plaid_items:
            if item.item_id == item_id:
                return item

    def get_accounts_of_all_items(self):
        """
        Returns all the accounts of all plaid items.

        :return: List of accounts of each known item.
        :rtype: ``list`` of ``dict``
        """
        accounts = []
        for item in self.plaid_items:
            accounts.extend(item.get_accounts())
        return accounts

    def get_transactions_of_all_items(
        self,
        start_date="{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30)),
        end_date="{:%Y-%m-%d}".format(datetime.datetime.now())
    ):
        """
        Returns the transactions of all items.

        :param start_date: The date from which to fetch the transactions in the YYYY-MM-DD format.
        :type start_date: ``str``
        :param end_date: The date to which to fetch the transactions in the YYYY-MM-DD format.
        :type end_date: ``str``
        :return: The list of transactions of each item.
        :rtyppe: ``list`` of ``dict``
        """
        all_transactions = []
        for item in self.plaid_items:
            transactions = item.get_transactions(start_date, end_date)
            transactions["item_id"] = item.item_id
            all_transactions.append(transactions)
        return all_transactions

    def initialize_existing_plaid_items_from_credentials_file(self):
        """
        Parses the credentials file and initializes the Item objects for each item in the file.
        """
        existing_items = options.get_existing_plaid_item_credentials()
        if existing_items is None:
            return None
        for item in existing_items:
            self.plaid_items.add(
                PlaidItem(
                    self.client, item["public_token"], item["access_token"], item["id"]
                )
            )
