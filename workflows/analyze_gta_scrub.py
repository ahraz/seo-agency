from tools.repo_analyzer import analyze_repo


location = "clients/gta-scrub/repo"


report = analyze_repo(location)


for key, value in report.items():

    print("\n====", key, "====")

    print(value)
