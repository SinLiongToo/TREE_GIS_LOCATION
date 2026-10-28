import urllib.request
import json
import urllib.parse
import sys

def search_datagov(query):
    url = f"https://data.gov.tw/api/v2/rest/dataset?q={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("result", {}).get("results", [])
            print(f"=== Results for '{query}' (Found: {len(results)}) ===")
            for item in results:
                title = item.get("title", "")
                dept = item.get("organization_title", item.get("org_name", ""))
                item_id = item.get("id", "")
                print(f"[{item_id}] {title} (Org: {dept})")
                for dist in item.get("distribution", []):
                    fmt = dist.get("format", "")
                    desc = dist.get("resourceDescription", "")
                    d_url = dist.get("downloadUrl") or dist.get("resourceDownloadUrl", "")
                    print(f"    - [{fmt}] {desc}: {d_url}")
            return results
    except Exception as e:
        print(f"Error searching '{query}': {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    search_datagov("受保護樹木")
    search_datagov("珍貴老樹")
    search_datagov("特定紀念樹木")
    search_datagov("老樹")
