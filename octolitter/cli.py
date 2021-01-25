#!/usr/bin/env python3
import logging
import argparse
from sys import argv
from pathlib import Path
from os import getenv
from ghapi.core import GhApi

from .repo import GithubRepo
from .runner import Runner


def cli_add_runners(args):
    # Authenticate
    github = GhApi(token=args.api)

    # Get Repo info
    repo = GithubRepo(github, args.repo)
    logging.info("Will add runner for %s", repo)
    runner = []
    for n in range(args.n):
        r = Runner(repo)
        logging.debug("Adding Runner %d of %d: %s", n, args.n, r)
        r.install()
        r.register()
        r.start()


def cli_remove_runners(args):
    # Authenticate
    github = GhApi(token=args.api)

    if args.all is True:
        for runner in Runner.discover(github):
            logging.info(github.actions.create_remove_token_for_repo("awadell1", "CellFit-BatteryArchive"))
            logging.info(runner.benefactor.api.actions.create_remove_token_for_repo("awadell1", "CellFit-BatteryArchive"))
            runner.kill()
    else:
        Runner.from_name(github, args.runner).kill()


def __cli_default(p: argparse.ArgumentParser):
    p.add_argument(
        "--api",
        default=getenv("GITHUB_API"),
        help="Github Personal Access Token. Defaults to GITHUB_API",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Be more verbose. Stacks up to 3",
    )

    p.set_defaults(func=lambda x: p.print_usage())


def cli(cli_args=argv[1:]):
    parser = argparse.ArgumentParser(
        prog="octolitter",
        description="Quickly spin up a litter of Github Runners",
    )
    __cli_default(parser)
    subp = parser.add_subparsers(help="SubCommands")

    # Adding Runners
    add = subp.add_parser(name="add")
    __cli_default(add)
    add.add_argument(
        "-n", metavar="N", type=int, default=1, help="Add N Runners to REPO"
    )
    add.add_argument("repo", help="Github URL for REPO")
    add.set_defaults(func=cli_add_runners)

    # Remove Runners
    remove = subp.add_parser("rm")
    __cli_default(remove)
    target = remove.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--all", help="Remove all runners", action="store_true", default=False
    )
    target.add_argument(
        "--runner", metavar="RUNNER", help="Remove RUNNER", default=None
    )
    remove.set_defaults(func=cli_remove_runners)

    parser.set_defaults(func=lambda x: parser.print_usage())
    args = parser.parse_args(cli_args)

    # Set logging level
    logLevel = min(logging.ERROR - 10 * args.verbose, logging.DEBUG)
    logging.basicConfig(level=logLevel)

    # Run Subcommand
    args.func(args)
