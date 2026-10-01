import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "elixir-release/cliff.toml"
BODY = ROOT / "git-cliff/release-notes.tera"
CLI = os.environ.get("GIT_CLIFF", "git-cliff")


class ReleaseNotesTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("GIT_CLIFF_", "GIT_CONFIG_"))
        }
        self.env.update({
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_AUTHOR_DATE": "2026-10-01T12:00:00Z",
            "GIT_COMMITTER_DATE": "2026-10-01T12:00:00Z",
        })
        self.run_command("git", "init", "-q")
        self.commit("chore: initial release")
        self.run_command("git", "tag", "v0.1.0")

    def run_command(self, *args):
        result = subprocess.run(
            args, cwd=self.repo, env=self.env, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def commit(self, message):
        self.run_command(
            "git", "-c", "commit.gpgsign=false", "commit",
            "--allow-empty", "-qm", message,
        )

    def cliff(self, *args):
        return self.run_command(CLI, "--offline", "--config", str(CONFIG), *args)

    def context(self):
        context = json.loads(self.cliff("--unreleased", "--context"))
        context[0]["timestamp"] = 1790856000
        return context

    def render(self, context, *args):
        path = self.repo / "context.json"
        path.write_text(json.dumps(context))
        return self.cliff(
            "--body-file", str(BODY), "--github-repo", "leandrocp/example",
            "--from-context", str(path), *args,
        )

    def test_pr_author_title_scope_and_parser_order(self):
        self.commit("fix(api): original fix")
        self.commit("feat: new capability")
        context = self.context()
        release = context[0]
        release["version"] = "v0.1.1"
        for commit in release["commits"]:
            commit["remote"] = dict(commit["github"])
            if commit["group"] == "Bug Fixes":
                commit["remote"].update(
                    username="merge-maintainer", pr_author="contributor",
                    pr_title="fix(api): clearer fix title", pr_number=42,
                )
            else:
                commit["remote"]["username"] = "leandrocp"
        notes = self.render(context)
        self.assertIn("## [0.1.1](https://github.com/leandrocp/example/compare/v0.1.0...v0.1.1)", notes)
        self.assertLess(notes.index("### Features"), notes.index("### Bug Fixes"))
        self.assertIn("- New capability", notes)
        self.assertNotIn("by @leandrocp", notes)
        self.assertIn(r"- **api:** Clearer fix title by @contributor in [\#42](https://github.com/leandrocp/example/pull/42)", notes)
        self.assertNotIn("merge-maintainer", notes)
        self.assertNotIn("original fix", notes)
        self.assertNotIn("\n\n\n", notes)

        feature = next(commit for commit in release["commits"] if commit["group"] == "Features")
        for pr_author, username, credit in [
            ("leandrocp", "merge-maintainer", ""),
            ("contributor", "leandrocp", " by @contributor"),
            (None, "contributor", " by @contributor"),
            (None, "leandrocp", ""),
        ]:
            with self.subTest(pr_author=pr_author, username=username):
                feature["remote"].update(pr_author=pr_author, username=username, pr_number=43)
                notes = self.render(context)
                self.assertIn(
                    "- New capability" + credit + r" in [\#43](https://github.com/leandrocp/example/pull/43)",
                    notes,
                )
                self.assertNotIn("by @leandrocp", notes)
                self.assertNotIn("by @merge-maintainer", notes)

    def test_package_tags_first_release_and_breaking_commit(self):
        self.commit("feat(core)!: change API")
        context = self.context()
        release = context[0]
        release["version"] = "cargo-example/v0.2.0"
        release["previous"]["version"] = "cargo-example/v0.1.0"
        notes = self.render(context)
        self.assertIn("## [0.2.0]", notes)
        self.assertIn("/compare/cargo-example/v0.1.0...cargo-example/v0.2.0", notes)
        self.assertIn("**core:** **Breaking:** Change API", notes)
        release["previous"] = None
        notes = self.render(context)
        self.assertIn("/tree/cargo-example/v0.2.0", notes)
        self.assertNotIn("/compare/", notes)

    def test_unreleased_without_remote_metadata(self):
        self.commit("fix: direct commit")
        notes = self.render(self.context())
        self.assertIn("## Unreleased", notes)
        self.assertIn("- Direct commit", notes)
        self.assertNotIn(" by @", notes)

    def test_formatting_preserves_prepended_history(self):
        self.commit("fix: new change")
        context = self.context()
        context[0]["version"] = "v0.1.1"
        history = "## [0.1.0]\n\n*   Old item\n\n\nUnusual spacing.\n"
        path = self.repo / "CHANGELOG.md"
        path.write_text(history)
        self.render(context, "--unreleased", "--prepend", str(path), "--strip", "header")
        notes = path.read_text()
        self.assertTrue(notes.endswith(history))
        self.assertEqual(notes.count("## [0.1.1]"), 1)

    def test_housekeeping_does_not_bump_or_appear(self):
        for message in ["chore: release v0.1.0", "chore(deps): update deps", "ci: update workflow"]:
            self.commit(message)
        self.assertEqual(self.cliff("--unreleased", "--bumped-version").strip(), "v0.1.0")
        self.commit("fix: visible fix")
        notes = self.render(self.context())
        self.assertIn("Visible fix", notes)
        self.assertNotIn("update", notes.lower())
        self.assertNotIn("release v0.1.0", notes)

    def test_zero_based_version_policy(self):
        self.commit("feat: new feature")
        self.assertEqual(self.cliff("--unreleased", "--bumped-version").strip(), "v0.1.1")
        self.commit("fix!: breaking fix")
        self.assertEqual(self.cliff("--unreleased", "--bumped-version").strip(), "v0.2.0")

    def test_stable_version_policy(self):
        self.run_command("git", "tag", "v1.0.0")
        self.commit("feat: new feature")
        self.assertEqual(self.cliff("--unreleased", "--bumped-version").strip(), "v1.1.0")
        self.commit("fix!: breaking fix")
        self.assertEqual(self.cliff("--unreleased", "--bumped-version").strip(), "v2.0.0")


if __name__ == "__main__":
    unittest.main()
