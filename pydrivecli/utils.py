import os
import sys
from pathlib import Path

from yaml import dump, Dumper
from yaml import load, Loader

from pydrive2.auth import GoogleAuth
from pydrive2.settings import ValidateSettings
from pydrive2.settings import InvalidConfigError

HOME = Path.home()
BASE = Path.home() / ".gdrive"
CONFIG = BASE / "config.yaml"
DRIVE = "google-drive"
TRASH = "google-drive-trash"

def load_configuration():
    try:
        with open (CONFIG, "r") as f:
            config = load(f, Loader = Loader)
    except FileNotFoundError as e:
        raise e
    else:
        return config

def find_settings_file(filename="settings.yaml"):
    # list of possible place to find settings file
    settings_file_env = os.environ.get("PYDRIVE_SETTINGS", None)
    settings_file_loc = BASE / filename

    # find settings file in this order
    settings_files = [settings_file_env, settings_file_loc]
    for settings_file in settings_files:
        if settings_file and settings_file.exists():
            return settings_file
    return None

def configure_application(options):
    try:
        settings_file = find_settings_file()
        if not settings_file.exists() or options.reconfigure:
            raise FileNotFoundError()
        print("Found settings file at %s; will use this settings file." % settings_file)
        return settings_file
    except FileNotFoundError:
        settings = new_settings(options)
        with open(settings_file, "w") as f:
            dump(settings, f, Dumper = Dumper)
        print("Configuring new settings file at %s" % settings_file)
        return settings_file
    except InvalidConfigError:
        print("Configuration error.")
        return None

def authenticate_and_authorize(options, settings_file=None, method="local"):
    gauth = GoogleAuth(settings_file = settings_file)

    gauth.LoadCredentials()
    if gauth.credentials is not None:
        raise RuntimeError("Error: credentials found at %s and it's already authenticated; skipping..."
            % gauth.settings.get("save_credentials_file"))

    if method == "local":
        gauth.LocalWebserverAuth(
            host_name = options.hostname,
            port_numbers = options.ports
        )
    elif method == "command_line":
        gauth.CommandLineAuth()
    else:
        raise ValueError("Error: received --method=%s, but --method can only be either 'local' or 'command_line'." % method)

    if gauth:
        print()
        print("Finished authentication and authorizion.")
        print("Please configure google drive client with gdrive-config if you have not done so yet.")
        print("Then, use gdrive -h for more information.")

    return gauth

def new_settings(options):
    settings = {
        "client_config_backend": options.client_config_backend,
        "save_credentials_backend": options.save_credentials_backend,
        "get_refresh_token": options.get_refresh_token,
        "oauth_scope": list(set(options.oauth_scope))
    }

    # update credentials related options if --save-credentials-backend=file
    if options.save_credentials_backend == "file":
        settings.update({
            "save_credentials": options.save_credentials,
            "save_credentials_file": options.save_credentials_file
        })
    else:
        raise ValueError("--save-credentials-backend must be 'file'.")

    # update application related options if --client-config-backend=file
    if options.client_config_backend == "file":
        settings.update({
            "client_config_file": os.path.abspath(options.client_config_file),
        })
    elif options.client_config_backend == "setting":
        settings.update({
            "client_config": {
                "client_id": options.client_id,
                "client_secret": options.client_secret,
                "auth_uri": options.auth_uri,
                "token_uri": options.token_uri,
                "redirect_uri": options.redirect_uri,
                "revoke_uri": options.revoke_uri,
            }
        })
    else:
        raise ValueError("--client-config-backend must either 'file' or 'setting'.")

    ValidateSettings(settings)

    return settings

class ExportFormat(dict):
    _exportable_mimetypes = {
        "application/vnd.google-apps.document": [
            "text/html",
            "application/zip",
            "text/plain",
            "application/rtf",
            "application/vnd.oasis.opendocument.text",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/epub+zip"
        ],
        "application/vnd.google-apps.spreadsheet": [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/epub+zip",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/x-vnd.oasis.opendocument.spreadsheet",
            "application/pdf",
            "text/csv",
            "text/tab-separated-values",
            "application/zip"
        ],
        "application/vnd.google-apps.drawing": [
            "image/jpeg",
            "image/png",
            "image/svg+xml",
            "application/pdf",
        ],
        "application/vnd.google-apps.presentation": [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.oasis.opendocument.presentation",
            "application/pdf",
            "text/plain",
        ]
    }

    def __init__(self):
        self["application/vnd.google-apps.document"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        self["application/vnd.google-apps.spreadsheet"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        self["application/vnd.google-apps.presentation"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        self["application/vnd.google-apps.drawing"] = "image/jpeg"

    def __setitem__(self, k, v):
        exportable_mimetypes = ExportFormat._exportable_mimetypes.get(k)
        if not exportable_mimetypes:
            raise ValueError("Not exportable google workspace documents: '%s'" % k)
        if v not in exportable_mimetypes:
            raise ValueError("Cannot export to this mimetype: '%s'. Availiable mimetypes are: '%s'" % (v, ", ".join(exportable_mimetypes)))
        dict.__setitem__(self, k, v)

    def __getitem__(self, k):
        return dict.__getitem__(self, k)

    @classmethod
    def from_format_string(cls, format_string):
        c = cls()
        c.update({c.get_google_document_mimetype(pair.split("=")[0].strip()): pair.split("=")[1].strip() for pair in format_string.strip().split(",")})
        return c

    def update(self, *args, **kwargs):
        """Overwritten method of dictionary."""
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def export_all_to_pdf(self):
        self["application/vnd.google-apps.document"] = "application/pdf"
        self["application/vnd.google-apps.spreadsheet"] = "application/pdf"
        self["application/vnd.google-apps.presentation"] = "application/pdf"
        self["application/vnd.google-apps.drawing"] = "application/pdf"

    @staticmethod
    def get_google_document_mimetype(alias):
        if alias == "folder":
            return "application/vnd.google-apps.folder"
        elif alias == "document":
            return "application/vnd.google-apps.document"
        elif alias == "spreadsheet":
            return "application/vnd.google-apps.spreadsheet"
        elif alias == "presentation":
            return "application/vnd.google-apps.presentation"
        elif alias == "drawing":
            return "application/vnd.google-apps.drawing"
        else:
            raise ValueError("Unknown alias '%s'." % alias)
