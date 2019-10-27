import datetime

from plaid import Client
from plaid import errors
from pyaccountant.utils.options import options


class PlaidItem(object):
    def __init__(self, public_token, access_token, item_id):
        self.public_token = public_token
        self.access_token = access_token
        self.item_id = item_id
        self.store_item_credentials()

    def store_item_credentials(self):
        """

        :return:
        """
        options.store_plaid_item_credentials(self)

    def get_identity(self, client):
        """
        Retrieve Identity data for an Item
        https://plaid.com/docs/#identity

        :return:
        """
        try:
            identity_response = client.Identity.get(self.access_token)
        except errors.PlaidError as e:
            return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}}
        return {'error': None, 'identity': identity_response}

    def get_balance(self, client):
        """
        Retrieve real-time balance data for each of an Item's accounts
        https://plaid.com/docs/#balance

        :return:
        """
        try:
            balance_response = client.Accounts.balance.get(self.access_token)
        except errors.PlaidError as e:
            return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}}
        return {'error': None, 'balance': balance_response}

    def get_accounts(self, client):
        """
        Retrieve an Item's accounts
        https://plaid.com/docs/#accounts

        :return:
        """
        try:
            accounts_response = client.Accounts.get(self.access_token)
        except errors.PlaidError as e:
            return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}}
        return {'error': None, 'accounts': accounts_response}

    def get_transactions(self, client, start_date=None, end_date=None):
        """
        Retrieve Transactions for an Item
        https://plaid.com/docs/#transactions

        :return:
        """
        if not start_date:
            # Pull transactions for the last 30 days
            start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
        if not end_date:
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        try:
            transactions_response = client.Transactions.get(self.access_token, start_date, end_date)
        except errors.PlaidError as e:
            raise e
        return {'error': None, 'transactions': transactions_response}


class PlaidAccountant(object):
    def __init__(self):
        self.client_id = '5d97d9a5f75ad900116dc7a6'
        self.public_key = '1ee26b4daa8011009b7c3d3cea4d58'
        self.secret = '17fcd7d3955fbc23b8012ff078af78'
        self.country_codes = 'US,CA,GB,FR,ES'
        self.env = 'development'
        self.products = 'transactions'
        self.client = Client(
            client_id=self.client_id,
            secret=self.secret,
            public_key=self.public_key,
            environment=self.env,
        )
        self.plaid_items = []

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
        self.plaid_items.append(
            PlaidItem(
                public_token, exchange_response["access_token"], item['item']['item_id']
            )
        )

    def get_plaid_item(self, item_id):
        """
        Gets a plaid item from the list of connected items.

        :param item_id:
        :return:
        """
        for item in self.plaid_items:
            if item.item_id == item_id:
                return item

    def get_transactions(self, item_id):
        return self.get_plaid_item(item_id).get_transactions(self.client)

    def get_transactions_of_all_items(self):
        all_transactions = []
        for item in self.plaid_items:
            all_transactions.append(self.get_transactions(item.item_id))
