import os
import re

# Files that should never have SEO metadata (config, types, etc.)
SKIP_FILES = {
    "next.config.js", "next.config.ts", "next.config.mjs",
    "tailwind.config.ts", "tailwind.config.js", "tailwind.config.mjs",
    "postcss.config.js", "postcss.config.mjs",
    "tsconfig.json", "package.json", "package-lock.json",
    ".eslintrc.json", ".eslintrc.js", "prettier.config.js",
    "next-env.d.ts", "env.d.ts", "globals.d.ts",
}

SKIP_SUFFIXES = {".d.ts", ".json", ".css", ".scss", ".less", ".config.js", ".config.ts"}

SKIP_DIR_PATTERNS = {"node_modules", ".next", "dist", "build", ".git", "__pycache__", "public/icons", "public/fonts"}

# Extensions to scan for SEO issues
SCAN_EXTENSIONS = {".html", ".jsx", ".tsx", ".js", ".ts", ".astro", ".vue"}


def _should_skip(filepath: str) -> bool:
    """Skip files that are not user-facing pages or components."""
    basename = os.path.basename(filepath)
    if basename in SKIP_FILES:
        return True
    for suffix in SKIP_SUFFIXES:
        if basename.endswith(suffix):
            return True
    for part in filepath.split(os.sep):
        if part in SKIP_DIR_PATTERNS:
            return True
    # Only scan relevant extensions
    if not any(filepath.endswith(ext) for ext in SCAN_EXTENSIONS):
        return True
    return False


def _check_nextjs_metadata(content: str, filepath: str) -> list:
    """Check a Next.js page/component for proper metadata exports."""
    findings = []
    basename = os.path.basename(filepath)

    # Check for metadata export (app router) or Head component (pages router)
    has_metadata_export = bool(re.search(r"export\s+(const\s+metadata|async\s+function\s+generateMetadata)", content))
    has_head_component = bool(re.search(r"<Head>", content))

    # Only flag as missing if it's a page file (app/ or pages/ directory)
    is_page_file = "/app/" in filepath or "/pages/" in filepath
    is_layout = "layout.tsx" in basename or "layout.jsx" in basename

    if is_page_file and not has_metadata_export and not has_head_component:
        # Don't flag client components that can't export metadata
        is_client = "'use client'" in content or '"use client"' in content
        if not is_client or is_layout:
            findings.append(f"Missing metadata export: {filepath}")

    # Check for meta description in metadata export
    if has_metadata_export:
        has_description = bool(re.search(r"description\s*:", content))
        if not has_description and (is_layout or filepath.endswith("/page.tsx") or filepath.endswith("/page.jsx")):
            findings.append(f"Missing description in metadata: {filepath}")

    return findings


def _check_html_seo(content: str, filepath: str) -> list:
    """Legacy check for plain HTML files."""
    findings = []

    if "<title" not in content:
        findings.append(f"Missing title tag: {filepath}")

    if "description" not in content.lower():
        findings.append(f"Missing meta description: {filepath}")

    return findings


def _check_images(content: str, filepath: str) -> list:
    """Check that <img> tags have alt text."""
    findings = []
    images = re.findall(r"<img\s[^>]*>", content)
    for img in images:
        if "alt=" not in img and "alt =" not in img:
            findings.append(f"Image missing alt text: {filepath}")
    return findings


def scan_files(path: str) -> list:
    """Scan a project for SEO issues. Works with Next.js, Astro, Vue, and plain HTML."""
    findings = []

    for root, dirs, files in os.walk(path):
        # Skip hidden and build dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIR_PATTERNS]

        for file in files:
            if not any(file.endswith(ext) for ext in SCAN_EXTENSIONS):
                continue

            filepath = os.path.join(root, file)
            if _should_skip(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for SEO metadata based on framework
                if "/app/" in filepath or "/pages/" in filepath:
                    findings.extend(_check_nextjs_metadata(content, filepath))
                elif file.endswith(".html"):
                    findings.extend(_check_html_seo(content, filepath))

                # Check images in all file types
                findings.extend(_check_images(content, filepath))

            except (UnicodeDecodeError, IOError):
                pass

    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        if f not in seen:
            seen.add(f)
            unique.append(f)

    return unique
