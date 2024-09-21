import os
from typing import List, Generator, Tuple

import click

from macschedule.job_configs import JobConfig
from macschedule.generate import PListGenerator
from macschedule.operate import PListLoader
from macschedule.logs import LaunchdLogReader
from macschedule.constants import LAUNCHAGENTS_DIR, LOGS_DIR


def _create_dirs() -> None:
    """Create the required directories if they do not already exist."""
    os.makedirs(os.path.expanduser(LAUNCHAGENTS_DIR), mode=0o755, exist_ok=True)
    os.makedirs(os.path.expanduser(LOGS_DIR), mode=0o755, exist_ok=True)


def _read_configs(jobfiles: List[str]) -> Generator[Tuple[str, JobConfig], None, None]:
    """Read and validate the yaml job configurations."""
    for jobfile in jobfiles:
        if jobfile.endswith(".yaml") or jobfile.endswith(".yml"):
            try:
                config = JobConfig.from_file(jobfile)
            except Exception as err:
                click.secho(f"Unable to read file {jobfile} -> {err}", fg="red")
                continue
            yield jobfile, config


@click.group()
@click.version_option()
def cli():
    _create_dirs()


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Do not copy .plist files to the LaunchAgents directory. Prints .plist to stdout.",
)
@click.option("-U", "--update", is_flag=True, help="Update/overwrite existing jobs.")
@click.argument("jobfiles", nargs=-1, type=click.Path(exists=True))
def generate(dry_run, update, jobfiles):
    """Generate or update .plist files from given .yaml configurations.

    JOBFILES are the paths to the .yaml job configurations.
    """
    click.secho("MacSchedule: Generating .plist files", bold=True)
    for jobfile, config in _read_configs(jobfiles):
        if dry_run:
            click.secho(f"{jobfile} ->", fg="blue")
            click.echo(PListGenerator(config).populate_plist().print_plist())
        else:
            if not update and os.path.exists(config.output_filepath()):
                click.secho(
                    f"{jobfile} -> {config.output_filepath()} already exists. "
                    "Use -U to overwrite.",
                    fg="red",
                )
                continue
            click.secho(f"{jobfile} -> {config.output_filepath()}", fg="blue")
            PListGenerator(config).populate_plist().write_plist()
    click.secho("Done", bold=True)


@click.command()
@click.option("--dry-run", is_flag=True, help="List files that would be removed.")
@click.argument("jobfiles", nargs=-1, type=click.Path(exists=True))
def remove(dry_run, jobfiles):
    """Remove .plist files from the LaunchAgents directory.

    JOBFILES are the paths to the .yaml job configurations.
    """
    click.secho("MacSchedule: Removing .plist files", bold=True)
    for jobfile, config in _read_configs(jobfiles):
        if dry_run:
            if os.path.exists(config.output_filepath()):
                click.secho(f"{jobfile} -> Would remove {config.output_filepath()}", fg="yellow")
        else:
            if os.path.exists(config.output_filepath()):
                click.secho(f"{jobfile} -> Removing {config.output_filepath()}", fg="yellow")
                os.remove(config.output_filepath())
    click.secho("Done", bold=True)


@click.command()
@click.argument("jobfiles", nargs=-1, type=click.Path(exists=True))
def load(jobfiles):
    """Batch load jobs using `launchctl load`.

    JOBFILES are the paths to the .yaml job configurations.
    """
    click.secho("MacSchedule: Loading .plist files", bold=True)
    for jobfile, config in _read_configs(jobfiles):
        click.secho(f"{jobfile} -> Loading {config.output_filepath()}", fg="blue")
        try:
            PListLoader(config).load()
        except Exception as err:
            click.secho(err, fg="red")
    click.secho("Done", bold=True)


@click.command()
@click.argument("jobfiles", nargs=-1, type=click.Path(exists=True))
def unload(jobfiles):
    """Batch unload jobs using `launchctl unload`.

    JOBFILES are the paths to the .yaml job configurations.
    """
    click.secho("MacSchedule: Unloading .plist files", bold=True)
    for jobfile, config in _read_configs(jobfiles):
        click.secho(f"{jobfile} -> Unloading {config.output_filepath()}", fg="yellow")
        try:
            PListLoader(config).unload()
        except Exception as err:
            click.secho(err, fg="red")
    click.secho("Done", bold=True)


@click.command()
@click.option(
    "--stream",
    default="stdout",
    type=click.Choice(["stdout", "stderr"]),
    help="Print stdout or stderr logs.",
)
@click.option("--tail", default=10, type=int, help="Number of lines to tail on the log.")
@click.argument("jobfiles", nargs=-1, type=click.Path(exists=True))
def logs(stream, tail, jobfiles):
    """View logs for given jobs.

    JOBFILES are the paths to the .yaml job configurations.
    """
    click.secho("MacSchedule: Viewing logs", bold=True)
    for jobfile, config in _read_configs(jobfiles):
        log = LaunchdLogReader(config).read(stream, tail)
        if log is None:
            click.secho(f"{jobfile} -> No log file. Job may have not run yet.", fg="red")
        else:
            click.secho(f"{jobfile} ->", fg="blue")
            click.echo(log)
    click.secho("Done", bold=True)


cli.add_command(generate)
cli.add_command(remove)
cli.add_command(load)
cli.add_command(unload)
cli.add_command(logs)
