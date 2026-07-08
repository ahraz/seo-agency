import os
import re


def scan_files(path):

    findings = []

    for root, dirs, files in os.walk(path):

        for file in files:

            if file.endswith(
                (
                    ".html",
                    ".jsx",
                    ".tsx",
                    ".js",
                    ".ts"
                )
            ):

                filepath = os.path.join(
                    root,
                    file
                )

                try:

                    with open(
                        filepath,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read()


                    # Title check
                    if "<title" not in content:
                        findings.append(
                            f"Missing title tag: {filepath}"
                        )


                    # Description check
                    if "description" not in content.lower():
                        findings.append(
                            f"Missing meta description: {filepath}"
                        )


                    # Images
                    images = re.findall(
                        r"<img.*?>",
                        content
                    )

                    for img in images:

                        if "alt=" not in img:

                            findings.append(
                                f"Image missing alt text: {filepath}"
                            )


                except Exception:
                    pass


    return findings
