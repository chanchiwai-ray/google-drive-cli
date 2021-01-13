from datetime import datetime

class Printer(object):
    def __init__(self, formatter="{id:40}\t{title:20}"):
        self.formatter = formatter

    def display(self, metadata):
        data = metadata.copy()
        data.update({
            "title": Title(data.get("title", "")),
            "createdDate": Datetime(data.get("createdDate", "")),
            "modifiedDate": Datetime(data.get("modifiedDate", "")),
            "fileSize": FileSize(data.get("fileSize", None))
        })
        if data.get("mimeType") == "application/vnd.google-apps.folder":
            data["title"] = data["title"].use_folder_scheme()
        print(self.formatter.format(**data), end = "\n")


class Title(str):
    def __new__(cls, title):
        return super().__new__(cls, title)
    def use_file_scheme(self):
        return self
    def use_folder_scheme(self):
        return type(self)("\033[92m\033[1m%s\033[0m/" % self)


class Datetime(str):
    def __new__(cls, date_time):
        try:
            date_time = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            return super().__new__(cls, datetime)
        else:
            if datetime.now().year > date_time.year:
                return super().__new__(cls, date_time.strftime("%b %-2d %-4Y"))
            else:
                return super().__new__(cls, date_time.strftime("%b %-2d %H:%M"))


class FileSize(str):
    def __new__(cls, file_size):
        if file_size is None:
            return super().__new__(cls, "-" * 6)
        else:
            return super().__new__(cls, "%d MB" % round(float(file_size) / 1e6))
