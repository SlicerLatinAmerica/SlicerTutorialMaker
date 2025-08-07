import requests
from dataclasses import dataclass
from slicer.i18n import tr as _

@dataclass
class GitFile:
    gitType: str
    path: str
    def __post_init__(self):
        self.files = {}
        self.url = ""
        pass
    def setFiles(self, files):
        self.files = files
        pass
    def dir(self, path="") -> list[str]:
        file = self.__file__(path)
        return list(file.files.keys())

    def getRaw(self, path:str) -> str:
        file = self.__file__(path)
        if file.gitType != "file":
            raise OSError(_(f"Expected file type, got {file.gitType} type"))
        return requests.get(file.url).text

    def __file__(self, path:str):
        if path == "":
            return self
        spath = path.split("/")
        parent = self
        for seg in spath:
            if seg not in parent.files:
                raise OSError(_("Path does not exist"))
            parent = parent.files[seg]
        return parent

class GitTools:

    def ParseRepo(repo:str, path="") -> GitFile:
        endpoint = f"https://api.github.com/repos/{repo}/contents/{path}"
        response = requests.get(endpoint)
        if response.status_code != 200 and response.status_code != 403:
            raise Exception(f"{endpoint} : {response.text}")
        contents = response.json()
        if not isinstance(contents, list) or not isinstance(contents[0], dict):
            if 'message' in contents:
                raise Exception(_("Message from {endpoint}: {message}").format(endpoint=endpoint, message=contents['message']))
            raise Exception(_("Malformed Response from {endpoint}").format(endpoint=endpoint))

        root = GitFile("dir", "")
        for data in contents:
            _file = GitFile(data["type"], data["path"])
            if _file.gitType == "dir":
                _file.setFiles(GitTools.__parseRecursive__(repo, data["path"]))
            elif _file.gitType == "file":
                _file.url = data["download_url"]
            root.files[data["name"]] = _file
        return root

    def __parseRecursive__(repo:str, path=""):
        endpoint = f"https://api.github.com/repos/{repo}/contents/{path}"
        response = requests.get(endpoint)
        if response.status_code != 200 and response.status_code != 403:
            raise Exception(f"{endpoint} : {response.text}")
        contents = response.json()
        if not isinstance(contents, list) or not isinstance(contents[0], dict):
            if 'message' in contents:
                raise Exception(_("Message from {endpoint}: {message}").format(endpoint=endpoint, message=contents['message']))
            raise Exception(_("Malformed Response from {endpoint}").format(endpoint=endpoint))

        files = {}
        for data in contents:
            _file = GitFile(data["type"], data["path"])
            if _file.gitType == "dir":
                _file.setFiles(GitTools.__parseRecursive__(repo, data["path"]))
            elif _file.gitType == "file":
                _file.url = data["download_url"]
            files[data["name"]] = _file
        return files

    def downloadRepoZip(fullrepo:str, saveToPath:str, branch:str):
        import SampleData
        fullurl = f"{fullrepo}/archive/refs/heads/{branch}"
        dataLogic = SampleData.SampleDataLogic()
        downloadedFile = dataLogic.downloadFile(fullurl, saveToPath, branch)
        return downloadedFile
