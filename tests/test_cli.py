from io import StringIO
import re
import pytest
from contextlib import redirect_stderr, redirect_stdout
from subprocess import call
from octolitter.cli import cli

def call_octolitter(args=[]):
    """ Check that help message is displayed """
    f = StringIO()
    with redirect_stdout(f):
        cli(args)
    return f.getvalue()

def call_octolitter_error(args=[]):
    """ Check that help message is displayed """
    f = StringIO()
    with redirect_stderr(f):
        with pytest.raises(SystemExit) as exec:
            cli(args)

    return f.getvalue(), exec

def test_main_help():
    s = call_octolitter()
    assert re.match("usage: octolitter.*", s)
    assert re.search("Error", s, re.IGNORECASE) == None

def test_subcmd_help():
    for subcmd in ["add", "rm"]:
        s, e = call_octolitter_error([subcmd])
        assert e.value.code == 2
        assert re.match(f"usage: octolitter {subcmd}.*", s)
