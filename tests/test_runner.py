from os import environ
from pathlib import Path
from tarfile import is_tarfile
from octolitter.repo import GithubRepo
from octolitter.runner import Runner


GITHUB_TOKEN = environ["GITHUB_TOKEN"]

def test_install():
    repo = GithubRepo(GITHUB_TOKEN, "https://github.com/awadell1/octolitter")
    runner = Runner(repo)
    runner_exe = runner.get_runner_app()
    assert Path(runner_exe).exists()
    assert is_tarfile(runner_exe)

