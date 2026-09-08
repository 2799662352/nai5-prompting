#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check whether danbooru tags exist and how many posts they have.

This answers exactly one question the writing rules care about: "does this spelling
exist as a tag, and how strong is it?" It cannot tell you a character's role, who
holds what, or relative positions — see 写法-词组与句子.md §4.2 for those limits.

Usage:
    python scripts/lookup_tag.py "cat ears" outstretched_hand nagasaki_soyo

Requires network access (danbooru.donmai.us). Standard library only.
Exit codes: 0 = all tags found, 1 = at least one tag missing, 2 = network/API error.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://danbooru.donmai.us/tags.json"
# danbooru rejects requests without a descriptive User-Agent.
USER_AGENT = "nai5-prompting-skill/1.2 (+https://github.com/Miint-Sunny/nai5-prompting)"
# Public tag lookups normally answer well under 5 s; 15 s leaves room for slow links
# without hanging an agent's turn.
TIMEOUT_SECONDS = 15

CATEGORY = {0: "general", 1: "artist", 3: "copyright", 4: "character", 5: "meta"}


def normalize(raw):
    # Prompts write "cat ears"; danbooru stores "cat_ears".
    return raw.strip().lower().replace(" ", "_")


def query(name):
    # name_or_alias_matches resolves aliases, so a deprecated spelling still returns
    # the canonical tag instead of a false "not found".
    params = {"search[name_or_alias_matches]": name, "limit": "5"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def describe(name, rows):
    if not rows:
        return "NOT FOUND   %s" % name, False
    rows = sorted(rows, key=lambda r: r.get("post_count", 0), reverse=True)
    lines = []
    for r in rows:
        alias = "" if r.get("name") == name else "   (alias of your spelling -> use this name)"
        lines.append("%-11s %-40s posts=%-8d %s%s" % (
            CATEGORY.get(r.get("category"), "cat%s" % r.get("category")),
            r.get("name", "?"), r.get("post_count", 0),
            "" if r.get("post_count", 0) else "(0 posts: tag exists but is empty)", alias))
    return "\n".join(lines), True


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    all_found = True
    for raw in argv:
        name = normalize(raw)
        try:
            rows = query(name)
        except urllib.error.HTTPError as e:
            hint = " (rate limited: wait a few seconds and retry)" if e.code == 429 else ""
            print("ERROR       %s: HTTP %s%s" % (name, e.code, hint))
            return 2
        except (urllib.error.URLError, OSError) as e:
            print("ERROR       %s: no network or danbooru unreachable (%s)" % (name, e))
            return 2
        except ValueError:
            print("ERROR       %s: unexpected non-JSON response from danbooru" % name)
            return 2
        text, found = describe(name, rows)
        all_found = all_found and found
        print(text)
    print("\npost count only tells you the spelling exists and how common it is;"
          " it says nothing about roles, ownership or positions.")
    return 0 if all_found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
