# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Repository Purpose

This repository provides reusable GitHub Actions workflows for CI/CD in Elixir and Rust projects. It is designed to be referenced by other repositories using the `workflow_call` trigger.

Based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

## Architecture

### Workflow Structure

All workflows are reusable (`on: workflow_call`) and located in `.github/workflows/`:

- **elixir-test.yml**: Runs Elixir tests across multiple Elixir/OTP version combinations
- **elixir-lint.yml**: Lints Elixir code and optionally runs Credo; can also install Rust for projects that compile Rust or NIF code
- **rust-test.yml**: Runs Rust tests across stable/MSRV and nightly OS matrices
- **rust-lint.yml**: Lints Rust code (rustfmt, clippy) and optionally verifies MSRV
- **nif-release.yml**: Builds precompiled Rustler NIF artifacts for multiple targets and publishes tagged releases
- **hex-publish.yml**: Publishes Elixir packages to Hex with configurable Elixir/OTP, optional Rust setup, custom env vars, and pre-publish hooks

The repository also includes **validate.yml**, a repository-level workflow that runs `actionlint` for changes under `.github/workflows/`. It is not reusable.

### Key Design Patterns

1. **Matrix Testing**: Reusable workflows use strategy matrices where it makes sense
   - Elixir test: defaults to Elixir 1.19/OTP 28 and `main-otp-28`/`maint-28`
   - Elixir lint: defaults to the same Elixir/OTP pairs and can optionally run Credo
   - Rust test: defaults to stable on LTS runners and nightly on latest runners; when `msrv` is set, an additional MSRV matrix runs on the stable OS set
   - NIF release: builds a target matrix across macOS, Linux, Windows, and FreeBSD targets

2. **Customizable Inputs**: All workflows accept version arrays as JSON strings
   - Example: `pairs: '[{"elixir": "1.17.x", "otp": "27.x"}]'`
   - Example: `rust-versions: '["nightly"]'`
   - Example: `stable-os-versions: '["ubuntu-22.04", "macos-14"]'`
   - Example: `nif-versions: '["2.15", "2.16"]'`

3. **Custom Environment Variables**: Elixir workflows support additional environment variables
   - Accepts JSON object via `env_vars` input
   - Example: `env_vars: '{"MDEX_BUILD": "1"}'`
   - Useful for projects requiring special compilation flags (e.g., forcing NIF builds)

4. **Publishing Workflows**
   - `hex-publish.yml` requires the `HEX_API_KEY` secret
   - `hex-publish.yml` uses `env-vars` (hyphenated) rather than `env_vars`
   - `hex-publish.yml` can install Rust and run a `pre-publish-command` before `publish-command`
   - `nif-release.yml` expects both the Mix app working directory and the Rust project directory when they differ

## Development

- Run `actionlint` to validate workflow syntax and content
- Prefer updating `README.md` when workflow inputs, defaults, or examples change

## Fetch links for extra context

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations
- https://learnxinyminutes.com/yaml
