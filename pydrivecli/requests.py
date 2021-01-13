class ValidationError(Exception):
    pass


class RequestParams(dict):
    # fallback _valid_params, subclass should always specify the _valid_params
    _valid_params = {}

    # Overwrite default __setitem__ to allow validation.
    def __setitem__(self, k, v):
        if self._valid_params.get(k, None) is None:
            raise KeyError("Optional parameter '%s' does not exist." % k)
        self._validate(k, v)
        dict.__setitem__(self, k, v)

    def _validate(self, k, v):
        props = self._valid_params.get(k)
        # props contains only two check fields
        if props.get("type", None) is not None and props.get("type") != type(v):
            raise ValidationError(f"Type mismatch. Expecting {props['type']}, but {v} has type {type(v)}.")
        if props.get("choices", None) is not None:
            # choices are comma separated
            if not set(v.split(",")).issubset(set(props.get("choices"))):
                raise ValidationError(f"Choices: '{v}' are not choosen from {props.get('choices')}.")

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def populate(self):
        # populate default parameters if it's needed
        for k, v in self._valid_params.items():
            if v["populate"]:
                self[k] = v["default"]


class FileListParams(RequestParams):
    _valid_params = {
        "corpora": {
            "type": str,
            "default": "user",
            "populate": False,
            "choices": (
                "user",
                "drive",
                "domain",
                "allDrives",
                "drive"
            )
        },
        "driveId": {
            "type": str,
            "populate": False,
        },
        "includeItemsFromAllDrives": {
            "type": bool,
            "default": True,
            "populate": True
        },
        "includePermissionsForView": {
            "type": str,
            "default": "published",
            "populate": False,
            "choices": ("published")
        },
        "maxResults": {
            "type": int,
            "default": 1000,
            "populate": True
        },
        "orderBy": {
            "type": str,
            "default": "folder,title",
            "populate": True,
            "choices": (
                'createdDate',
                'folder',
                'lastViewedByMeDate',
                'modifiedByMeDate',
                'modifiedDate',
                'quotaBytesUsed',
                'recenct',
                'sharedWithMeDate',
                'starred',
                'title',
                'title_natural'
            )
        },
        "pageToken": {
            "type": str,
            "default": "0",
            "populate": False
        },
        "q": {
            "type": str,
            "default": "'root' in parents and trashed=false",
            "populate": True
        },
        "spaces": {
            "type": str,
            "default": "drive,photos",
            "populate": False,
            "choices": (
                "drive",
                "appDataFolder",
                "photos"
            )
        },
        "supportsAllDrives": {
            "type": bool,
            "default": True,
            "populate": True
        },
        "fields": {
            "type": str,
            "default": "items(%s)" %
                "alternateLink,appDataContents,"
                "canComment,canReadRevisions,capabilities,"
                "copyable,createdDate,defaultOpenWithLink,description,"
                "downloadUrl,editable,embedLink,etag,explicitlyTrashed,"
                "exportLinks,fileExtension,fileSize,folderColorRgb,"
                "fullFileExtension,hasAugmentedPermissions,"
                "headRevisionId,iconLink,id,"
                "imageMediaMetadata,indexableText,isAppAuthorized,kind,"
                "labels,lastModifyingUser,lastModifyingUserName,"
                "lastViewedByMeDate,markedViewedByMeDate,md5Checksum,"
                "mimeType,modifiedByMeDate,modifiedDate,openWithLinks,"
                "originalFilename,ownedByMe,ownerNames,owners,parents,"
                "permissions,properties,quotaBytesUsed,selfLink,shareable,"
                "shared,sharedWithMeDate,sharingUser,spaces,teamDriveId,"
                "thumbnail,thumbnailLink,title,trashedDate,trashingUser,"
                "userPermission,version,videoMediaMetadata,webContentLink,"
                "webViewLink,writersCanShare",
            "populate": True
        }
    }

    def __init__(self):
        self.populate()
