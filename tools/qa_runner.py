import subprocess


def run_command(command, cwd):

    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout + result.stderr
    }


def run_nextjs_checks(repo_path):

    results = {}

    results["lint"] = run_command(
        "npm run lint",
        repo_path
    )

    results["build"] = run_command(
        "npm run build",
        repo_path
    )

    return results
