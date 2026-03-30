# GitHub Actions for Elixir and Rust CI

Reusable GitHub Actions workflows for testing, linting, and releasing Elixir and Rust projects.

Initially based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

Used by:
- https://github.com/leandrocp/mdex
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
      pairs: '[{"elixir": "1.17.x", "otp": "27.x"}, {"elixir": "1.18.x", "otp": "28.x"}]'
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      pairs: '[{"elixir": "1.18.x", "otp": "28.x"}]'
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
- **`test-msrv`**: Specified MSRV version on LTS OS versions (replaces test-stable)
- **`test-nightly`**: Rust nightly on latest OS versions

This ensures compatibility with your project's minimum supported Rust version.

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

This runs tests on MSRV + nightly (instead of stable + nightly), and verifies that your Cargo.toml's `rust-version` field matches the MSRV.

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
      elixir-version: "1.19"
      otp-version: "28"
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
