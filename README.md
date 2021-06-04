# git-change-request
a tool for working with pull/merge requests in a CI context.

## Background
This tool came about because our Jenkins CI was behind a firewall so we couldn't 
use the Jenkins Github plugin out of the box nor did my team want the overhead
of managing a `smee.io` client. Couple that with the fact that in this context the 
closest solution was to setup our dynamic Jenkins agent with the github cli to
pull down the PR for testing but the github client does not handle updating a 
PR's commit status to report the outcome of the downstream status

So with those factors in mind this tool was born with the following goals:

* Be able to checkout a PR locally and update it's status from one tool rather than multiple tools
* Be able to support the above PR workflow in any CI system context without needing CI system plugins/dependencies
* Be able to support the above PR workflow with any remote repo hosting app like GitLab, Bitbucket, etc. 


## Installation
`git-change-request` can be easily installed with a one line command. It is recommended (as best practice) to create a virtual
environment and install ospclientsdk. Please see the commands below to install. Note this is only supported
in python 3.6 and higher.

```
# install python virtualenv
$ pip install python-virtualenv

# create virtualenv
$ virtualenv cr

# activate virtualenv
$ source cr/bin/activate

# install git-change-request
$ (cr) pip install git-change-request
```

## Usage
Let's dive into how to use this the command line tool. 

### Setup
You will need to setup two things to use this tool, a repo url and a personal auth token.
* For authorization, git-change-request supports the `gh cli` environment variables 
  `GH_TOKEN || GITHUB_TOKEN`
* For the repo url git-change-request supports the following options
```

# you can set the following environment variable

$ export GIT_CR_REPO=<repo url from borwser>

# or you can ovverride the variable and pass it on the command line with

git-cr --repo-url "<repo url from the browser>" 
```
<p>&nbsp;</p>

### Command List
Once you've setup the authentication token and repo url. You can begin running commands


#### list
You can list PRs on your repo
```

$ git-cr list [--state <state>]
```

**example**
```
$ git-cr list
[
    {
        "number": 41,
        "title": "Create umb.txt",
        "state": "open"
    }
]
```

**state** - can be the supported GitHub states of *open*, *closed*, *all*. By default if state is not specified
it will list open PRs.

<p>&nbsp;</p>

#### status
You can select to see the status of a PR or update the status of a PR.


##### status get
It will get the full status of a PR, if check-suites are configured for your project the status will 
be included along with the combined commit status
```

$ git-cr status get [--number <PR Number>]
```

**example**
```
$ git-cr status get --number 41
  {
      "checks": {
          "conclusion": "success",
          "status": "completed"
      },
      "status": {
          "state": "pending",
          "statuses": [
              {
                  "state": "success",
                  "context": "\"jenkins downstream tests\"",
                  "description": "\"pytest completed successfully\""
              },
              {
                  "state": "pending",
                  "context": "jenkins downstream tests",
                  "description": "e2e-test running"
              }
          ]
      }
  }
```

**number** - The PR number to query.
<p>&nbsp;</p>

##### status set
It will set the status of a PR with state and relevant information while optionally assign
reviewers to the PR

```

$ git-cr status set [--number <PR Number>] 
                    [--state <state>] 
                    [--context <context>]
                    [--description <description>]
                    [--target-url <url>]
                    [--reviewer <reviewer>, --team <team>]
```

**example**
```
$ git-cr status set --number 41 --state success --context "jenkins downstream tests" --description "pytest completed successfully" --team "test-team"

```

**number** - The PR number to update status on.

**state** - The status of the commit, can be any supported GitHub options *success*, *error*, *failure*, *pending*

**context** - A label to differentiate the status

**description** - A short description of the status

**target-url** - The target URL to associate with this status. This URL will be linked from the GitHub UI to allow users 
to easily see the source of the status.

**reviewer** - A reviewer to assign to the the PR once the status has been updated

**team** - A project team to assign to the PR once the status has been updated
<p>&nbsp;</p>

 #### checkout
 Clone the repo and checkout the PR locally.
 
 It will first attempt to clone the repo to the current working directory. It is the 
 equivalent to running `git clone <repo_url>`. If it is determined that repo already exists it 
 will skip the cloning process, proceed to fetch the PR, create a local branch with a schema 
 of `pull-<number>`, and checkout the branch.
 ``` 
 $ git-cr checkout [--number <number>]
 ```
 
 **example**
 ```
$ ls -lrta
drwxrwxr-x. 29 user user  4096 May  5 12:12 ..
drwxrwxr-x. 29 user user  4096 May  5 12:12 .

$ git-cr checkout --number 41

$ ls -lrta && cd piqe-ocp-lib && git branch --list
drwxrwxr-x. 29 user user  4096 May  5 12:12 ..
drwxrwxr-x. 29 user user  4096 May  5 12:12 .
drwxrwxr-x. 29 user user  4096 May  5 12:12 piqe_ocp_lib
  master
* pull-41
 ```
 
 **number** - The PR number to checkout
<p>&nbsp;</p>

#### view
View a summary of information about the PR.
 ``` 
 $ git-cr view [--number <number>]
 ```
 
 **example**
 ```
$ git-cr view --number 36
 {
     "number": 36,
     "title": "[CSSWA-474] - Library requirements",
     "state": "closed",
     "sha": "bcc84d8a0c1c23b2b2a6d0ef6163a968fe3b3150",
     "merged": true,
     "reviews": [
         {
             "user": "Dannyb48",
             "state": "COMMENTED"
         },
         {
             "user": "gmcrocetti",
             "state": "COMMENTED"
         },
         {
             "user": "btjd",
             "state": "COMMENTED"
         },
         {
             "user": "Dannyb48",
             "state": "COMMENTED"
         },
         {
             "user": "Dannyb48",
             "state": "APPROVED",
             "body": "LGTM"
         },
         {
             "user": "btjd",
             "state": "APPROVED"
         }
     ],
     "status_and_checks": {
         "checks": {
             "conclusion": "success",
             "status": "completed"
         },
         "status": {
             "state": "pending",
             "statuses": []
         }
     }
 }

 ```
 
 **number** - The PR number to view information on.
<p>&nbsp;</p>

 ## Developing Plugins
 
 If you're interested in extending support for other backend repo managers like GitLab, Bitbucket
 or want to write your own GitHub implementation you can do so easily but still leverage
 the same interface, you can do so easily
 
 1. Install git-change-requests
 
 2. Create a python module and/or file where from git-change-request you import `BaseRequest`
 
 3. To enable logging you can create a logger using the `create_logger` function or calling python's `getLogger`
 
 4. Create a setup.py file so that it can register the plugin where git-change-request can find it. 
    Register to `git_cr_plugins`. Please refer 
    [here](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins)                   
    for more information on entry points
    
 5. Finally, export the environment variable `GIT_CR_PLUGIN_NAME` to the plugin class name. This will
    cause the `ChangeRequest` interface to inject the new plugin rather than the default.                                                                                              
    
Below is an example of the process
 ```python
from git_change_request import BaseRequest
from loggin import getLogger

class NewPlugin(BaseRequest):

    def __init__(self, repo_url):

        # creating logger for this plugin to get added to git-change-request's loggers
        self.create_logger(name='newplugin', data_folder=<data folder name>)
        # OR
        logger = getLogger('git_change_request')
        
        self.repo_url = repo_url
        self.cr = None
        
        # init some client using the repo_url
        self.client = SomeClient(repo_url)
    
    def work_on(self, number):
        self.cr = number

    def get_status(self):
        # Your code to get status 
        self.client.get_status(self, self.cr)


    def success(self, **kwargs):
        # when implementing state for status update, set them as first class functions. 
        # for example this success function will be called when a client wants to set
        # the state to 'success' on the commit status

        self.client.create_status(**kwargs)

```

   
```python
   
   from setuptools import setup, find_packages

   setup(
       name='new_plugin',
       version="1.0",
       description="new plugin for git-change-request",
       author="John Doe",
       packages=find_packages(),
       include_package_data=True,
       python_requires=">=3",
       install_requires=[
           'git-change-request',
       ],
       entry_points={
                     'git_cr_plugins': 'new_plugin = <plugin package name>:<NewPluginClass>'
                    }
   )
 ```  

```
export GIT_CR_PLUGIN_NAME = NewPlugin
```

 