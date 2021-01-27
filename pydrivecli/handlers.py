from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from queue import Queue
import re
import sys
import threading

from tqdm import tqdm
from pydrive2.files import ApiRequestError

from . import requests
from . import utils
from .formatter import Printer
from .formatter import Title

def create_handler(type):
    if type == "list":
        return ListHandler()
    elif type == "download":
        return DownloadHandler()
    elif type == "upload":
        return UploadHandler()
    elif type == "create":
        return CreateHandler()
    elif type == "trash":
        return TrashHandler()
    elif type == "untrash":
        return UnTrashHandler()
    elif type == "delete":
        return DeleteHandler()
    elif type == "move":
        return MoveHandler()
    elif type == "rename":
        return RenameHandler()
    else:
        raise NotImplementedError(f"{type} handler has not been implemented.")

class Handler(ABC):
    def __init__(self, type):
        self.drive = None
        self.type = type

    def attach(self, drive):
        self.drive = drive

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class ListHandler(Handler):
    def __init__(self):
        super().__init__("list")
        self.request_params = requests.FileListParams()
        self.printer = Printer()

    def process(self, options):
        # Display options
        self.recursive = options.recursive
        if options.time:
            self.request_params["orderBy"] += ",modifiedDate"
        if options.fields:
            fields = [i.strip() for i in options.fields.strip().split(",")]
            self.printer.formatter = "\n".join("%-10s: {%s}" % (i.upper(), i) for i in fields) + "\n"
        elif options.long:
            self.printer.formatter = "{id:40}\t{ownerNames[0]:10}\t{fileSize:>10} MB\t{modifiedDate}\t{title:20}"
        else:
            self.printer.formatter = "{id:40}\t{title:20}"

        # File Filter Options
        if options.query:
            q = options.query
        elif options.all:
            q = "'root' in parents or sharedWithMe and trashed=false"
        elif options.filename or options.id:
            if options.filename and not options.id:
                q = " or ".join(["title='%s'" % fname.strip() for fname in options.filename])
            elif options.id and not options.filename:
                q = " or ".join(["'%s' in parents" % id.strip() for id in options.id])
            else:
                q_ids = " or ".join(["'%s' in parents" % id.strip() for id in options.id])
                q_filenames = " or ".join(["title='%s'" % fname.strip() for fname in options.filename])
                q = q_ids + " or " + q_filenames
        else:
            q = "'root' in parents and trashed=false"
        self.request_params["q"] = q

    def _execute(self, result, queue):
        item = queue.get()
        parent_folder = item["parent_folder"]
        child_folder = item["child_folder"]
        param = self.request_params.copy()
        param.update({"q": "'%s' in parents and trashed=false" % child_folder["id"]})
        for f in self.drive.ListFile(param = param).GetList():
            result["%s/%s" % (parent_folder, child_folder["title"])].append(f)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                queue.put({
                    "parent_folder": "%s/%s" % (parent_folder, child_folder["title"]),
                    "child_folder": f
                })

    def execute(self):
        if self.recursive:
            q = Queue()
            folders = defaultdict(list)
            for f in self.drive.ListFile(param = self.request_params).GetList():
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    q.put({"parent_folder": "./MyDrive", "child_folder": f})
                if f.get("ownedByMe"):
                    folders["./MyDrive"].append(f)
                else:
                    folders["./ShareWithMe"].append(f)

            while not q.empty():
                self._execute(result, q)

            for folder, items in result.items():
                print(Title(folder).use_folder_scheme())
                for f in items:
                    self.printer.display(f)
        else:
            for f in self.drive.ListFile(param = self.request_params).GetList():
                self.printer.display(f)


class DownloadHandler(Handler):
    def __init__(self):
        super().__init__("download")
        try:
            config = utils.load_configuration()
        except FileNotFoundError:
            print("error: no configuration file found, please make sure you have configure the application with gdrive-config; exiting...")
            sys.exit()
        else:
            self.download_path = Path(config["home_directory"], config["drive_directory_name"])
        self.request_params = requests.FileListParams()
        self.export_format = None
        self.files = []

    def process(self, options):
        # process export options
        if options.export_format:
            self.export_format = utils.ExportFormat.from_format_string(options.export_format)
        elif options.pdf:
            self.export_format = utitl.ExportFormat()
            self.export_format.export_all_to_pdf()
        elif options.auto_export:
            self.export_format = utils.ExportFormat()
        else:
            self.export_format = None

        # process file filter options
        if options.query:
            q = options.query
        elif options.all:
            q = "'root' in parents or sharedWithMe"
        elif options.filename:
            q = " or ".join(["title='%s'" % fname.strip(" /") for fname in options.filename])
        else:
            q = "'root' in parents and trashed=false"
        self.request_params["q"] = q

        # process download options
        self.download_path = Path(options.path) or self.download_path

        # add download task to self.files
        self._add_download_tasks(
            self.request_params,
            self.download_path,
            options.recursive,
            options.force
        )

    def execute(self):
        for file in self.files:
            progress_bar = tqdm(
                desc = "%s" % file["title"],
                total = 100,
                ncols = 100,
                ascii = True,
                bar_format = "  {desc:<20}: |{bar}| {n_fmt:>3}/{total_fmt:>3}"
            )
            threading.Thread(
                target = file["file"].GetContentFile,
                args = (file["path"] / file["title"],),
                kwargs = {"mimetype": file["export_format"], "callback": self._update_progress_bar(progress_bar)}
            ).start()

    def _update_progress_bar(self, progress_bar):
        def _update(x, total):
            if (total == 0.0 and x == 0.0) or total is None:
                steps = 100
            else:
                steps = int(x/total*100 - progress_bar.n)
            progress_bar.update(steps)
        return _update

    def _add_download_tasks(self, request_params, download_path, recursive, force):
        _filenames = []
        for file in self.drive.ListFile(param = request_params).GetList():
            mimetype = file["mimeType"]
            # some shared files cannot be downloaded because the owner
            # does not allow you to do so
            capabilities = file["capabilities"]
            if not capabilities["canDownload"]:
                print("error: '%s' cannot be downloaded; probably you don't have permission to do so" % file["title"])
                continue

            # cache filenames and check if there are duplicated names,
            # append the file id to the filename if there are duplicates
            title = u"%s" % file["title"].replace("/", u"\u2215")
            if title in _filenames:
                title += " " + file["id"]
            else:
                _filenames.append(title)

            # file / folder already exists
            if Path(download_path, title).exists() and not force:
                print("error: '%s' cannot be downloaded because it already exists; skipping..." % title)
                continue

            if not mimetype.startswith("application/vnd.google-apps."):
                # a file
                export_format = None
            elif mimetype.startswith("application/vnd.google-apps.folder") and not recursive:
                # a folder but not download
                print("error: -r not specified; omitting folder '%s/'" % title)
                continue
            elif mimetype.startswith("application/vnd.google-apps.folder") and recursive:
                # a folder and download recursively
                request_params = self.request_params.copy()
                request_params["q"] = "'%s' in parents" % file["id"]
                folder_name = Path(download_path, title)
                folder_name.mkdir(exist_ok = True) # if the folder already exists, it will be bait out already in previous sanity check
                self._add_download_tasks(request_params, folder_name, recursive, force)
                continue # skip this task since it is only a folder
            else:
                # a google workspace document
                if self.export_format is None:
                    exportable_mimetypes = file["exportLinks"].keys()
                    export_format = input("\n-- Choose an export mimetype for '%s':\n%s\n>> " % (title, "\n".join(exportable_mimetypes))).strip()
                    while export_format not in exportable_mimetypes:
                        print(">> Invalid mimetype: %s" % export_format)
                        export_format = input(">> ")
                else:
                    export_format = self.export_format[mimetype]

            self.files.append({
                "file": file,
                "title": title,
                "export_format": export_format,
                "path": download_path
            })


class UploadHandler(Handler):
    def __init__(self):
        super().__init__("upload")
        self.metadatas = []
        self.paths = defaultdict(list)

    def _add_path(self, path, rename=False, id="root"):
        if path.is_dir():
            folder = self.drive.CreateFile(metadata = {
                "title": rename or path.name,
                "parents": [{"id": id}],
                "mimeType": "application/vnd.google-apps.folder"
            })
            folder.Upload()
            for filename in path.iterdir():
                self._add_path(Path(filename), id = folder["id"])
        else:
            self.paths[id].append((rename, path))

    def process(self, options):
        if options.rename and len(options.rename) != len(options.filename):
            print("error: must provide as much --rename and --filename, or vice versa.")
            sys.exit()
        elif options.rename and len(options.filename) == len(options.rename):
            name_pairs = zip(options.rename, options.filename)
        else:
            name_pairs = zip(options.filename, options.filename)

        for rename, filename in name_pairs:
            rename = Path(rename).name
            path = Path(filename)
            if not path.exists():
                print("error: No such file or folder: '%s', skipping..." % path)
                continue
            if not options.allow_duplicate:
                param = requests.FileListParams()
                param["q"] = "'%s' in parents and trashed=false and title='%s'" % (options.root, rename)
                files = list(self.drive.ListFile(param = param).GetList())
                if len(files) > 0:
                    print("error: '%s' already exists in your google drive." % rename)
                    continue
            self._add_path(path, rename = rename, id = options.root)

    def execute(self):
        for id, files in self.paths.items():
            for rename, path in files:
                file = self.drive.CreateFile(metadata = {
                    "title" : rename or path.name,
                    "parents" : [{"id": id}]
                })
                file.SetContentFile(path)
                threading.Thread(
                    target = file.Upload
                ).start()


class CreateHandler(Handler):
    def __init__(self):
        super().__init__("create")
        self.contents = ""
        self.metadata = {
            "title": "untitled",
            "mimeType": None
        }

    def process(self, options):
        self.contents = options.contents or self.contents
        self.metadata["title"] = options.filename or self.metadata["title"]
        self.metadata["mimeType"] = "text/plain" if self.contents else "application/vnd.google-apps.folder"
        self.metadata["parents"] = {"id": options.root.strip(" /")}
        if not options.allow_duplicate:
            param = requests.FileListParams()
            param["q"] = "'%s' in parents and trashed=false and title='%s'" % (options.root.strip(" /"), options.filename)
            files = list(self.drive.ListFile(param = param).GetList())
            if len(files) > 0:
                print("error: '%s' already exists in your google drive." % options.filename)
                sys.exit()

    def execute(self):
        file = self.drive.CreateFile(metadata = self.metadata)
        if self.contents:
            file.SetContentString(self.contents)
        file.Upload()

    def upload(self, file):
        try:
            file.Upload()
        except ApiRequestError as e:
            print("error: cannot upload this file %s; %s" % (file["id"], str(e)))
        else:
            print("uploaded %s" % file["id"])


class TrashHandler(Handler):
    def __init__(self):
        super().__init__("trash")

    def process(self, options):
        self.ids = [id.strip() for id in options.ids]

    def execute(self):
        for id in self.ids:
            file = self.drive.CreateFile(metadata = {"id": id})
            threading.Thread(
                target = self.trash,
                args = (file,)
            ).start()

    def trash(self, file):
        try:
            file.Trash()
        except ApiRequestError as e:
            print("error: cannot trash this file %s; %s" % (file["id"], str(e)))
        else:
            print("trashed %s" % file["id"])


class UnTrashHandler(Handler):
    def __init__(self):
        super().__init__("untrash")

    def process(self, options):
        self.ids = [id.strip() for id in options.ids]

    def execute(self):
        for id in self.ids:
            file = self.drive.CreateFile(metadata = {"id": id})
            threading.Thread(
                target = self.untrash,
                args = (file,)
            ).start()

    def untrash(self, file):
        try:
            file.UnTrash()
        except ApiRequestError as e:
            print("error: cannot untrash this file %s; %s" % (file["id"], str(e)))
        else:
            print("untrashed %s" % file["id"])


class DeleteHandler(Handler):
    def __init__(self):
        super().__init__("delete")

    def process(self, options):
        self.ids = [id.strip() for id in options.ids]

    def execute(self):
        for id in self.ids:
            file = self.drive.CreateFile(metadata = {"id": id})
            threading.Thread(
                target = self.delete,
                args = (file,)
            ).start()

    def delete(self, file):
        try:
            file.Delete()
        except ApiRequestError as e:
            print("error: cannot delete this file %s; %s" % (file["id"], str(e)))
        else:
            print("delete %s" % file["id"])


class MoveHandler(Handler):
    def __init__(self):
        super().__init__("move")

    def process(self, options):
        self.sources = options.sources
        self.destination = options.destination

    def execute(self):
        for source in self.sources:
            source_file = self.drive.CreateFile(metadata = {"id": source})
            source_file.FetchMetadata(fields = "id,parents")
            threading.Thread(
                target = self.move,
                args = (source_file, ",".join(parent["id"] for parent in source_file["parents"]))
            ).start()

    def move(self, source_file, old_parents):
        try:
            source_file.Upload({
                "addParents": self.destination,
                "removeParents": old_parents
            })
        except ApiRequestError as e:
            print("error: cannot move this file %s; %s" % (source_file["id"], str(e)))
        else:
            print("moved %s to %s" % (source_file["id"], self.destination))


class RenameHandler(Handler):
    def __init__(self):
        super().__init__("rename")

    def process(self, options):
        self.id = options.id
        self.name = options.name

    def execute(self):
        file = self.drive.CreateFile(metadata = {"id": self.id})
        file.FetchMetadata(fields = "id,title")
        file["title"], self.old_name = self.name, file["title"]
        threading.Thread(
            target = self.rename,
            args = (file,)
        ).start()

    def rename(self, file):
        try:
            file.Upload()
        except ApiRequestError as e:
            print("error: cannot rename this file %s; %s" % (self.old_name, str(e)))
        else:
            print("renamed '%s' to '%s'" % (self.old_name, file["title"]))
