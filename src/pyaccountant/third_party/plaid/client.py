from plaid import Client


class PlaidClient(object):
    def __init__(self, client_id, secret, public_key, environment):
        self.client_id = client_id
        self.secret = secret
        self.public_key = public_key
        self.environment = environment

    def get_client(self):
        """
        Returns a plaid client.

        :return: A plaid Client.
        :rtype: :py:class:`plaid.Client`
        """
        # Available environments are 'sandbox', 'development', and 'production'.
        return Client(
            client_id=self.client_id,
            secret=self.secret,
            public_key=self.public_key,
            environment=self.environment,
        )

    @staticmethod
    def get_transactions(client, public_token):
        response = client.Item.public_token.exchange(public_token)
        access_token = response['access_token']
        response = client.Transactions.get(access_token, start_date='2016-07-12', end_date='2017-01-09')
        transactions = response['transactions']

        # the transactions in the response are paginated, so make multiple calls while increasing the offset to
        # retrieve all transactions
        while len(transactions) < response['total_transactions']:
            response = client.Transactions.get(
                access_token,
                start_date='2016-07-12',
                end_date='2017-01-09',
                offset=len(transactions)
            )
            transactions.extend(response['transactions'])
        return transactions


if __name__ == "__main__":
    plaid_client = PlaidClient(
        client_id='5d97d9a5f75ad900116dc7a6',
        secret='fad459d44f8628407c72d29fa6aefd',
        public_key='1ee26b4daa8011009b7c3d3cea4d58',
        environment='sandbox'
    )
    print(plaid_client.get_transactions("access-sandbox-1be19663-6d3c-4e58-9ab6-1098c24b04ce"))
