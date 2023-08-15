<div align="center">
  <h1>Dotbot Hostname Conditional Plugin<br>
  <sub><sup><code>dotbot-ifhostname</code></sup></sub></h1>
</div>

[![License][shield-license]][url-license]
![Programming Language][shield-language]
[![CI Results][shield-ci]][url-ci]
[![Code Coverage][shield-codecov]][url-codecov]

A plugin for conditional execution of [Dotbot][url-dotbot] directives based on
the hostname of the machine.

Inspired by [dotbot-if][url-dotbot-if] and [dotbot-ifplatform][url-dotbot-ifplatform].


## Prerequisites
This is a plugin for [Dotbot][url-dotbot], requiring it to be available.

## Installation
1. Add [dotbot-ifhostname][url-repo] as a submodule to your dotfiles repository:
```bash
git submodule add https://github.com/johnlettman/dotbot-ifhostname.git
```

2. Pass the CLI argument `--plugin-dir path/to/dotbot-ifhostname` when executing the `dotbot` command.

## Usage
Add the `ifhostname` directive to the [Dotbot][url-dotbot] YAML configuration file
to conditionally execute the directives:
```yaml

- ifhostname:
  hostname: computer-a
  met:
  - shell:
    - echo on computer A!

- ifhostname:
  hostname: computer-b
  met:
  - shell:
    - echo on computer B!
  unmet:
  - shell:
    - echo this isn't computer B!

```

## Details
The following configuration options are available for the `ifhostname` directive:

| Option     | Required | Description                                             |
|------------|----------|---------------------------------------------------------|
| `hostname` | Yes      | The hostname to match against.                          |
| `met`      | No       | Directives to execute when the hostname matches.        |
| `unmet`    | No       | Directives to execute when the hostname does not match. |


[url-dotbot]: https://github.com/anishathalye/dotbot
[url-dotbot-if]: https://github.com/wonderbeyond/dotbot-if
[url-dotbot-ifplatform]: https://github.com/ssbanerje/dotbot-ifplatform

[url-repo]: https://github.com/johnlettman/dotbot-ifhostname
[url-license]: https://github.com/johnlettman/dotbot-ifhostname/blob/main/LICENSE
[url-ci]: https://github.com/johnlettman/dotbot-ifhostname/actions/workflows/ci.yml
[url-codecov]: https://app.codecov.io/gh/johnlettman/dotbot-ifhostname

[shield-license]: https://img.shields.io/badge/License-MIT-green?style=for-the-badge
[shield-language]: https://img.shields.io/github/languages/top/johnlettman/dotbot-ifhostname?style=for-the-badge
[shield-ci]: https://img.shields.io/github/actions/workflow/status/johnlettman/dotbot-ifhostname/ci.yml?style=for-the-badge&label=CI
[shield-codecov]: https://img.shields.io/codecov/c/github/johnlettman/dotbot-ifhostname?style=for-the-badge
