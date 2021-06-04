from .base_request import BaseRequest
from git import Repo
from urllib.parse import urlparse
from ..helpers import get_change_request_plugin_class
from typing import Iterator, Dict, List, Union
import os


class ChangeRequest(BaseRequest):

    def __init__(self, repo_url, log_level='info'):

        self.create_logger(name='git_change_request', data_folder='/tmp/git_cr', log_level=log_level)

        self.repo_url = repo_url
        self.change_request = get_change_request_plugin_class(urlparse(repo_url).netloc.lower())(repo_url)

    def __iter__(self) -> Iterator[dict]:
        for cr in self.change_request.list():
            yield cr

    def work_on(self, number: int):
        self.change_request.work_on(number)

    def get_status(self) -> Dict[str, str]:
        return self.change_request.get_status()

    def request_reviewers(self, reviewers: Union[List[str], None] = None, teams: Union[List[str], None] = None):
        self.change_request.request_reviewers(reviewers, teams)

    def list(self, **kwargs: Dict[str, str]) -> List[dict]:
        return self.change_request.list(**kwargs)

    def view(self) -> Dict[str, str]:
        return self.change_request.view()

    def checkout(self, number: Union[int, None] = None):
        if number is None and self.change_request.cr is None:
            raise ValueError("Can't checkout a change request without a number.")

        if number is None:
            number = self.change_request.cr.number

        dest_folder = self.repo_url.split('/')[-1]
        branch_name = f"pull-{number}"
        clone = None
        self.logger.info(f"cloning from {self.repo_url} to {dest_folder}")
        if os.getcwd().find(dest_folder) != -1:
            clone = Repo(os.getcwd())
        elif os.path.exists(dest_folder):
            clone = Repo(dest_folder)
        else:
            clone = Repo.clone_from(self.repo_url, dest_folder)
        clone.remote().fetch(refspec=f'pull/{number}/head:{branch_name}')
        clone.branches[-1].checkout()

    def __getattr__(self, item):

        # Using this to get the attribute from the change request implementation
        # on state being using dynamically. Not ever implementation will have the same
        # state.
        if hasattr(self.change_request, item):
            return getattr(self.change_request, item)
        else:
            raise AttributeError(f"The {item} doesn't exist. It could be possible it's not an implemented state.")
