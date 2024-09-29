# macschedule

`macschedule` provides a CLI to generate `launchd` agents for automating jobs on MacOS quickly from simple, readable yaml configuration files.

## Background

Running automated scripts and jobs on MacOS is usually done using `cron` or more recently `launchd`.
The latter has several advantages and is now the recommended approach from [Apple](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html).
However, for scheduling simple python or bash scripts it can be tedious to manually create the required `.plist` files, copy them to the `~/Library/LaunchAgents` directory, and start and monitor the services.

Therefore, this CLI allows you to:
- Write simple yaml files to define your jobs and store them anywhere you want. Some flexibility in `launchd` is intentionally dropped to make these configurations quick and readable.
- Batch autogenerate all the `.plist` files and directly move them to the user `LaunchAgents` directory as required.
- Start, stop and monitor all your jobs. This is batch wrapper over `launchctl`.
- Quickly check logs from `launchd`. By default this CLI adds output files for `stdout` and `stderr` to improve debugging.

## Usage

Generate `.plist` files from all configurations stored in a folder call "jobs":
```bash
# test output before copying to LaunchAgents
msch generate --dry-run jobs/*
# if everything looks good
msch generate jobs/*
```

Load all the jobs that were just generated:
```bash
msch load jobs/*
```

Unload all the jobs that were just generated:
```bash
msch unload jobs/*
```

Print the tail of the logs from the given jobs:
```bash
# stdout logs
msch logs --stream=stdout --tail=10 jobs/*
# stderr logs
msch logs --stream=stderr --tail=10 jobs/*
```

Cleanup and remove the `.plist` files that were generated in the first step:
```bash
# check what will be deleted
msch remove --dry-run jobs/*
# if everything looks good delete the files
msch remove jobs/*
```

Get help:
```bash
msch --help
```

See `/examples/` for example job configurations and their generated `.plist` files.

## More information

A `launchd` tutorial and documentation is available [here](https://www.launchd.info).
