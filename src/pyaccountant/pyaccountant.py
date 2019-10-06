import argparse
import datetime

import flask
import plaid
from pyaccountant.third_party.plaid import client

app = flask.Flask(__name__)
global plaid_access_token, accountant


class PyAccountant(object):
    def __init__(self):
        self.plaid_client_id = '5d97d9a5f75ad900116dc7a6'
        self.plaid_secret = 'fad459d44f8628407c72d29fa6aefd'
        self.plaid_public_key = '1ee26b4daa8011009b7c3d3cea4d58'
        self.plaid_country_codes = 'US,CA,GB,FR,ES'
        self.plaid_env = 'sandbox'
        self.plaid_products = 'transactions'
        plaid_client = client.PlaidClient(
            client_id=self.plaid_client_id,
            secret=self.plaid_secret,
            public_key=self.plaid_public_key,
            environment=self.plaid_env,
        )
        self.plaid_client = plaid_client.get_client()


def create_parser():
    parser = argparse.ArgumentParser(description="Start pyaccountant locally")
    parser.add_argument(
        "-p",
        "--port",
        default="5000",
        help="The port that the flask app should use. (Default: '{}')".format(5000)
    )
    return parser


@app.route('/')
def index():
    return flask.render_template(
        'index.html',
        plaid_public_key=accountant.plaid_public_key,
        plaid_environment=accountant.plaid_env,
        plaid_products=accountant.plaid_products,
        plaid_country_codes=accountant.plaid_country_codes,
    )


# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    global access_token
    public_token = flask.request.form['public_token']
    try:
        exchange_response = accountant.plaid_client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return flask.jsonify(e)

    print(exchange_response)
    access_token = exchange_response['access_token']
    return flask.jsonify(exchange_response)


@app.route('/set_plaid_access_token', methods=['POST'])
def set_plaid_access_token():
    global plaid_access_token
    plaid_access_token = flask.request.form['access_token']
    item = accountant.plaid_client.Item.get(plaid_access_token)
    return flask.jsonify({'error': None, 'item_id': item['item']['item_id']})


# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions
@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    # Pull transactions for the last 30 days
    start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
    try:
        transactions_response = accountant.plaid_client.Transactions.get(access_token, start_date, end_date)
    except plaid.errors.PlaidError as e:
        return flask.jsonify(e)
    print(transactions_response)
    return flask.jsonify({'error': None, 'transactions': transactions_response})


def main():
    global accountant
    parser = create_parser()
    args = parser.parse_args()
    accountant = PyAccountant()
    print(type(accountant.plaid_client))
    app.run(port=args.port)
