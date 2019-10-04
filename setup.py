import codecs
import os
import re

import setuptools


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string")


entrypoints = {"console_scripts": ["pyaccountant = pyaccountant.pyaccountant:main"]}
setuptools.setup(
    name="pyaccountant", version=find_version("src", "pyaccountant", "version.py")
)
setuptools.setup(
    name="pyaccountant",
    version=find_version("src", "pyaccountant", "version.py"),
    description="Make sense of your finances",
    package_dir={"": "src"},
    package=setuptools.find_packages(where="src"),
    include_package_data=True,
    entry_points=entrypoints,
    install_requires=[""],
)
