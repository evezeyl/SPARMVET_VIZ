# @deps
# provides: script:check_gallery_links
# consumes: assets/gallery_data/*/example_meta.md
# consumed_by: .claude/rules/rules_toolchain.md
# doc: .claude/rules/rules_gallery_standards.md, .claude/rules/rules_asset_scripts.md
# @end_deps
"""Check online that the links of the Gallery guidance pages still answer.

Reads every link of every `example_meta.md` under the gallery directory, asks each distinct address once (HEAD, then
GET when HEAD is refused) with a generic client name, and prints a table: status, address, examples that use it.
It needs the network, so it is not part of the test suite (the offline form check is
`app/tests/test_gallery_link_form.py`). Exit code 1 when any link does not answer 200.
"""
import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]*)\)")
_BARE = re.compile(r"https?://[^\s)>\"]+")


def collect(gallery: Path) -> dict:
    """{address: [example ids]} for every link of every example_meta.md."""
    found: dict = {}
    for meta in sorted(gallery.glob("*/example_meta.md")):
        text = meta.read_text(encoding="utf-8")
        for url in set(_MD_LINK.findall(text)) | set(_BARE.findall(text)):
            url = url.strip()
            if url and not url.startswith("#"):
                found.setdefault(url, []).append(meta.parent.name)
    return found


def status(url: str, timeout: float) -> str:
    """The HTTP status of an address, or the error name."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "gallery-link-check/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as answer:
                return str(answer.status)
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in (403, 405, 501):
                continue
            return str(error.code)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            return f"error:{type(error).__name__}"
    return "error"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gallery-dir", default="assets/gallery_data",
                        help="directory with one folder per example (default: assets/gallery_data)")
    parser.add_argument("--timeout", type=float, default=20.0, help="seconds per request (default: 20)")
    args = parser.parse_args()
    links = collect(Path(args.gallery_dir))
    bad = 0
    print(f"{'status':<14}{'address':<75}examples")
    for url in sorted(links):
        code = status(url, args.timeout)
        bad += code != "200"
        print(f"{code:<14}{url:<75}{', '.join(links[url])}")
    print(f"{len(links)} distinct links, {bad} not answering 200")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
