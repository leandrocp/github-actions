# GitHub Actions for Elixir and Rust CI

Reusable GitHub Actions workflows for testing, linting, and releasing Elixir and Rust projects.

Initially based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

Used by:
- https://github.com/leandrocp/mdex
- https://github.com/leandrocp/mdex_native
- https://github.com/leandrocp/mdex_gfm
- https://github.com/leandrocp/mdex_mermaid
- https://github.com/leandrocp/mdex_katex
- https://github.com/leandrocp/nimble_publisher_mdex
- https://github.com/leandrocp/lumis
- https://github.com/leandrocp/req_embed
- https://github.com/leandrocp/err

## Usage: Elixir

```yaml
name: Elixir CI

on:
  push:
    branches: [ main ]
  pull_request:
  workflow_dispatch:

jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
```

Customize the Elixir and Erlang versions:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
    with:
      pairs: '[{"elixir": "1.17.x", "otp": "27.x"}, {"elixir": "1.20.x", "otp": "29.x"}]'
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      pairs: '[{"elixir": "1.20.x", "otp": "29.x"}]'
```

Pass custom environment variables (useful for NIFs or special build requirements):

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
    with:
      env_vars: '{"MDEX_BUILD": "1"}'
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      env_vars: '{"MDEX_BUILD": "1", "CUSTOM_VAR": "value"}'
```

Run tests with coverage enabled:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
    with:
      coverage: true
```

Coverage thresholds are configured by the project through `test_coverage` in `mix.exs`.

Enable optional Credo checks and pass extra arguments when needed:

```yaml
jobs:
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      credo: true
      credo_args: "--strict"
```

Install Rust for Elixir jobs that compile Rust or NIF code:

```yaml
jobs:
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      rust-toolchain: stable
      env_vars: '{"MIX_ENV": "test", "MDEX_BUILD": "1"}'
```

### Release pull requests

`elixir-release.yml` uses [git-cliff](https://git-cliff.org/) to maintain a
categorized release pull request. Release notes credit the pull request author,
omit dependency and housekeeping commits, and do not add a first-contribution
section. Merging the release pull request tags its merge commit and creates the
GitHub Release.

For `0.x` packages, features bump the patch version and breaking changes bump
the minor version. At `1.0.0` and later, features bump minor and breaking
changes bump major.

The caller keeps the trigger because reusable workflows cannot define when a
repository should release:

```yaml
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/elixir-release.yml@main
    secrets:
      release_token: ${{ secrets.RELEASE_PLEASE_TOKEN }}
```

The existing token can be reused; no GitHub App or additional token is needed.
It must be able to push branches and tags, create pull requests, and create
releases. A personal access token is required instead of `GITHUB_TOKEN` when
the created tag must trigger another workflow, such as Hex or NIF publishing.

Defaults assume `mix.exs` contains one `@version "x.y.z"` declaration,
`CHANGELOG.md` starts with `# Changelog`, release tags use `vX.Y.Z`, and at least
one release tag already exists. Override paths for an umbrella or nested package:

```yaml
jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/elixir-release.yml@main
    with:
      working-directory: packages/my_package
      version-file: mix.exs
      changelog-file: CHANGELOG.md
      release-branch: release/my-package
    secrets:
      release_token: ${{ secrets.RELEASE_PLEASE_TOKEN }}
```

## Usage: Rust

Basic usage with default settings:

```yaml
name: Rust CI

on:
  push:
    branches: [ main ]
  pull_request:
  workflow_dispatch:

jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
  lint:
    uses: leandrocp/github-actions/.github/workflows/rust-lint.yml@main
```

### Default Test Strategy

Tests run in two separate job groups:
- **`test-stable`**: Rust stable on proven LTS OS versions
  - ubuntu-22.04, windows-2022, macos-14 (3 jobs)
- **`test-nightly`**: Rust nightly on latest OS versions
  - ubuntu-latest, windows-latest, macos-latest (3 jobs)

Total: 6 test jobs by default.

**MSRV Testing:** When you specify an MSRV (Minimum Supported Rust Version), tests run on:
- **`test-msrv`**: Specified MSRV version on LTS OS versions
- **`test-stable`**: Rust stable on LTS OS versions
- **`test-nightly`**: Rust nightly on latest OS versions

This adds three MSRV jobs for a total of 9 test jobs. The three groups run in
parallel when using `rust-test.yml`.

### Opt-in Stable Gate

Use the `test-stage` input to call `rust-test.yml` in two stages. Put `needs`
on the compatibility call so its MSRV and nightly matrices start only after
every stable job passes:

```yaml
jobs:
  test-stable:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      test-stage: stable

  test-compatibility:
    needs: test-stable
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      test-stage: compatibility
      msrv: '1.82.0'
```

`test-stage` accepts `all` (the default), `stable`, or `compatibility`.
Existing callers keep the fully parallel behavior. If stable fails, GitHub
skips the downstream reusable workflow call and its compatibility jobs.
Successful gated runs may take longer because compatibility waits for the
slowest stable runner.

### Customization Examples

**Test only stable (skip nightly):**
```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      nightly-os-versions: '[]'
```

**Test on specific OS versions:**
```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      stable-os-versions: '["ubuntu-22.04"]'
      nightly-os-versions: '["ubuntu-latest", "macos-latest"]'
```

**Use with Rust NIFs (custom manifest path):**
```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      manifest-path: 'native/my_nif/Cargo.toml'
      stable-os-versions: '["ubuntu-22.04", "macos-14"]'
  lint:
    uses: leandrocp/github-actions/.github/workflows/rust-lint.yml@main
    with:
      manifest-path: 'native/my_nif/Cargo.toml'
```

**Test selected packages from a workspace in one job matrix:**
```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      manifest-path: 'Cargo.toml'
      test-args: >-
        --package my_core
        --package my_cli
```

`test-args` is appended to `cargo nextest run` for the stable, MSRV, and nightly
jobs. Selecting multiple workspace packages this way avoids repeating the full
OS and toolchain matrix for each package.

**Test and verify Minimum Supported Rust Version (MSRV):**
```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      msrv: '1.82.0'
  lint:
    uses: leandrocp/github-actions/.github/workflows/rust-lint.yml@main
    with:
      msrv: '1.82.0'
```

This runs tests on stable, MSRV, and nightly, and verifies that your
Cargo.toml's `rust-version` field matches the MSRV.

## Usage: NIF Release

Build and release precompiled NIFs for multiple platforms:

```yaml
name: NIF Release

on:
  push:
    branches: [main]
    paths: ["native/**", ".github/workflows/nif-release.yml"]
    tags: ["*"]
  pull_request:
    paths: [".github/workflows/nif-release.yml"]
  workflow_dispatch:

jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/nif-release.yml@main
    with:
      project-name: my_nif
      project-dir: native/my_nif
```

Customize NIF versions:

```yaml
jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/nif-release.yml@main
    with:
      project-name: my_nif
      project-dir: native/my_nif
      nif-versions: '["2.15", "2.16"]'
```

Customize feature variants:

```yaml
jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/nif-release.yml@main
    with:
      project-name: my_nif
      project-dir: native/my_nif
      feature-variants: '[{"features":"","variant":""},{"features":"syntect","variant":"syntect"},{"features":"","variant":"no_syntax_highlighter"}]'
```

Upload artifacts to Cloudflare R2:

```yaml
jobs:
  release:
    uses: leandrocp/github-actions/.github/workflows/nif-release.yml@main
    with:
      project-name: my_nif
      project-dir: native/my_nif
      r2-path: releases/download/${{ github.ref_name }}
    secrets:
      R2_ACCOUNT_ID: ${{ secrets.R2_ACCOUNT_ID }}
      R2_ACCESS_KEY_ID: ${{ secrets.R2_ACCESS_KEY_ID }}
      R2_SECRET_ACCESS_KEY: ${{ secrets.R2_SECRET_ACCESS_KEY }}
      R2_BUCKET: ${{ secrets.R2_BUCKET }}
```

Disabled by default, artifacts are uploaded under `r2-path`.

## Usage: Hex Publish

Keep the trigger in the consumer repo and call the reusable workflow from here:

```yaml
name: Publish

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

jobs:
  publish:
    uses: leandrocp/github-actions/.github/workflows/hex-publish.yml@main
    secrets: inherit
```

Customize versions or publish command when needed:

```yaml
jobs:
  publish:
    uses: leandrocp/github-actions/.github/workflows/hex-publish.yml@main
    with:
      elixir-version: "1.20"
      otp-version: "29"
      working-directory: "."
      publish-command: "mix hex.publish --yes"
    secrets: inherit
```

Use extra environment variables, install Rust, or run a pre-publish step when publishing packages that build Rust or NIF code:

```yaml
jobs:
  publish:
    uses: leandrocp/github-actions/.github/workflows/hex-publish.yml@main
    with:
      working-directory: "."
      env-vars: '{"MDEX_BUILD": "1"}'
      install-rust: true
      rust-version: stable
      pre-publish-command: "mix deps.compile"
    secrets: inherit
```
