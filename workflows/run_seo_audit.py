from tools.seo_audit import scan_files


repo = "clients/gta-scrub/repo"


results = scan_files(repo)


print("\nSEO AUDIT RESULTS\n")


for item in results:

    print("-", item)


print(
    "\nTotal issues:",
    len(results)
)
