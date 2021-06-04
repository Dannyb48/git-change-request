import pytest
from git_change_request.bin.change_request_cli import git_cr
from click.testing import CliRunner


@pytest.fixture(scope='class')
def runner():
    return CliRunner()


class TestCli(object):

    @staticmethod
    def test_git_cr_list(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib', 'list'])
        assert results.exit_code == 0

    @staticmethod
    def test_git_cr_list_state(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib',
                                         'list', '--state', 'all'])
        assert len(results.output) > 0


    @staticmethod
    def test_git_cr_get_status(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib',
                                         'status', 'get', '--number', '41'])
        assert results.exit_code == 0

    @staticmethod
    def test_git_cr_get_status_fail(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib',
                                         'status', 'get', '--number', '100'])
        assert results.exit_code == 2

    @staticmethod
    def test_git_cr_set_status(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib',
                                         'status', 'set', '--number', '41', '--state', 'success', '--context',
                                         'css-jenkins downstream tests', '--description',
                                         'pytest completed successfully'])
        assert results.exit_code == 0

    @staticmethod
    def test_git_cr_view(runner):
        results = runner.invoke(git_cr, ['--repo-url', 'https://github.com/piqe-test-libraries/piqe-ocp-lib',
                                         'view', '--number', '41'])
        assert results.exit_code == 0