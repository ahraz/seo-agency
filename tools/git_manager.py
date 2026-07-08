import subprocess
import os
from github import Github
from config.settings import GITHUB_TOKEN


def _ensure_token_remote(repo_path):
    """Rewrite the origin remote URL to embed the GITHUB_TOKEN so
    `git push` doesn't prompt for a username/password."""
    token = GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return  # no token available, let normal auth handle it

    result = subprocess.run(
        "git remote get-url origin",
        cwd=repo_path, shell=True, capture_output=True, text=True
    )
    url = result.stdout.strip()
    if not url:
        return  # no remote set

    # If the token is already embedded, skip
    if f"://{token}@" in url or f":{token}@" in url or token in url:
        return

    # Inject token into the URL
    if url.startswith("https://"):
        authed_url = url.replace("https://", f"https://{token}@", 1)
    else:
        return  # SSH — can't inject token; user must have keys set up

    subprocess.run(
        f"git remote set-url origin {authed_url}",
        cwd=repo_path, shell=True, capture_output=True, text=True
    )


def run_git(command, cwd):
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr


def create_branch(repo_path, branch_name):
    return run_git(
        f"git checkout -b {branch_name}",
        repo_path
    )


def git_status(repo_path):
    return run_git(
        "git status",
        repo_path
    )


def commit_changes(repo_path, message):
    run_git("git add .", repo_path)
    return run_git(f'git commit -m "{message}"', repo_path)


def push_branch(repo_path, branch_name):
    _ensure_token_remote(repo_path)
    return run_git(f"git push origin {branch_name}", repo_path)


def create_pull_request(repo_name, title, body, branch):
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body, head=branch, base="main")
    return pr.number


def merge_pull_request(repo_name, pr_number):
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    result = pr.merge(commit_message="Auto merge: SEO agent update")
    return result.merged

