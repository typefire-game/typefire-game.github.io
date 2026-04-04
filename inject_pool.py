#!/usr/bin/env python3
"""
inject_pool.py  —  injects pool data into index.html as an inline script.
Usage: inject_pool.py <pool.b64 file> <public-repo-dir>
"""
import sys, os, re

def main():
    if len(sys.argv) != 3:
        print("Usage: inject_pool.py <pool.b64 file> <public-repo-dir>", file=sys.stderr)
        sys.exit(1)

    b64_file, repo_dir = sys.argv[1], sys.argv[2]

    with open(b64_file, encoding="utf-8") as f:
        b64_str = f.read().strip()

    html_path = os.path.join(repo_dir, "index.html")
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # Replace the inline pool script line
    pattern = r"(<script>window\._POOL_B64 = ')[^']*(';</script>)"
    if not re.search(pattern, content):
        print("[inject] ERROR: inline _POOL_B64 script not found in index.html", file=sys.stderr)
        sys.exit(1)

    new_content = re.sub(pattern, rf"\g<1>{b64_str}\g<2>", content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    size_kb = len(new_content.encode("utf-8")) / 1024
    print(f"[inject] wrote {html_path} ({size_kb:.0f} KB)", file=sys.stderr)

if __name__ == "__main__":
    main()
