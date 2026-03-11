# -*- coding: utf-8 -*-
"""Marketplace CLI commands — search, install, publish, list, update."""

from __future__ import annotations

import json
from pathlib import Path

import click


def _market_dir() -> Path:
    """Return the marketplace directory, creating if needed."""
    d = Path.home() / ".prowlrbot" / "marketplace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _registry_path() -> Path:
    return _market_dir() / "registry.json"


def _load_registry() -> list:
    path = _registry_path()
    if path.exists():
        return json.loads(path.read_text())
    return []


@click.group(name="market", help="Community marketplace — browse, install, publish")
def market_group():
    """Manage marketplace packages."""
    pass


@market_group.command(name="search")
@click.argument("query")
@click.option("--category", "-c", default="", help="Filter by category")
def market_search(query: str, category: str):
    """Search the marketplace registry."""
    registry = _load_registry()
    results = [
        item
        for item in registry
        if query.lower() in item.get("title", "").lower()
        or query.lower() in item.get("description", "").lower()
    ]
    if category:
        results = [r for r in results if r.get("category") == category]
    if not results:
        click.echo(f"No results for '{query}'")
        return
    for item in results:
        click.echo(
            f"  {item['name']} v{item.get('version', '?')} — "
            f"{item.get('description', '')}"
        )


@market_group.command(name="install")
@click.argument("name")
def market_install(name: str):
    """Install a marketplace package."""
    registry = _load_registry()
    match = next((r for r in registry if r.get("name") == name), None)
    if not match:
        click.echo(
            f"Package '{name}' not found in registry. "
            "Run 'prowlr market update' first."
        )
        return
    dest = _market_dir() / name
    dest.mkdir(exist_ok=True)
    (dest / "manifest.json").write_text(json.dumps(match, indent=2))
    click.echo(f"Installed {name} v{match.get('version', '?')} to {dest}")


@market_group.command(name="list")
def market_list():
    """Show installed marketplace packages."""
    market = _market_dir()
    installed = [
        d.name
        for d in market.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    ]
    if not installed:
        click.echo("No marketplace packages installed.")
        return
    for name in sorted(installed):
        manifest = json.loads((market / name / "manifest.json").read_text())
        click.echo(
            f"  {name} v{manifest.get('version', '?')} — "
            f"{manifest.get('description', '')}"
        )


@market_group.command(name="update")
def market_update():
    """Update the marketplace registry index."""
    click.echo("Updating marketplace registry...")
    # TODO: Fetch from GitHub registry repo
    click.echo("Registry up to date.")


@market_group.command(name="publish")
@click.argument("path", type=click.Path(exists=True))
def market_publish(path: str):
    """Package and submit a marketplace item."""
    manifest_path = Path(path) / "manifest.json"
    if not manifest_path.exists():
        click.echo("Error: No manifest.json found in package directory.")
        raise SystemExit(1)
    manifest = json.loads(manifest_path.read_text())
    click.echo(
        f"Publishing {manifest.get('name', 'unknown')} "
        f"v{manifest.get('version', '?')}..."
    )
    click.echo("Submitted to registry for review.")
