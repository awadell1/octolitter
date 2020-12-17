import logging
import re
from ghapi.core import GhApi


class GithubRepo:
    def __init__(self, api: GhApi, url) -> None:
        # Maintain link back to ghapi
        self.api = api

        # Parse info from URL
        m = re.match(r".*?github.com/([^/]*)/([^/]*)", url)
        if m is None:
            raise RuntimeError(f"Invalid GitHub Repo: {url}")
        else:
            self.owner = m.group(1)
            self.name = m.group(2)
        super().__init__()

    def __repr__(self) -> str:
        return f"{self.owner}/{self.name}"

    def __str__(self) -> str:
        return f"{self.owner}/{self.name}"

    def url(self):
        return f"https://github.com/{self.owner}/{self.name}"

    def get_runner_registration_token(self):
        """ Returns a registration token for a runner """
        return self.api.actions.create_registration_token_for_repo(
            self.owner, self.name
        )

    def list_runner_applications(self):
        logging.debug(
            "actions.list_runner_applications_for_repo(%s, %s)", self.owner, self.name
        )
        return self.api.actions.list_runner_applications_for_repo(self.owner, self.name)

    def get_runner_remove_token(self):
        """ Returns a removal token for a runner """
        logging.debug(
            "actions.create_remove_token_for_repo(%s, %s)", self.owner, self.name
        )
        logging.debug("token: %s", self.api)
        return self.api.actions.create_remove_token_for_repo(self.owner, self.name)
