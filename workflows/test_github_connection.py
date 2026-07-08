from tools.github_tool import get_repo


repo = get_repo("ahraz/gtascrub.com")

print("Connected successfully")

print("Repository:")
print(repo.full_name)

print("Default branch:")
print(repo.default_branch)

print("Latest commit:")
print(repo.get_commits()[0].sha)
