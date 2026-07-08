from tools.git_manager import merge_pull_request


repo = "ahraz/gtascrub.com"

pr_number = 1


result = merge_pull_request(
    repo,
    pr_number
)


print(
    "Merged:",
    result
)
