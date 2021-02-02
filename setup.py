""" Google Drive Command Line Interface

Command-line tools to perform various operations on your google drive
"""
import os
from setuptools import setup


PACKAGE_NAME = "python3-gdrive-cli"
AUTHOR = "Chi Wai Chan"
EMAIL = "chanchiwairay@gmail.com"
VERSION = "1.0.dev0"

DOCLINES = __doc__.split("\n")
DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])


if __name__ == "__main__":
    setup(
        name = PACKAGE_NAME,
        author = AUTHOR,
        author_email = EMAIL,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        license = "MIT",
        scripts = [
            "bin/gdrive",
            "bin/gdrive-auth",
            "bin/gdrive-config"
        ],
        packages = ["pydrivecli"],
        install_requires = [
            "tqdm",
            "pyyaml"
#            "pydrive2"
        ]
    )
