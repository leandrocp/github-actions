# GitHub Actions for Elixir and Rust CI

This repository contains reusable GitHub Actions workflows for testing and linting Elixir and Rust projects, encapsulating best practices around artifact caching and linting.

Based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

## Elixir Workflows

### The `elixir-test` workflow

The `elixir-test` workflow does the following:
* Compiles your dependencies, ignoring any warnings
* Compiles your project code with `--warnings-as-errors`
* Runs `mix test`

The test workflow runs in a matrix of the three latest major Elixir and Erlang releases, using the latest minor/patch version of each. Combinations which are not supported are automatically excluded from the matrix.

### The `elixir-lint` workflow

The `elixir-lint` workflow does the following:
* Compiles your dependencies, ignoring any warnings
* Compiles your project code with `--warnings-as-errors`
* Checks for unused dependencies
* Runs `mix format --check-formatted`
* Runs `mix credo --strict`
* Runs `mix dialyzer`

The lint workflow runs on the latest major Elixir and Erlang releases, using the latest minor/patch version of each.

### Usage: Elixir

To use these workflows for an Elixir project, create a `.github/workflows/elixir.yml` file in your repository:

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

You can customize the Elixir and Erlang versions:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
    with:
      elixirs: '["1.17.x", "1.18.x"]'
      erlangs: '["27.x", "28.x"]'
  lint:
    uses: leandrocp/github-actions/.github/workflows/elixir-lint.yml@main
    with:
      elixirs: '["1.18.x"]'
      erlangs: '["28.x"]'
```

If your project requires additional apt packages:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/elixir-test.yml@main
    with:
      apt-packages: 'libsqlite3-dev postgresql-client'
```

## Rust Workflows

### The `rust-test` workflow

The `rust-test` workflow does the following:
* Builds your project with warnings treated as errors
* Runs `cargo test`

The test workflow runs in a matrix of stable, beta, and nightly Rust toolchains by default.

### The `rust-lint` workflow

The `rust-lint` workflow does the following:
* Checks code formatting with `cargo fmt`
* Runs `cargo clippy` with warnings as errors
* Builds your project

The lint workflow runs on the stable Rust toolchain by default.

### Usage: Rust

To use these workflows for a Rust project, create a `.github/workflows/rust.yml` file in your repository:

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

You can customize the Rust versions:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      rust-versions: '["stable", "nightly"]'
  lint:
    uses: leandrocp/github-actions/.github/workflows/rust-lint.yml@main
    with:
      rust-versions: '["stable"]'
```

If your project requires additional apt packages:

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      apt-packages: 'libssl-dev pkg-config'
```

## License

MIT
