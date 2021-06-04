
import pytest
import mock
import json
import os
import collections
from git_change_request import BaseRequest, ChangeRequest
from git_change_request.lib.exceptions import ChangeRequestException
from git_change_request.lib.helpers.decorators import raise_and_log_exception

def wrap(value):
    """
    The top-level API for wrapping an arbitrary object.

    This only works for ``dict``, ``list`` and ``tuple`` types. If you want
    to wrap other types you may write your own ``wrap`` and pass ``wrapper=``
    to ``DictProxy`` and ``ListProxy``.

    """
    if isinstance(value, dict):
        return ResponseDict(value)
    if isinstance(value, (tuple, list)):
        return ResponseList(value)
    return value


class ResponseDict(collections.Mapping):

    """
    A proxy for a dictionary that allows attribute access to underlying keys.

    You may pass a custom ``wrapper`` to override the logic for wrapping
    various custom types.

    """
    def __init__(self, obj, wrapper=wrap):
        self.obj = obj
        self.wrapper = wrapper

    def __getitem__(self, key):

        return self.wrapper(self.obj[key])

    def __len__(self):
        return self.obj.__len__()

    def __iter__(self):
        return self.obj.__iter__()

    def __getattr__(self, key):

        try:
            return self.wrapper(getattr(self.obj, key))
        except AttributeError:

            try:
                return self[key]
            except KeyError:
                try:
                    key = key.replace('_', '-')
                    return self[key]
                except KeyError:
                    raise AttributeError(key)

    def json(self):

        if isinstance(self.obj, str):
            return self.obj
        return json.dumps(self.obj, indent=2)

    def dict(self):
        if isinstance(self.obj, dict):
            return self.obj
        return json.loads(self.obj)


class ResponseList(collections.Sequence):
    """
    A proxy for a list that allows for wrapping items.

    You may pass a custom ``wrapper`` to override the logic for wrapping
    various custom types.

    """
    def __init__(self, obj, wrapper=wrap):
        self.obj = obj
        self.wrapper = wrapper

    def __getitem__(self, key):
        return self.wrapper(self.obj[key])

    def __len__(self):
        return self.obj.__len__()

    def json(self):

        return json.dumps(self.obj, indent=2)

    def dict(self):

        return self.obj


class TestException(Exception):

    def __init__(self, message, status=404):

        self.message = message
        self._status = status

    @property
    def status(self):
        return self._status


class TestChangeRequests(BaseRequest):

    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.cr = None
        self.sha = None


    @raise_and_log_exception()
    def work_on(self, number):
        self.cr = self._load_response("data/pull.json")
        self.sha = self._load_response("data/sha.json")
        if number != self.cr.number:
            raise TestException(self._load_response("data/missing_pull.json"))

    def get_status(self):
        commit_status = self._load_response("data/sha_status.json")
        return dict(status=commit_status.state)

    def request_reviewers(self, reviewers=None, teams=None):
        pass

    def list(self):
        return [dict(title=self.cr.title, number=self.cr.number)]

    def view(self):
        return self._load_response("data/view.json")

    def _load_response(self, file):
        dir = os.path.dirname(__file__)
        full = os.path.join(dir, file)
        with open(full, 'r') as f:
            return wrap(json.loads((f.read())))


class TestChangeRequest:

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_work_on(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_failed_work_on(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        with pytest.raises(ChangeRequestException) as e:
            cr.work_on(number=42)
            assert "The PR/Commit doesn't exist or your token doesn't have proper permissions." in e.value.args

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_iter(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)
        for pr in cr:
            assert pr.get('title') == "Create umb.txt"
            assert pr.get('number') == 41

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_list(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)
        crs = cr.list()
        for pr in crs:
            assert pr.get('title') == "Create umb.txt"
            assert pr.get('number') == 41

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_fail_checkout_no_number(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        with pytest.raises(ValueError) as e:
            cr.checkout()

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.Repo')
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_checkout_number(mock_get_plugin, mock_repo):
        mock_get_plugin.return_value = TestChangeRequests
        mock_repo.return_value = "success"
        cr = ChangeRequest(repo_url='https://github.com')
        cr.checkout(41)

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.Repo')
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_checkout_worked_on_number(mock_get_plugin, mock_repo):
        mock_get_plugin.return_value = TestChangeRequests
        mock_repo.return_value = "success"
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(41)
        cr.checkout()

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_get_status(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)
        assert cr.get_status().get('status') == 'success'

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_request_reviewers(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)
        cr.request_reviewers(reviewers=['john-doe'])

    @staticmethod
    @mock.patch('git_change_request.lib.apis.change_request.get_change_request_plugin_class')
    def test_view(mock_get_plugin):
        mock_get_plugin.return_value = TestChangeRequests
        cr = ChangeRequest(repo_url='https://github.com')
        cr.work_on(number=41)
        resp = cr.view()
        assert resp.get('number') == 41 and not resp.get('merged')
