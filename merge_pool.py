#!/usr/bin/env python3
"""
TYPEFIRE merge_pool.py
Two modes:

  Extract mode:
    python merge_pool.py <index.html> --extract <output.json>

  Merge mode:
    python merge_pool.py <index.html> --merge <new_passages.json> <pool.b64>
"""

import sys, re, gzip, base64, json

POOL_MAX = 500

def extract_pool(html_path):
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    # Match inline: <script>window._POOL_B64 = '...';</script>
    m = re.search(r"window\._POOL_B64 = '([^']+)'", content)
    if not m:
        print("[merge] no existing pool found, starting fresh", file=sys.stderr)
        return []
    try:
        compressed = base64.b64decode(m.group(1).strip())
        passages = json.loads(gzip.decompress(compressed).decode("utf-8"))
        print(f"[merge] extracted {len(passages)} existing passages", file=sys.stderr)
        return passages
    except Exception as e:
        print(f"[merge] could not decode pool: {e}, starting fresh", file=sys.stderr)
        return []

def main():
    if len(sys.argv) < 4:
        print("Usage: merge_pool.py <index.html> --extract <out.json>")
        print("       merge_pool.py <index.html> --merge <new.json> <pool.b64>")
        sys.exit(1)

    html_path = sys.argv[1]
    mode = sys.argv[2]

    if mode == "--extract":
        out_json = sys.argv[3]
        passages = extract_pool(html_path)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(passages, f, ensure_ascii=True)
        print(f"[merge] saved to {out_json}", file=sys.stderr)

    elif mode == "--merge":
        if len(sys.argv) < 5:
            print("Usage: merge_pool.py <index.html> --merge <new.json> <pool.b64>", file=sys.stderr)
            sys.exit(1)
        new_json = sys.argv[3]
        out_b64  = sys.argv[4]

        existing = extract_pool(html_path)

        with open(new_json, encoding="utf-8") as f:
            new_passages = json.load(f)
        print(f"[merge] {len(new_passages)} new passages", file=sys.stderr)

        merged = existing + new_passages
        if len(merged) > POOL_MAX:
            drop = len(merged) - POOL_MAX
            print(f"[merge] dropping {drop} oldest passages (FIFO)", file=sys.stderr)
            merged = merged[drop:]

        print(f"[merge] final pool: {len(merged)} passages", file=sys.stderr)

        raw = json.dumps(merged, ensure_ascii=True)
        compressed = gzip.compress(raw.encode("utf-8"), compresslevel=9)
        b64 = base64.b64encode(compressed).decode("ascii")

        with open(out_b64, "w", encoding="utf-8") as f:
            f.write(b64)
        print(f"[merge] pool.b64 written ({len(b64)} chars)", file=sys.stderr)

    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
