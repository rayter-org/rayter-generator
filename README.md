# rayter-generator

[![Build Status](https://github.com/rayter-org/rayter-generator/workflows/Tests/badge.svg)](https://github.com/rayter-org/rayter-generator/actions?query=workflow%3ATests)

A static site generator for game ranking leagues.

## Developing

This is more a set of notes than a full-fledged guide.

### Get started
`pip install -e .`

`rayter-generate-website --games-path <path to games folder> --output <output folder>`

`python3 -m http.server 8000` in output folder.

### When done with change
* Commit change.
* Bump version in pyproject.toml and commit.
* `git tag <same version>`
* Push commits and tag.
* Wait for https://github.com/rayter-org/rayter-generator/actions to build.
* Optionally: ask someone to code review.
* Click "Run workflow" on `https://github.com/<your user>/<your games repo>/actions/workflows/build.yml`.
* Go to https://rayter.win to see the result.
