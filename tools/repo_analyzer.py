import os
import json
import subprocess


def clone_repo(repo_url, destination):

    if os.path.exists(destination):
        return "Repository already exists"

    subprocess.run(
        [
            "git",
            "clone",
            repo_url,
            destination
        ],
        check=True
    )

    return "Repository cloned"


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
