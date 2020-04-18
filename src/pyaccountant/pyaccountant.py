import argparse

import flask

from pyaccountant.third_party.plaid import client

app = flask.Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.do")


class PyAccountant(object):
    def __init__(self):
        self.plaid_client = client.PlaidAccountant()


def create_parser():
    parser = argparse.ArgumentParser(description="Start pyaccountant")
    parser.add_argument(
        "-p",
        "--port",
        default="5000",
        help="The port that the flask app should use. (Default: '{}')".format(5000),
    )
    return parser


@app.route("/")
def index():
    all_plaid_accounts = accountant.plaid_client.get_accounts_of_all_items()
    all_plaid_transactions = accountant.plaid_client.get_transactions_of_all_items()
    return flask.render_template(
        "index.html",
        all_plaid_accounts=all_plaid_accounts,
        all_plaid_transactions=all_plaid_transactions,
        plaid_public_key=accountant.plaid_client.public_key,
        plaid_environment=accountant.plaid_client.env,
        plaid_products=accountant.plaid_client.products,
        plaid_country_codes=accountant.plaid_client.country_codes,
    )


@app.route("/initialize_plaid_item", methods=["POST"])
def initialize_plaid_item():
    accountant.plaid_client.get_access_token(flask.request.form["public_token"])
    return flask.redirect(flask.url_for("index"))


def main():
    parser = create_parser()
    args = parser.parse_args()
    app.run(port=args.port)


accountant = PyAccountant()
