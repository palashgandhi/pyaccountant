from pyaccountant.utils.options import options


class PlaidItem:
    def __init__(self, plaid_client, public_token, access_token, item_id):
        self.plaid_client = plaid_client
        self.public_token = public_token
        self.access_token = access_token
        self.item_id = item_id
        self.institution_id = plaid_client.Item.get(access_token)["item"][
            "institution_id"
        ]
        self.institution_name = plaid_client.Institutions.get_by_id(
            self.institution_id
        )["institution"]["name"]

    def save_plaid_item_credentials(self):
        """
        Saves the plaid Item credentials in the credentials file.
        """
        options.store_plaid_item_credentials(self)

    def get_identity(self):
        """
        Retrieve Identity data for an Item
        https://plaid.com/docs/#identity

        :return: The identity data for the item.
        :rtype: ``dict``
        """
        print("Fetching identity data of item {}.".format(self.institution_name))
        return self.plaid_client.Identity.get(self.access_token)

    def get_balance(self):
        """
        Retrieve real-time balance data for each of an Item's accounts
        https://plaid.com/docs/#balance

        :return: The balance data of the item.
        :rtype: ``dict``
        """
        print("Fetching balance of accounts for item {}.".format(self.institution_name))
        return self.plaid_client.Accounts.balance.get(self.access_token)

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
        print(
            "Fetching transactions for item {} from {} to {}...".format(
                self.institution_name, start_date, end_date
            )
        )
        return self.plaid_client.Transactions.get(
            self.access_token, start_date, end_date
        )
