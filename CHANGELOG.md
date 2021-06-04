# Version 0.3.0 (2021-06-04)

## New features
* None

## Enhancements
* None

## Bug Fixes
* None

## Doc Changes
* None

## Test/CI Enhancements
* Update create_release workflow to use PAT vs the GitHub App token
  because it does not support cascading triggering of workflows that utilize 
  the token.


# Version 0.2.0 (2021-06-04)

## New features
* None

## Enhancements
* None

## Bug Fixes
* None

## Doc Changes
* None

## Test/CI Enhancements
* Fixed the publish_package workflow to trigger manually and on 
  release events published/created
* Added a command to output only the recent changelog of the release
  and add that to the github release rather than the full running
  changelog


# Version 0.1.0 (2021-06-03)

## New features
* First initial release of the git-change-requests
* Supports the following github features
    * Listing PRs from a repo
    * Getting the status of a PR
    * Setting the commit status of PR
    * Cloning the repo and checking out a PR locally

## Enhancements
* None

## Bug Fixes
* None

## Doc Changes
* None

## Test/CI Enhancements
* None