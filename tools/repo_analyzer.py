import os
import json
import subprocess

from config.settings import GITHUB_TOKEN


def _embed_token(url: str) -> str:
    """Embed GITHUB_TOKEN into an HTTPS git URL so cloning/pushing
    never prompts for credentials."""
    token = GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return url
    if not url.startswith("https://"):
        return url  # SSH — leave alone
    if f"://{token}@" in url or f":{token}@" in url or token in url:
        return url  # already authed
    return url.replace("https://", f"https://{token}@", 1)


def clone_repo(repo_url, destination):
    if os.path.exists(destination):
        return "Repository already exists"

    authed_url = _embed_token(repo_url)
    try:
        result = subprocess.run(
            ["git", "clone", authed_url, destination],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            # The URL might already be authed from a previous attempt
            # Try stripping the user@ part if it fails
            return f"Clone failed: {result.stderr.strip()[:200]}"
        return "Repository cloned"
    except subprocess.TimeoutExpired:
        return "Clone failed: timed out after 120 seconds"
    except Exception as e:
        return f"Clone failed: {str(e)[:200]}"


def analyze_repo(path):

    report = {}

    # Files
    files = []

    for root, dirs, filenames in os.walk(path):

        for file in filenames:
            relative = os.path.relpath(
                os.path.join(root, file),
                path
            )
            files.append(relative)

    report["total_files"] = len(files)

    # Framework detection
    package_file = os.path.join(path, "package.json")

    if os.path.exists(package_file):

        with open(package_file) as f:
            package = json.load(f)

        report["framework"] = {
            "dependencies": package.get(
                "dependencies",
                {}
            ),
            "scripts": package.get(
                "scripts",
                {}
            )
        }

    # Important SEO files
    seo_files = []

    for f in files:

        name = f.lower()

        if any(
            x in name
            for x in [
                "sitemap",
                "robots",
                "schema",
                "seo",
                "metadata",
                "head",
                "layout"
            ]
        ):
            seo_files.append(f)

    report["seo_related_files"] = seo_files

    # Images
    images = [
        f for f in files
        if f.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".svg"
            )
        )
    ]

    report["images_count"] = len(images)

    report["sample_files"] = files[:100]

    return report
