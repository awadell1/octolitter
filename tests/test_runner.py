from os import environ
from pathlib import Path
from tarfile import is_tarfile
from octolitter.repo import GithubRepo
from octolitter.runner import Runner


GITHUB_API = environ["GITHUB_API"]

def test_install():
    repo = GithubRepo(GITHUB_API, "https://github.com/awadell1/octolitter")
    runner = Runner(repo)
    runner_exe = runner.get_runner_app()
    assert Path(runner_exe).exists()
    assert is_tarfile(runner_exe)

    # Test installing the runner
    assert runner.path.exists() == False
    runner.install()
    assert runner.path.exists()
    assert runner.path.is_dir()

    # Test killing the runner
    runner.kill()
    assert runner.path.exists() == False
