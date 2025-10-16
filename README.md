# GitHub Actions for Elixir and Rust CI

Reusable GitHub Actions workflows for testing and linting Elixir and Rust projects.

Initially based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

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
      elixirs: '["1.18.x"]'
      erlangs: '["28.x"]'
```

## Usage: Rust

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

Customize the Rust versions:

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

Use with Rust NIFs (custom manifest path):

```yaml
jobs:
  test:
    uses: leandrocp/github-actions/.github/workflows/rust-test.yml@main
    with:
      manifest-path: 'native/my_nif/Cargo.toml'
  lint:
    uses: leandrocp/github-actions/.github/workflows/rust-lint.yml@main
    with:
      manifest-path: 'native/my_nif/Cargo.toml'
```
