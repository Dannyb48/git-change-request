import click
import json
from ..lib import ChangeRequest


@click.group(name='git-cr')
@click.pass_context
@click.option(
    '--repo-url',
    help='url of the git repo',
    metavar='',
    envvar='GIT_CR_REPO',
    required=False
)
@click.option(
    '--log-level',
    help='logging level. default=INFO',
    metavar='',
    type=click.Choice(['info', 'debug'], case_sensitive=False),
    required=False
)
def git_cr(ctx, repo_url, log_level):
    ctx.obj = ChangeRequest(repo_url=repo_url, log_level=log_level)


@git_cr.command()
@click.option(
    '--number',
    help='pull/merge request number to work on',
    metavar='',
    required=True
)
@click.pass_context
def checkout(ctx, number):
    """
    Clone the repo and checkout the PR locally.

    It will first attempt to clone the repo to the current working directory. It is the
    equivalent to running `git clone <repo_url>`. If it is determined that repo already exists it
    will skip the cloning process, proceed to fetch the PR, create a local branch with a schema
    of `pull-<number>`, and checkout the branch.
    """
    try:
        ctx.obj.work_on(int(number))
        ctx.obj.checkout()
    except Exception as e:
        click.echo(e)
        ctx.exit(2)


@git_cr.command()
@click.option(
    '--number',
    help='pull/merge request number to work on',
    metavar='',
    required=True
)
@click.pass_context
def view(ctx, number):
    """
    View summarized information about the PR.
    """
    try:
        ctx.obj.work_on(int(number))
        resp = ctx.obj.view()
        click.echo(json.dumps(resp, indent=4))
    except Exception as e:
        click.echo(e)
        ctx.exit(2)


@git_cr.command(name='list')
@click.option(
    '--state',
    help='list pull requests by state. Defaults=open',
    metavar='',
    required=False
)
@click.pass_context
def list_change_requests(ctx, state):
    """
    You can list PRs on your repo
    """
    crs = ctx.obj.list(state=state) if state else ctx.obj.list()
    click.echo(json.dumps(crs, indent=4))


@git_cr.group(chain=True)
@click.pass_context
def status(ctx):
    """
    You can select to see the status of a PR or update the status of a PR.
    """
    pass


@status.command(name='get')
@click.option(
    '--number',
    help='pull/merge request number to work on',
    metavar='',
    required=True
)
@click.pass_context
def get_status(ctx, number):
    """
    Get the full status of a PR, if check-suites are configured for your project the status will be included
    along with the combined commit status
    """

    try:
        ctx.obj.work_on(int(number))
        resp = ctx.obj.get_status()
        click.echo(json.dumps(resp, indent=4))
    except Exception as e:
        click.echo(e)
        ctx.exit(2)


@status.command(name='set')
@click.option(
    '--number',
    help='pull/merge request number to work on',
    metavar='',
    required=True
)
@click.option(
    '--state',
    help='state to set on the cr commit',
    type=click.Choice(['pending', 'success', 'failure', 'error'], case_sensitive=False),
    metavar='',
    required=True
)
@click.option(
    '--target-url',
    help='target url to refer to from CI system',
    metavar='',
    required=False
)
@click.option(
    '--context',
    help='label to identify this status',
    metavar='',
    required=False
)
@click.option(
    '--description',
    help='description of the status',
    metavar='',
    required=False
)
@click.option(
    '--reviewer',
    help='reviewer to add',
    metavar='',
    multiple=True,
    type=str,
    required=False
)
@click.option(
    '--team',
    help='project team to add',
    metavar='',
    multiple=True,
    type=str,
    required=False
)
@click.pass_context
def set_status(ctx, number, state, target_url, context, description, reviewer, team):
    """
    Set the status of a PR with state and relevant information while optionally assign reviewers to the PR
    """

    try:
        ctx.obj.work_on(int(number))
        getattr(ctx.obj, state)(target_url=target_url, context=context, description=description)
        if reviewer or team:
            if reviewer:
                reviewer = list(reviewer)
            if team:
                team = list(team)
            ctx.obj.request_reviewers(reviewer, team)
    except Exception as e:
        click.echo(e)
        ctx.exit(2)
