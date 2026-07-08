from tools.qa_runner import run_nextjs_checks


repo = "clients/gta-scrub/repo"


results = run_nextjs_checks(repo)


for check, result in results.items():

    print("\n====", check, "====")

    print(
        "PASSED"
        if result["success"]
        else "FAILED"
    )

    print(
        result["output"][-1000:]
    )
