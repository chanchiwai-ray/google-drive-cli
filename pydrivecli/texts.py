from datetime import datetime

class EnhancedText(str):
    def __new__(cls, text, prefix="", suffix=""):
        return super().__new__(cls, prefix + str(text) + suffix)
    def __add__(self, other):
        return type(self)(str(self) + str(other))
    def add_prefix(self, prefix=""):
        return type(self)(str(prefix) + str(self))
    def add_suffix(self, suffix=""):
        return self + suffix
    def rgb(self, r, g, b):
        return type(self)("\033[38;2;%s;%s;%sm%s\033[0m" % (r, g, b, self))
    def bold(self):
        return type(self)("\033[1m%s\033[0m" % self)
    def italic(self):
        return type(self)("\033[3m%s\033[0m" % self)
    def underline(self):
        return type(self)("\033[4m%s\033[0m" % self)
    def invert(self):
        return type(self)("\033[7m%s\033[0m" % self)
    def use_code(self, code):
        return type(self)("\033[%dm%s\033[0m" % (code, self))
    def show(self):
        print(self)


class LoggingText(object):
    def __new__(cls, text, level="LOGGING", rgb=(255,255,255)):
        text = EnhancedText(text).bold().italic()
        prefix = EnhancedText("[%s] " % level.upper()).bold().rgb(*rgb)
        return text.add_prefix(prefix)


class FolderText(object):
    def __new__(cls, text):
        text = EnhancedText(text).rgb(0, 255, 0).bold()
        suffix = EnhancedText("/")
        return text.add_suffix(suffix)


class FileText(object):
    def __new__(cls, text):
        return EnhancedText(text)


class LinkText(object):
    def __new__(cls, text):
        return EnhancedText(text).underline().rgb(7,146,252)


class DatetimeText(object):
    def __new__(cls, text):
        try:
            date_time = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception:
            return EnhancedText(text)
        else:
            if datetime.now().year > date_time.year:
                return EnhancedText(date_time.strftime("%b %-2d %-4Y"))
            else:
                return EnhancedText(date_time.strftime("%b %-2d %H:%M"))


class FileSizeText(object):
    def __new__(cls, text):
        if text is None:
            return EnhancedText(text)
        # display in MB
        return EnhancedText(round(float(text) / 1e6), suffix = " MB")


class ExecutableText(object):
    def __new__(cls, text):
        text = EnhancedText(text).rgb(59, 191, 59)
        suffix = EnhancedText("*")
        return text.add_suffix(suffix)