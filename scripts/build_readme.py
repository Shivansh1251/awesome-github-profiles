#!/usr/bin/env python3
"""Validate profiles.json and generate or check the README profile directory."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "profiles.json"
README_PATH = ROOT / "README.md"
START_MARKER = "<!-- PROFILE-LIST:START -->"
END_MARKER = "<!-- PROFILE-LIST:END -->"
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
REQUIRED_FIELDS = {"username", "name", "category", "description"}
FIELD_LIMITS = {"username": 39, "name": 80, "category": 48, "description": 240}


class ProfileDataError(ValueError):
    """Raised when the profile data is invalid."""


def load_profiles() -> list[dict[str, str]]:
    try:
        raw: Any = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileDataError(f"Could not read valid JSON from {DATA_PATH}: {error}") from error

    if not isinstance(raw, list):
        raise ProfileDataError("profiles.json must contain a JSON array.")

    profiles: list[dict[str, str]] = []
    seen_usernames: set[str] = set()

    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ProfileDataError(f"Profile entry {index} must be a JSON object.")

        if set(item) != REQUIRED_FIELDS:
            missing = sorted(REQUIRED_FIELDS - set(item))
            extra = sorted(set(item) - REQUIRED_FIELDS)
            details = []
            if missing:
                details.append(f"missing fields: {', '.join(missing)}")
            if extra:
                details.append(f"unknown fields: {', '.join(extra)}")
            raise ProfileDataError(f"Profile entry {index} has " + "; ".join(details) + ".")

        profile: dict[str, str] = {}
        for field in sorted(REQUIRED_FIELDS):
            value = item[field]
            if not isinstance(value, str):
                raise ProfileDataError(f"Profile entry {index}: {field} must be text.")
            value = " ".join(value.split())
            if not value:
                raise ProfileDataError(f"Profile entry {index}: {field} cannot be empty.")
            if len(value) > FIELD_LIMITS[field]:
                raise ProfileDataError(
                    f"Profile entry {index}: {field} exceeds {FIELD_LIMITS[field]} characters."
                )
            profile[field] = value

        username = profile["username"]
        if not USERNAME_PATTERN.fullmatch(username):
            raise ProfileDataError(
                f"Profile entry {index}: {username!r} is not a valid GitHub username."
            )

        key = username.casefold()
        if key in seen_usernames:
            raise ProfileDataError(f"Duplicate GitHub username: {username}.")
        seen_usernames.add(key)
        profiles.append(profile)

    return profiles


def render_table(profiles: list[dict[str, str]]) -> str:
    if not profiles:
        return (
            "_No profiles have been added yet. "
            "Submit a pull request to add the first GitHub profile._"
        )

    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for profile in profiles:
        by_category[profile["category"]].append(profile)

    lines = [
        "<table>",
        "<thead>",
        "<tr>",
        '<th scope="col">Preview</th>',
        '<th scope="col">GitHub profile</th>',
        '<th scope="col">Focus</th>',
        '<th scope="col">Why it is featured</th>',
        "</tr>",
        "</thead>",
        "<tbody>",
    ]

    category_order = lambda label: (label.casefold() != "project maintainer", label.casefold())
    for category in sorted(by_category, key=category_order):
        for profile in sorted(
            by_category[category],
            key=lambda entry: (entry["name"].casefold(), entry["username"].casefold()),
        ):
            username = profile["username"]
            github_url = f"https://github.com/{username}"
            avatar_url = f"{github_url}.png?size=96"
            name = html.escape(profile["name"], quote=True)
            safe_username = html.escape(username, quote=True)
            safe_category = html.escape(profile["category"], quote=True)
            description = html.escape(profile["description"], quote=True)
            lines.extend(
                [
                    "<tr>",
                    f'<td align="center"><a href="{github_url}"><img src="{avatar_url}" '
                    f'width="64" height="64" alt="GitHub avatar for {safe_username}" /></a></td>',
                    f'<td><a href="{github_url}"><strong>{name}</strong></a><br />'
                    f"<code>@{safe_username}</code></td>",
                    f"<td>{safe_category}</td>",
                    f"<td>{description}</td>",
                    "</tr>",
                ]
            )

    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def replace_generated_section(readme: str, table: str) -> str:
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise ProfileDataError("README.md must contain exactly one pair of profile list markers.")

    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER)
    if end < start:
        raise ProfileDataError("README profile list markers are out of order.")

    content_start = start + len(START_MARKER)
    return readme[:content_start] + "\n" + table + "\n" + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated README section does not match profiles.json",
    )
    args = parser.parse_args()

    try:
        profiles = load_profiles()
        readme = README_PATH.read_text(encoding="utf-8")
        generated = replace_generated_section(readme, render_table(profiles))
    except (OSError, ProfileDataError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.check:
        if generated != readme:
            print(
                "README profile directory is out of date. "
                "Run: python scripts/build_readme.py",
                file=sys.stderr,
            )
            return 1
        print("Profile data and README directory are in sync.")
        return 0

    README_PATH.write_text(generated, encoding="utf-8", newline="\n")
    print("Updated the generated profile directory in README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
