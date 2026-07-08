import os
from github import Github
from config.settings import GITHUB_TOKEN


def get_github_client():

    return Github(
        GITHUB_TOKEN
    )


def get_repo(repo_name):

    github = get_github_client()

    return github.get_repo(repo_name)
