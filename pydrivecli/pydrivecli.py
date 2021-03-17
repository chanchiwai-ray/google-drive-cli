import os
import sys
from yaml import dump, Dumper
from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from . import utils
from .utils import BASE, CONFIG, DRIVE, TRASH, HOME
from .handlers import create_handler
from .commands import parse_command_line
from .commands import parse_auth_command_line


class PyDriveCLI(object):
    """Command line interface for interacting with the google drive.
    """

    def __init__(self):
        settings_file = utils.find_settings_file()
        if not settings_file:
            print("error: no settings file found, please make sure you have authenticate yourself and authorize the CLI with gdrive-auth; exiting...")
            sys.exit()
        self.gauth = GoogleAuth(settings_file = settings_file)
        self.drive = GoogleDrive(self.gauth)
        self.options = parse_command_line()
        self.config = None

    def main(self):
        """Entry point for the CLI"""
        choice = self.options.choice
        handler = create_handler(choice)
        handler.attach(self.drive)
        handler.process(self.options)
        handler.execute()


class PyDriveAuthCLI(object):
    """Command line interface for initial authentication and authorization.
    """

    def __init__(self):
        self.options = parse_auth_command_line()
        self.settings_file = utils.configure_application(self.options)

    def main(self):
        """Entry point for the CLI"""
        try:
            _ = utils.authenticate_and_authorize(
                self.options,
                settings_file = self.settings_file,
                method = self.options.method,
            )
        except Exception as e:
            print(e)
            sys.exit()


class PyDriveConfigCLI(object):
    """Command line interface for initial configuration of the google drive cli application.
    """

    def main(self):
        """Entry point for the CLI"""
        if not BASE.exists():
            BASE.mkdir()

        if not CONFIG.exists():
            self.init(self.configure(CONFIG))
        else:
            response = ""
            while response != 'y' and response != 'n':
                response = input("Configuration file already exists. Process to reconfigure? [y/n] ")

            if response == 'y':
                self.init(self.configure(CONFIG))
            else:
                print("bye~")

    def create_directory(self, path):
        try:
            path.mkdir()
        except FileExistsError:
            print("%s already exists. Please re-configure with gdrive-config or delete the existing directory." % path)
            return False
        except PermissionError:
            print("Permission denied: cannot create path at %s. Please re-configure with gdrive-config." % path)
            return False
        except FileNotFoundError:
            print("Invalid path: %s. Please re-configure with gdrive-config." % path)
            return False
        else:
            print("%s has been created." % path)
            return True

    def configure(self, config_file=CONFIG):
        home = input("Set the home directory for your drive (default: %s): " % HOME).strip()
        drive_name = input("Set the name for your google drive directory (default: %s): " % DRIVE).strip()
        #trash_name = input("Set the name for your google drive trash directory (default: %s): " % TRASH).strip()
        print()
        with open(config_file, "w") as f:
            config = {
                "home_directory": home if home != "" else HOME,
                "drive_directory_name": drive_name if drive_name != "" else DRIVE
                #"trash_directory_name": trash_name if trash_name != "" else TRASH
            }
            dump(config, f, Dumper = Dumper)
        return config

    def init(self, config):
        drive_path = Path(config["home_directory"], config["drive_directory_name"])
        #trash_path = Path(config["home_directory"], config["trash_directory_name"])
        paths = (drive_path, TRASH)

        success = True
        for path in paths:
            success &= self.create_directory(path)

        if success:
            print("\nFinished configuring google drive client.")
            print("Please authenticate yourself and authorize this app with gdrive-auth if you have not done so yet.")
            print("Then, use gdrive -h for more information.")
        else:
            print("\nConfiguration fails. Please re-configure.")
