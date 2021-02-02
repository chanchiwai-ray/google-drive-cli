# Google Drive CLI

**gdrive** is a command-line tool to perform various operations on your google drive. It is currently supporting most of the common operations that you will do on the web-based drive application such as downloading, uploading and moving files. You can learn more about the opeartions by typing

```
gdrive -h
```

## Installation

You can install the command-line tool in a virtual environment using pip3 (this is recommended to avoid dependencies and versions issues):

```
pip3 install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
(your-env) python3 setup.py install
```

You also need to fork/clone the [developing fork of PyDrive2](https://github.com/chanchiwai-ray/PyDrive2) to use this tool for now, since there're some bugs haven't been fixed in the [maintained fork of Pydrive2](https://github.com/iterative/PyDrive2)

```
git clone https://github.com/chanchiwai-ray/PyDrive2
cd ./PyDrive2
source <your-env>/bin/activate
(your-env) python3 setup.py install
```

## Configuration

### The authentication and authorization process

Since this command line tool is making use of the Google Drive API v2, you need to download the applcation configuration file from the Google API Console. For details, please see this [guide](https://developers.google.com/drive/api/v2/enable-drive-api) on how to enable the Drive API.

Once you have the client configuration file, you can proceed to create the command-line tool with the configuration file and authencate the user (which is you in this case) and authorize the command-line tool to access your google drive (also see this [guide](https://developers.google.com/drive/api/v2/about-auth)). Typically, you want to do this step once, so you need to save the your access token and your client configuration into a settings file. For example:

```
gdrive-auth --save-credentials --get-refresh-token --client-config-file <your_configuration_file.json>
```

### The configuration process

Currently, the configuration process only configures the default path to where you want to store the downloads. You can start the interactive configuration process by typing:

```
gdrive-config
```

You can also specify a one time download path by typing `gdrive download --path <path_to_download>`


## Options

The authentication and authorization options:

```
usage: gdrive-auth [options...]

The authentication and authorization options. This is used to configure your appliaction, for
example, client_secret and oauth2.0 scopes. Typical use: gdrive-auth --save-credentials --get-
refresh-token --client-config-file my_client_secret.json

optional arguments:
  -h, --help            show this help message and exit

Application Configuration Options:
  --client-config-backend CLIENT_CONFIG_BACKEND
                        The client configuration for the application [file | setting]. (Default:
                        file
  --client-config-file CLIENT_CONFIG_FILE
                        The client configuration file for the application. (Required if --client-
                        config-backend=file) (Default: client_secrets.json)
  --client-id CLIENT_ID
                        The client ID of the application. (Required if --client-config-
                        backend=setting)
  --client-secret CLIENT_SECRET
                        The client secret of the application. (Required if --client-config-
                        backend=setting)
  --auth-uri AUTH_URI   The authorization server endpoint URI. (Required if --client-config-
                        backend=setting) (Default: 'https://accounts.google.com/o/oauth2/auth')
  --token-uri TOKEN_URI
                        The token server endpoint URI. (Required if --client-config-
                        backend=setting) (Default: 'https://accounts.google.com/o/oauth2/token')
  --redirect-uri REDIRECT_URI
                        Redirection endpoint URI. (Required if --client-config-backend=setting)
                        (Default: 'urn:ietf:wg:oauth:2.0:oob')
  --revoke-uri REVOKE_URI
                        Revoke endpoint URI. (Required if --client-config-backend=setting)
                        (Default: None)
  --save-credentials-backend SAVE_CREDENTIALS_BACKEND
                        Backend to save credential to. [file] (Default: file)
  --save-credentials    Save the credentials? (Default: False)
  --save-credentials-file SAVE_CREDENTIALS_FILE
                        Destination of credentials file. (Default:
                        /home/<username>/.gdrive/credentials.json)
  --get-refresh-token   Get refresh token. (Optional) (Default: False)
  --oauth-scope OAUTH_SCOPE
                        Get refresh token. (Default: 'https://www.googleapis.com/auth/drive')
  --reconfigure         Force to reconfigure the application settings. (Default: False)

Authentication Options:
  --hostname HOSTNAME   The hostname for the local webserver. (Default: localhost)
  --ports PORTS         The port number for the local webserver. (Default: [8080 | 8090])
  --method METHOD       Authenticate method [local | command_line]. (Default: command_line)
```

The command line interface for google drive:

```
usage: gdrive [-h] {create,delete,download,list,move,rename,trash,untrash,upload} ...

The command line interface for google drive. You can choose one of the commands from below to
perform various operations on your google drive.

optional arguments:
  -h, --help            show this help message and exit

commands:
  {create,delete,download,list,move,rename,trash,untrash,upload}
    create              Create a new folder in your google drive or a plain text file with some
                        contents.
    delete              Permanently delete files or folders in your google drive.
    download            Download files from the Google Drive. If no options are provided, it will
                        download all files (not including folders) from your google drive.
    list                Listing files in the Google Drive. By default, it will list the names of
                        all files in your drive.
    move                Move files / folders to a different folder.
    rename              Rename a file or folder.
    trash               Move files or folders in your google drive to trash.
    untrash             Undo the trash operation.
    upload              Upload files to the Google Drive.
```

For details of each command, you can print the helps by using:

```
gdrive {command} -h
```

