
import os
import re
from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([a-zA-Z0-9.]+)['"]''')

def get_version():
    """Return the version number"""
    init = open(os.path.join(ROOT, 'git_change_request', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


def get_long_description():
    """Returns README.md content."""
    return open("README.md", "r").read()


setup(
    name="git_change_request",
    version=get_version(),
    author="Danny Baez",
    author_email="danny.baez.jr@gmail.com",
    description=" tool for working with pull/merge requests in a CI context.",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license='GPLv3',
    url="https://github.com/Dannyb48/git-change-request",
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'PyGithub',
        'GitPython',
        'click'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': ['git-cr=git_change_request.bin.change_request_cli:git_cr'],
        'git_cr_plugins': [
            'github_request = git_change_request.lib.apis:GithubRequest'
        ],

    }
)
