# -*- coding: utf-8 -*-
"""CLI commands for backup and restore."""
from __future__ import annotations

import tarfile
import time
from pathlib import Path

import click

from ..constant import WORKING_DIR, SECRET_DIR


@click.group("backup", help="Backup and restore ProwlrBot data.")
def backup_group() -> None:
    pass


@backup_group.command("create")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output file path. Defaults to ~/.prowlrbot/backups/<timestamp>.tar.gz",
)
@click.option(
    "--include-secrets",
    is_flag=True,
    default=False,
    help="Include secrets directory in backup.",
)
def backup_create(output: str | None, include_secrets: bool) -> None:
    """Create a backup of ProwlrBot data."""
    backup_dir = WORKING_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if output:
        out_path = Path(output)
    else:
        timestamp = time.strftime("%Y-%m-%dT%H-%M-%S")
        out_path = backup_dir / f"{timestamp}.tar.gz"

    click.echo(f"Creating backup: {out_path}")

    with tarfile.open(str(out_path), "w:gz") as tar:
        # Backup working directory (config, chats, skills, etc.)
        if WORKING_DIR.is_dir():
            for item in WORKING_DIR.iterdir():
                if item.name == "backups":
                    continue  # Don't backup the backups
                tar.add(str(item), arcname=f"prowlrbot/{item.name}")
                click.echo(f"  + {item.name}")

        # Optionally include secrets
        if include_secrets and SECRET_DIR.is_dir():
            for item in SECRET_DIR.iterdir():
                tar.add(str(item), arcname=f"prowlrbot.secret/{item.name}")
                click.echo(f"  + [secret] {item.name}")

    size_mb = out_path.stat().st_size / (1024 * 1024)
    click.echo(f"Backup complete: {out_path} ({size_mb:.1f} MB)")


@backup_group.command("restore")
@click.argument("backup_file", type=click.Path(exists=True))
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing files without prompting.",
)
def backup_restore(backup_file: str, force: bool) -> None:
    """Restore ProwlrBot data from a backup."""
    backup_path = Path(backup_file)

    if not force:
        click.confirm(
            f"This will overwrite existing data in {WORKING_DIR}. Continue?",
            abort=True,
        )

    click.echo(f"Restoring from: {backup_path}")

    with tarfile.open(str(backup_path), "r:gz") as tar:
        for member in tar.getmembers():
            if member.name.startswith("prowlrbot/"):
                # Strip the prowlrbot/ prefix and extract to WORKING_DIR
                member.name = member.name[len("prowlrbot/"):]
                tar.extract(member, path=str(WORKING_DIR))
                click.echo(f"  > {member.name}")
            elif member.name.startswith("prowlrbot.secret/"):
                member.name = member.name[len("prowlrbot.secret/"):]
                tar.extract(member, path=str(SECRET_DIR))
                click.echo(f"  > [secret] {member.name}")

    click.echo("Restore complete.")


@backup_group.command("list")
def backup_list() -> None:
    """List available backups."""
    backup_dir = WORKING_DIR / "backups"
    if not backup_dir.is_dir():
        click.echo("No backups found.")
        return

    backups = sorted(backup_dir.glob("*.tar.gz"), reverse=True)
    if not backups:
        click.echo("No backups found.")
        return

    click.echo(f"Backups in {backup_dir}:")
    for b in backups:
        size_mb = b.stat().st_size / (1024 * 1024)
        click.echo(f"  {b.name}  ({size_mb:.1f} MB)")
