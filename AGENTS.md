# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Repository Purpose

This repository provides reusable GitHub Actions workflows for CI/CD in Elixir and Rust projects. It is designed to be referenced by other repositories using the `workflow_call` trigger.

Based on [mtrudel/elixir-ci-actions](https://github.com/mtrudel/elixir-ci-actions).

## Architecture

### Workflow Structure

All workflows are reusable (`on: workflow_call`) and located in `.github/workflows/`:

- **elixir-test.yml**: Runs Elixir tests across multiple Elixir/OTP version combinations
- **elixir-lint.yml**: Lints Elixir code (compile warnings, formatting, unused deps)
- **rust-test.yml**: Runs Rust tests across multiple OS and Rust version combinations
- **rust-lint.yml**: Lints Rust code (rustfmt, clippy)

### Key Design Patterns

1. **Matrix Testing**: All workflows use strategy matrices to test across multiple versions
   - Elixir: Tests against Elixir 1.15 to latest and OTP 26 to latest by default
   - Rust: Tests against stable/beta/nightly and ubuntu/windows/macos by default

2. **Customizable Inputs**: All workflows accept version arrays as JSON strings
   - Example: `elixirs: '["1.17.x", "1.18.x"]'`
   - Example: `rust-versions: '["stable", "nightly"]'`

## Development

- Run `actionlint` to validate workflow syntax and content

## Fetch links for extra context

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://learnxinyminutes.com/yaml
