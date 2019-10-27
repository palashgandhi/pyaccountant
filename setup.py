import codecs
import os

import setuptools


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


entrypoints = {"console_scripts": ["pyaccountant = pyaccountant.pyaccountant:main"]}
setuptools.setup(
    name="pyaccountant",
    version="0.1.0",
    description="Make sense of your finances",
    package_dir={"": "src"},
    package=setuptools.find_packages(where="src"),
    include_package_data=True,
    entry_points=entrypoints,
    install_requires=["plaid-python==3.4.0", "flask==1.1.1"],
)
