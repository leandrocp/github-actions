import tempfile
import unittest
from pathlib import Path

from release_changelog import (
    compare_versions,
    release_notes,
    update_changelog,
    update_version,
)


GENERATED = """\
## [0.3.0](https://github.com/leandrocp/example/compare/v0.2.0...v0.3.0) (2026-08-03)

### Features

- Add an API by @contributor in [#12](https://github.com/leandrocp/example/pull/12)

**Full Changelog**: https://github.com/leandrocp/example/compare/v0.2.0...v0.3.0
"""


class ReleaseChangelogTest(unittest.TestCase):
    def test_compare_versions(self):
        self.assertEqual(compare_versions("0.2.0", "0.2.0"), "equal")
        self.assertEqual(compare_versions("0.3.0", "0.2.9"), "greater")
        self.assertEqual(compare_versions("0.2.9", "0.3.0"), "less")
        self.assertEqual(compare_versions("1.0.0", "1.0.0-rc.1"), "greater")

    def test_update_version_requires_one_declaration(self):
        source = 'defmodule Example.MixProject do\n  @version "0.2.0"\nend\n'
        self.assertIn('@version "0.3.0"', update_version(source, "0.3.0"))
        with self.assertRaises(ValueError):
            update_version("defmodule Example do\nend\n", "0.3.0")

    def test_inserts_release_after_title(self):
        changelog = "# Changelog\n\n## [0.2.0]\n\nOld notes.\n"
        updated = update_changelog(changelog, GENERATED)
        self.assertLess(updated.index("## [0.3.0]"), updated.index("## [0.2.0]"))
        self.assertEqual(updated.count("# Changelog"), 1)

    def test_moves_unreleased_notes_into_release(self):
        changelog = (
            "# Changelog\n\n## Unreleased\n\n### Changed\n\n"
            "- Preserve this manual note\n\n## [0.2.0]\n\nOld notes.\n"
        )
        updated = update_changelog(changelog, GENERATED)
        self.assertIn("## Unreleased\n\n## [0.3.0]", updated)
        self.assertIn("- Preserve this manual note", updated)
        self.assertEqual(updated.count("- Preserve this manual note"), 1)

    def test_absorbs_orphan_subsection_as_manual_notes(self):
        changelog = "# Changelog\n\n### Changes\n\n- Manual note\n\n## [0.2.0]\n"
        updated = update_changelog(changelog, GENERATED)
        self.assertLess(updated.index("## [0.3.0]"), updated.index("### Changes"))
        self.assertLess(updated.index("### Changes"), updated.index("## [0.2.0]"))

    def test_extracts_release_body_from_linked_heading(self):
        changelog = f"# Changelog\n\n{GENERATED}\n## [0.2.0]\n\nOld notes.\n"
        notes = release_notes(changelog, "0.3.0")
        self.assertTrue(notes.startswith("### Features"))
        self.assertNotIn("## [0.2.0]", notes)

    def test_extracts_release_body_from_plain_heading(self):
        changelog = "# Changelog\n\n## 0.3.0 (2026-08-03)\n\nNotes.\n"
        self.assertEqual(release_notes(changelog, "0.3.0"), "Notes.\n")

    def test_temp_files_are_ordinary_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CHANGELOG.md"
            path.write_text(f"# Changelog\n\n{GENERATED}")
            self.assertIn("Features", path.read_text())


if __name__ == "__main__":
    unittest.main()
