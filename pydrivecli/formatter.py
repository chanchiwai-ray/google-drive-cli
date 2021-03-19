from . import texts

class Formatter(object):
    def __init__(self, template="{id:40}\t{title:20}"):
        self.template = template

    def display(self, metadata):
        data = metadata.copy()
        data.update({
            "createdDate": texts.DatetimeText(data.get("createdDate", "")),
            "modifiedDate": texts.DatetimeText(data.get("modifiedDate", "")),
            "fileSize": texts.FileSizeText(data.get("fileSize", None))
        })
        if data.get("mimeType") == "application/vnd.google-apps.folder":
            data["title"] = texts.FolderText(data.get("title", ""))
        else:
            data["title"] = texts.FileText(data.get("title", ""))
        print(self.template.format(**data), end = "\n")