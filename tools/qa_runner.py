import subprocess
import os
from crewai.tools import tool


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


@tool("Run Shell Command")
def run_shell_command(command: str, cwd: str = ".") -> str:
    """Run a shell command inside the repo directory and return the output.
    Use for npm build, npm run lint, git status, etc.
    - command: the shell command to run (e.g. 'npm run build')
    - cwd: directory to run in (relative to current working dir)
    """
    abs_cwd = os.path.abspath(cwd)
    result = subprocess.run(
        command,
        cwd=abs_cwd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr
    if result.returncode == 0:
        return f"✅ Command succeeded:\n{output[:3000]}"
    else:
        return f"❌ Command failed (exit {result.returncode}):\n{output[:3000]}"


def run_nextjs_checks(repo_path):
    results = {}

    # Install dependencies if node_modules missing
    node_modules = os.path.join(repo_path, "node_modules")
    if not os.path.exists(node_modules):
        install_result = run_command("npm install", repo_path)
        results["install"] = install_result
        if not install_result["success"]:
            return results

    results["lint"] = run_command(
        "npm run lint",
        repo_path
    )

    results["build"] = run_command(
        "npm run build",
        repo_path
    )

    return results
