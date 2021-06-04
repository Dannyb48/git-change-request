
from .base_request import BaseRequest
from ..helpers import raise_and_log_exception
from github import Github, CheckSuite, Commit
from urllib.parse import urlparse
from typing import Iterator, Dict, List, Union
import os


class GithubRequest(BaseRequest):

    def __init__(self, repo):
        token = os.getenv('GH_TOKEN') if not os.getenv('GITHUB_TOKEN', None) else os.getenv('GITHUB_TOKEN')
        self.repo = Github(token).get_repo(urlparse(repo).path[1:])
        self.cr = None
        self.sha = None

    def __iter__(self) -> Iterator[dict]:

        for pull in self.list():
            yield pull

    @raise_and_log_exception()
    def work_on(self, number: int):
        self.cr = self.repo.get_pull(number)
        self.sha = self._get_latest_commit()

    @raise_and_log_exception()
    def get_status(self) -> Dict[str, str]:
        resp = dict(checks=dict(conlusion='', status=''), status=dict(state='', statuses=''))
        resp['checks'] = self._get_pr_check_suite_status()
        resp['status'] = self._get_commit_status()
        self.logger.debug(resp)
        return resp

    @raise_and_log_exception()
    def request_reviewers(self, reviewers: Union[List[str], None] = None, teams: Union[List[str], None] = None):
        params = dict()
        if reviewers:
            params.setdefault('reviewers', reviewers)
        if teams:
            params.setdefault('team_reviewers', teams)
        self.cr.create_review_request(**params)

    @raise_and_log_exception()
    def list(self, **kwargs: Dict[str, str]) -> List[dict]:
        pulls = []
        if kwargs:
            pulls = self.repo.get_pulls(**kwargs)
        else:
            pulls = self.repo.get_pulls()

        return self._normalize_list(pulls)

    @raise_and_log_exception()
    def view(self) -> Dict[str, str]:
        summary = dict()
        summary['number'] = self.cr.number
        summary['title'] = self.cr.title
        summary['state'] = self.cr.state
        summary['sha'] = self.sha.sha
        summary['merged'] = self.cr.merged
        reviews = self.cr.get_reviews()
        if reviews.totalCount != 0:
            summary['reviews'] = []
            for review in reviews:
                summary['reviews'].append(dict(user=review.user.login, state=review.state))
                if review.body:
                    summary['reviews'][-1].update(dict(body=review.body))
        summary['status_and_checks'] = self.get_status()

        return summary

    @raise_and_log_exception()
    def pending(self, target_url: Union[str, None] = None, context: Union[str, None] = None,
                description: Union[str, None] = None):
        params = dict(state='pending')
        if target_url:
            params.setdefault('target_url', target_url)
        if context:
            params.setdefault('context', context)
        if description:
            params.setdefault('description', description)
        self.sha.create_status(**params)

    @raise_and_log_exception()
    def success(self, target_url: Union[str, None] = None, context: Union[str, None] = None,
                description: Union[str, None] = None):
        params = dict(state='success')
        if target_url:
            params.setdefault('target_url', target_url)
        if context:
            params.setdefault('context', context)
        if description:
            params.setdefault('description', description)
        self.sha.create_status(**params)

    @raise_and_log_exception()
    def error(self, target_url: Union[str, None] = None, context: Union[str, None] = None,
              description: Union[str, None] = None):
        params = dict(state='error')
        if target_url:
            params.setdefault('target_url', target_url)
        if context:
            params.setdefault('context', context)
        if description:
            params.setdefault('description', description)
        self.sha.create_status(**params)

    @raise_and_log_exception()
    def failure(self, target_url: Union[str, None] = None, context: Union[str, None] = None,
                description: Union[str, None] = None):
        params = dict(state='failure')
        if target_url:
            params.setdefault('target_url', target_url)
        if context:
            params.setdefault('context', context)
        if description:
            params.setdefault('description', description)
        self.sha.create_status(**params)

    @raise_and_log_exception()
    def _get_latest_commit(self) -> Commit:

        return self.cr.get_commits().reversed[0]

    @raise_and_log_exception()
    def _get_latest_check_suite(self) -> CheckSuite:

        return self.sha.get_check_suites().reversed[0]

    @raise_and_log_exception()
    def _get_pr_check_suite_status(self) -> Dict[str, str]:

        resp = dict(conclusion='', status='')
        suite = self._get_latest_check_suite()
        self.logger.debug(suite)
        resp['conclusion'] = suite.conclusion
        resp['status'] = suite.status
        self.logger.debug(resp)
        return resp

    @raise_and_log_exception()
    def _get_commit_status(self) -> Dict[str, str]:
        resp = dict(state='', statuses=[])
        status = self.sha.get_combined_status()
        self.logger.debug(status)
        resp['state'] = status.state
        if status.statuses:
            for s in status.statuses:
                resp['statuses'].append(dict(state=s.state, context=s.context, description=s.description))
        self.logger.debug(resp)
        return resp

    def _normalize_list(self, pulls) -> List[dict]:
        dict_pulls = []
        for pull in pulls:
            dict_pulls.append(dict(number=pull.number, title=pull.title, state=pull.state))
        return dict_pulls
