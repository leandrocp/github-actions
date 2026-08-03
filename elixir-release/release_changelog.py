#!/usr/bin/env python3
"""Update and extract release sections without rewriting changelog history."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)
VERSION_DECLARATION_RE = re.compile(
    r'^(?P<prefix>\s*@version\s+")(?P<version>[^"]+)(?P<suffix>".*)$',
    re.MULTILINE,
)
H2_RE = re.compile(r"^## (?!#)", re.MULTILINE)
UNRELEASED_RE = re.compile(r"^## Unreleased\s*$", re.IGNORECASE | re.MULTILINE)


def semver_key(value: str) -> tuple[int, int, int, tuple[tuple[int, object], ...]]:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise ValueError(f"unsupported semantic version: {value}")

    prerelease = match.group("prerelease")
    if prerelease is None:
        prerelease_key: tuple[tuple[int, object], ...] = ((1, ""),)
    else:
        parts: list[tuple[int, object]] = []
        for identifier in prerelease.split("."):
            parts.append((0, int(identifier)) if identifier.isdigit() else (1, identifier))
        prerelease_key = ((0, ""), *parts)

    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease_key,
    )


def compare_versions(left: str, right: str) -> str:
    left_key = semver_key(left)
    right_key = semver_key(right)
    if left_key == right_key:
        return "equal"
    return "greater" if left_key > right_key else "less"


def update_version(contents: str, version: str) -> str:
    matches = list(VERSION_DECLARATION_RE.finditer(contents))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one @version declaration, found {len(matches)}")
    return VERSION_DECLARATION_RE.sub(
        lambda match: f'{match.group("prefix")}{version}{match.group("suffix")}',
        contents,
        count=1,
    )


def merge_manual_notes(generated: str, manual: str) -> str:
    generated = generated.strip()
    manual = manual.strip()
    if not manual:
        return generated

    heading, separator, generated_body = generated.partition("\n")
    parts = [heading, manual]
    if separator and generated_body.strip():
        parts.append(generated_body.strip())
    return "\n\n".join(parts)


def update_changelog(contents: str, generated: str) -> str:
    if not contents.startswith("# Changelog"):
        raise ValueError("changelog must start with '# Changelog'")

    generated = generated.strip()
    if not generated.startswith("## "):
        raise ValueError("generated release notes must start with a level-two heading")

    unreleased = UNRELEASED_RE.search(contents)
    if unreleased:
        next_heading = H2_RE.search(contents, unreleased.end())
        section_end = next_heading.start() if next_heading else len(contents)
        manual = contents[unreleased.end() : section_end]
        release = merge_manual_notes(generated, manual)
        prefix = contents[: unreleased.end()].rstrip()
        suffix = contents[section_end:].lstrip()
        pieces = [prefix, release]
        if suffix:
            pieces.append(suffix.rstrip())
        return "\n\n".join(pieces) + "\n"

    first_line_end = contents.find("\n")
    if first_line_end == -1:
        return f"# Changelog\n\n{generated}\n"

    after_title = contents[first_line_end + 1 :]
    first_heading = H2_RE.search(after_title)
    pre_release = after_title[: first_heading.start()] if first_heading else after_title
    history = after_title[first_heading.start() :] if first_heading else ""

    if pre_release.strip().startswith("### "):
        release = merge_manual_notes(generated, pre_release)
        preamble = ""
    else:
        release = generated
        preamble = pre_release.strip()

    pieces = ["# Changelog"]
    if preamble:
        pieces.append(preamble)
    pieces.append(release)
    if history.strip():
        pieces.append(history.strip())
    return "\n\n".join(pieces) + "\n"


def release_notes(contents: str, version: str) -> str:
    heading = re.compile(
        rf"^## (?:\[{re.escape(version)}\]|{re.escape(version)})(?:\s|\(|$).*$",
        re.MULTILINE,
    ).search(contents)
    if not heading:
        raise ValueError(f"release section for {version} was not found")

    next_heading = H2_RE.search(contents, heading.end())
    section_end = next_heading.start() if next_heading else len(contents)
    notes = contents[heading.end() : section_end].strip()
    if not notes:
        raise ValueError(f"release section for {version} is empty")
    return notes + "\n"


def prepare(args: argparse.Namespace) -> None:
    version_file = Path(args.version_file)
    changelog_file = Path(args.changelog_file)
    notes_file = Path(args.notes_file)

    version_file.write_text(update_version(version_file.read_text(), args.version))
    changelog_file.write_text(
        update_changelog(changelog_file.read_text(), notes_file.read_text())
    )


def extract(args: argparse.Namespace) -> None:
    notes = release_notes(Path(args.changelog_file).read_text(), args.version)
    Path(args.output).write_text(notes)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)

    compare = commands.add_parser("compare")
    compare.add_argument("left")
    compare.add_argument("right")

    prepare_command = commands.add_parser("prepare")
    prepare_command.add_argument("--version-file", required=True)
    prepare_command.add_argument("--changelog-file", required=True)
    prepare_command.add_argument("--notes-file", required=True)
    prepare_command.add_argument("--version", required=True)

    extract_command = commands.add_parser("extract")
    extract_command.add_argument("--changelog-file", required=True)
    extract_command.add_argument("--version", required=True)
    extract_command.add_argument("--output", required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "compare":
        print(compare_versions(args.left, args.right))
    elif args.command == "prepare":
        prepare(args)
    else:
        extract(args)


if __name__ == "__main__":
    main()
