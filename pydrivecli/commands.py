from .utils import HOME, BASE

from argparse import ArgumentParser

# To add more command line options, create a new function with name
# 'append_xxx_options' and append the subparser options to the main parser in
# parse_command_line function.

__all__ = ["parse_command_line", "parse_auth_command_line"]


def append_list_options(subparsers):
    list_opts = subparsers.add_parser(
        "list",
        prog = "gdrive list",
        help = "Listing files in the Google Drive. By default, it will list the names of all files in your drive."
    )
    # Display control options
    display_opts_group = list_opts.add_argument_group(
        title = "Display Control Options"
    )
    display_opts_group.add_argument(
        "-t", "--time",
        action = "store_true",
        help = "List the files in descending time order. (Optional)"
    )
    display_opts_group.add_argument(
        "-l", "--long",
        action = "store_true",
        help = "Show more details about the files. (Optional)"
    )
    display_opts_group.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "List all the files and files in a folder. (Optional)"
    )
    display_opts_group.add_argument(
        "-F", "--fields",
        help = "Show these fields instead. The fields should be comma separated, for example: 'title,id,createdDate'. This option has the highest priority in this group. (Optional)"
    )
    # Files filters options
    filter_opts_group = list_opts.add_argument_group(
        title = "File Filter Options"
    )
    filter_opts_group.add_argument(
        "-a", "--all",
        action = "store_true",
        help = "List all files in your drive, including shared files. (Optional)"
    )
    filter_opts_group.add_argument(
        "-i", "--id",
        action = "append",
        help = "Show the detail of these folders. (Optional)"
    )
    filter_opts_group.add_argument(
        "-f", "--filename",
        action = "append",
        help = "Show the detail of these files. (Optional)"
    )
    filter_opts_group.add_argument(
        "-q", "--query",
        help = "Use this query instead the default query and options in this group, when searching and listing files. This option has the highest priority in this group. (Optional)"
    )

def append_download_options(subparsers):
    download_opts = subparsers.add_parser(
        "download",
        prog = "gdrive download",
        help = "Download files from the Google Drive. If no options are provided, it will download all files (not including folders) from your google drive."
    )
    download_opts.add_argument(
        "-F", "--force",
        action = "store_true",
        help = "Force to download the files to your local storage even if files with same names already exists. (Optional)"
    )
    download_opts.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "Download all the files in a folder. (Optional)"
    )
    download_opts.add_argument(
        "-P", "--path",
        help = "Overwrite the default output directory. (Optional)"
    )
    # Files filters options
    filter_opts_group = download_opts.add_argument_group(
        title = "File Filter Options"
    )
    filter_opts_group.add_argument(
        "-a", "--all",
        action = "store_true",
        help = "Download all files in your drive, including shared files. (Optional)"
    )
    filter_opts_group.add_argument(
        "-f", "--filename",
        action = "append",
        help = "Download the files / folder with these names. (Optional)"
    )
    filter_opts_group.add_argument(
        "-q", "--query",
        help = "Download all files that pass this query. This option has the highest priority in this group. (Optional)"
    )
    # Files export options
    file_export_opts = download_opts.add_argument_group(
        title = "File Export Options"
    )
    file_export_opts.add_argument(
        "-A", "--auto-export",
        action = "store_true",
        help = "Automatically set the export format of google workspace documents. (Optional)"
    )
    file_export_opts.add_argument(
        "-p", "--pdf",
        action = "store_true",
        help = "Set the export format of google workspace documents to pdf. (Optional)"
    )
    file_export_opts.add_argument(
        "-e", "--export-format",
        help = "Set the export format for google workspace documents. You should provide the export format in a comma seperated key value pair format: key1=value1,key2=value2 (Optional)"
    )

def append_upload_options(subparsers):
    upload_opts = subparsers.add_parser(
        "upload",
        prog = "gdrive upload",
        help = "Upload files to the Google Drive."
    )
    upload_opts.add_argument(
        "-f", "--filename",
        action = "append",
        required = True,
        help = "Set the names of the files or folders to be uploaded. (Required)"
    )
    upload_opts.add_argument(
        "-n", "--rename",
        action = "append",
        help = "Rename the names of the files or folders to be uploaded; must provide as much as --filename. (Optional)"
    )
    upload_opts.add_argument(
        "-d", "--allow-duplicate",
        action = "store_true",
        help = "Allow files / folders with the same name to be uploaded. (Optional) "
    )
    upload_opts.add_argument(
        "-R", "--root",
        default = "root",
        help = "Upload file to the folder with this id. (Optional)"
    )

def append_create_options(subparsers):
    create_opts = subparsers.add_parser(
        "create",
        prog = "gdrive create",
        help = "Create a new folder in your google drive or a plain text file with some contents."
    )
    create_opts.add_argument(
        "-f", "--filename",
        default = "untitled",
        help = "Set the filename of the new file or folder. (Default: 'untitled')"
    )
    create_opts.add_argument(
        "-R", "--root",
        default = "root",
        help = "Create a file / folder to the folder with this id. (Optional)"
    )
    create_opts.add_argument(
        "-d", "--allow-duplicate",
        action = "store_true",
        help = "Allow files / folders with the same name to be created. (Optional) "
    )
    create_opts.add_argument(
        "-c", "--contents",
        help = "Set the content string for this file. If the content string is provided, it is assumed that you are creating a file not a folder. (Optional)"
    )

def append_delete_options(subparsers):
    delete_ops = subparsers.add_parser(
        "delete",
        prog = "gdrive delete",
        help = "Permanently delete files or folders in your google drive."
    )
    delete_ops.add_argument(
        "ids",
        nargs = "+",
        help = "Set the ids of the file or folder to be deleted."
    )

def append_trash_options(subparsers):
    trash_opts = subparsers.add_parser(
        "trash",
        prog = "gdrive trash",
        help = "Move files or folders in your google drive to trash."
    )
    trash_opts.add_argument(
        "ids",
        nargs = "+",
        help = "Set the ids of the file or folder to be trashed."
    )

def append_untrash_options(subparsers):
    untrash_opts = subparsers.add_parser(
        "untrash",
        prog = "gdrive untrash",
        help = "Undo the trash operation."
    )
    untrash_opts.add_argument(
        "ids",
        nargs = "+",
        help = "Set the ids of the file or folder to be untrashed."
    )

def append_move_options(subparsers):
    move_opts = subparsers.add_parser(
        "move",
        prog = "gdrive move",
        help = "Move files / folders to a different folder."
    )
    move_opts.add_argument(
        "sources",
        nargs = "+",
        help = "Set the ids of the files or folders to be moved."
    )
    move_opts.add_argument(
        "destination",
        help = "Set the destination folder id."
    )

def append_rename_options(subparsers):
    rename_opts = subparsers.add_parser(
        "rename",
        prog = "gdrive rename",
        help = "Rename a file or folder."
    )
    rename_opts.add_argument(
        "id",
        help = "Set the id of the file or folder to be renamed."
    )
    rename_opts.add_argument(
        "name",
        help = "Set the new name for the file or folder."
    )
    rename_opts.add_argument(
        "-d", "--allow-duplicate",
        action = "store_true",
        help = "Allow duplicated name. (Optional)"
    )

def append_share_options(subparsers):
    share_opts = subparsers.add_parser(
        "share",
        prog = "gdrive share",
        help = "Get a shareable link with certain permissions. (Also see 'gdrive permission' command)"
    )
    share_opts.add_argument(
        "ids",
        nargs = "+",
        help = "Set the ids of the files or folders to be shared."
    )
    share_opts.add_argument(
        "-t", "--type",
        default = "anyone",
        choices = ["user", "group", "domain", "anyone"],
        help = "Set the account type. Availiable values are: user, group, domain or anyone. (Default: anyone)"
    )
    share_opts.add_argument(
        "-u", "--user",
        help = "Set the email address of the user who you want to share file of folder with. (Optional, and required only --type=user)"
    )
    access_control_opt_group = share_opts.add_mutually_exclusive_group()
    access_control_opt_group.add_argument(
        "-w", "--writable",
        action = "store_true",
        help = "Set the shared file to be writable."
    )
    access_control_opt_group.add_argument(
        "-r", "--readable",
        action = "store_true",
        help = "Set the shared file to be  readable. (Default)"
    )

def append_unshare_options(subparsers):
    unshare_opts = subparsers.add_parser(
        "unshare",
        prog = "gdrive unshare",
        help = "Unshare a file or link. (Also see 'gdrive permission' command)"
    )
    unshare_opts.add_argument(
        "ids",
        nargs = "+",
        help = "Set the ids of the files or folders to be unshared."
    )
    unshare_opts.add_argument(
        "-t", "--type",
        default = "anyone",
        choices = ["user", "group", "domain", "anyone"],
        help = "Set the account type. Availiable values are: user, group, domain or anyone. (Default: anyone)"
    )
    unshare_opts.add_argument(
        "-u", "--user",
        help = "Set the email address of the user who you want to unshare the file or folder with. (Optional, and required only --type=user)"
    )

def parse_command_line():
    parser = ArgumentParser(
        description = "The command line interface for google drive. You can choose one of the commands from below to perform various operations on your google drive."
    )
    subparsers = parser.add_subparsers(
        dest = "choice",
        title = "commands"
    )
    append_create_options(subparsers)
    append_delete_options(subparsers)
    append_download_options(subparsers)
    append_list_options(subparsers)
    append_move_options(subparsers)
    append_rename_options(subparsers)
    append_trash_options(subparsers)
    append_untrash_options(subparsers)
    append_upload_options(subparsers)
    append_share_options(subparsers)
    append_unshare_options(subparsers)

    return parser.parse_args()

def parse_auth_command_line():
    parser = ArgumentParser(
        usage = "gdrive-auth [options...]",
        description = "The authentication and authorization options. \
            This is used to configure your appliaction, for example, client_secret \
            and oauth2.0 scopes. Typical use: gdrive-auth --save-credentials \
            --get-refresh-token --client-config-file my_client_secret.json"
        )

    app_config_opts = parser.add_argument_group("Application Configuration Options")
    app_config_opts.add_argument(
        "--client-config-backend",
        default = "file",
        help = "The client configuration for the application [file | setting]. (Default: file)"
    )
    app_config_opts.add_argument(
        "--client-config-file",
        default = "client_secrets.json",
        help = "The client configuration file for the application. (Required if --client-config-backend=file) (Default: client_secrets.json)"
    )
    app_config_opts.add_argument(
        "--client-id",
        help = "The client ID of the application. (Required if --client-config-backend=setting)"
    )
    app_config_opts.add_argument(
        "--client-secret",
        help = "The client secret of the application. (Required if --client-config-backend=setting)"
    )
    app_config_opts.add_argument(
        "--auth-uri",
        default = "https://accounts.google.com/o/oauth2/auth",
        help = "The authorization server endpoint URI. (Required if --client-config-backend=setting) (Default: 'https://accounts.google.com/o/oauth2/auth')"
    )
    app_config_opts.add_argument(
        "--token-uri",
        default = "https://accounts.google.com/o/oauth2/token",
        help = "The token server endpoint URI. (Required if --client-config-backend=setting) (Default: 'https://accounts.google.com/o/oauth2/token')"
    )
    app_config_opts.add_argument(
        "--redirect-uri",
        default = "urn:ietf:wg:oauth:2.0:oob",
        help = "Redirection endpoint URI. (Required if --client-config-backend=setting) (Default: 'urn:ietf:wg:oauth:2.0:oob')"
    )
    app_config_opts.add_argument(
        "--revoke-uri",
        default = None,
        help = "Revoke endpoint URI. (Required if --client-config-backend=setting) (Default: None)"
    )
    app_config_opts.add_argument(
        "--save-credentials-backend",
        default = "file",
        help = "Backend to save credential to. [file] (Default: file)"
    )
    app_config_opts.add_argument(
        "--save-credentials",
        action = "store_true",
        help = "Save the credentials? (Default: False)"
    )
    app_config_opts.add_argument(
        "--save-credentials-file",
        default = BASE / "credentials.json",
        help = "Destination of credentials file. (Default: %s)" % (BASE / "credentials.json")
    )
    app_config_opts.add_argument(
        "--get-refresh-token",
        action = "store_true",
        help = "Get refresh token. (Optional) (Default: False)"
    )
    app_config_opts.add_argument(
        "--oauth-scope",
        action = "append",
        default = ['https://www.googleapis.com/auth/drive'],
        help = "Get refresh token. (Default: 'https://www.googleapis.com/auth/drive')"
    )
    app_config_opts.add_argument(
        "--reconfigure",
        action = "store_true",
        help = "Force to reconfigure the application settings. (Default: False)"
    )

    auth_opts = parser.add_argument_group("Authentication Options")
    auth_opts.add_argument(
        "--hostname",
        default = "localhost",
        help = "The hostname for the local webserver. (Default: localhost)"
    )
    auth_opts.add_argument(
        "--ports",
        default = [8080, 8090],
        action = "append",
        help = "The port number for the local webserver. (Default: [8080 | 8090])"
    )
    auth_opts.add_argument(
        "--method",
        default = "command_line",
        help = "Authenticate method [local | command_line]. (Default: command_line)"
    )

    return parser.parse_args()
