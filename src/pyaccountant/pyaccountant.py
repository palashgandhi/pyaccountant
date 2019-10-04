import argparse


class PyAccountant(object):
    pass


def create_parser():
    parser = argparse.ArgumentParser(description="Start pyaccountant locally")
    parser.add_argument(
        "-p",
        "--port",
        default=5000,
        help="The port that the flask app should use. (Default: '{}')".format(5000)
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    accountant = PyAccountant()
