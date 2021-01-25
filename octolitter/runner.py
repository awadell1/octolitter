import subprocess
import shutil
import platform
import requests
import logging
import json
from pathlib import Path
from uuid import uuid4
from typing import Optional, List

from .repo import GithubRepo


class Runner:
    runner_dir = Path(Path.home(), "github-runner")

    def __init__(self, repo: Optional[GithubRepo], name=None) -> None:
        self.benefactor = repo
        self.name = str(uuid4()) if name is None else name
        self.proc = None

    def __repr__(self) -> str:
        return f"< {self.__class__.__name__} {self.name} >"

    @staticmethod
    def from_dir(api, path):
        """
        Constructs a runner from an existing folder
        """
        path = Path(path)
        assert path.is_dir()
        name = path.name

        runner_file = Path(path, ".runner")
        if not runner_file.is_file():
            repo = None
        else:
            with open(runner_file, "r", encoding="utf-8-sig") as fid:
                runner_info = json.load(fid)

            repo = GithubRepo(api, runner_info["gitHubUrl"])

        return Runner(repo, name)

    @staticmethod
    def from_name(api, name):
        path = Path(Runner.runner_dir, name)
        return Runner.from_dir(api, path)

    @staticmethod
    def discover(api):
        """ Reload all existing runners """
        runners:list[Runner] = []
        for rd in [
            r for r in Runner.runner_dir.joinpath("runners").iterdir() if r.is_dir
        ]:
            logging.info("Creating Runner for %s", rd)
            runners.append(Runner.from_dir(api, rd))
        return runners

    def install(self):
        if not self.path.is_dir():
            github_runner = self.get_runner_app()
            self.path.parent.mkdir(exist_ok=True, parents=True)
            shutil.unpack_archive(str(github_runner.absolute()), str(self.path.absolute()))

    @property
    def path(self) -> Path:
        return Path(self.runner_dir, "runners", self.name)

    def register(self):
        """ Register runner with Github """
        self.install()
        logging.info("Registering %s", self)
        token = self.benefactor.get_runner_registration_token().token
        cmd = [
            Path(self.path, "config.sh"),
            "--url",
            self.benefactor.url(),
            "--token",
            token,
            "--name",
            self.name,
            "--unattended",
        ]
        subprocess.run(cmd, check=True)

    def kill(self):
        """ Stop Runner and deregister """
        logging.info("Killing %s", self)
        if self.benefactor is not None:
            token = self.benefactor.get_runner_remove_token().token
            cmd = [Path(self.path, "config.sh"), "remove", "--token", token]
            subprocess.run(cmd, check=True)

        if self.proc is not None:
            self.proc.terminate()

        shutil.rmtree(self.path)

    def start(self):
        # Start the runner
        self.proc = subprocess.Popen(
            [Path(self.path, "run.sh")], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def get_runner_app(self):
        """Downloads the runner application for the current platform
        runner_bins - output of one of the following
            - list_runner_applications_for_repo
            - list_runner_applications_for_org
        """
        os = platform.system().lower()
        arch = platform.machine().lower()
        runner_bins = self.benefactor.list_runner_applications()

        # Remap to Github Codes
        os_map = {"darwin": "osx", "windows": "win"}
        os = os_map[os] if os in os_map else os
        arch_map = {"x86_64": "x64", "amd64": "x64"}
        arch = arch_map[arch] if arch in arch_map else arch
        is_m1 = os == "osx" and arch == "arm64"

        # Get installer info
        runner = None
        for r in runner_bins:
            if r.os == os and r.architecture == arch:
                runner = r
                break

            # Allow Rossetta Fall back iff alternate is not available
            if is_m1 and r.os == os and r.architecture == "x64" and runner is None:
                runner = r

        if runner is None:
            raise RuntimeError(f"No Gitlab Runner for os: {os}, arch: {arch}")

        # Create cache folder
        file = Path(self.runner_dir, "github", runner.filename).resolve()

        # If missing runner zip -> Download it
        if not file.exists():
            # Download runner from Github and write to disk
            logging.info("Downloading %s to %s", runner.filename, str(file))
            r = requests.get(runner.download_url)
            r.raise_for_status()

            file.parent.mkdir(parents=True, exist_ok=True)
            with open(file, "wb") as fid:
                fid.write(r.content)
            file.chmod(400)
        else:
            logging.info("Reusing %s", str(file))

        return file
