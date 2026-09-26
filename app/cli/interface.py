"""
CLI Interface module for IMM.
Provides terminal commands and rich formatted displays.
"""

import click
from rich.console import Console
from rich.table import Table
from app.config import config
from app.database import init_db, get_db_connection
from app.utils.logger import logger

console = Console()


@click.group()
def cli():
    """IMM - Instagram Modular Manager CLI Tool."""
    pass


@cli.command()
def init():
    """Initializes the SQLite database schema."""
    try:
        init_db()
        console.print("[bold green]✓ Database initialized successfully![/bold green]")
        logger.info("Database initialized via CLI.")
    except Exception as e:
        console.print(f"[bold red]✗ Database initialization failed:[/bold red] {e}")
        logger.error(f"Database initialization failed: {e}")


@cli.command()
def status():
    """Displays current system configuration and database connection status."""
    table = Table(title="IMM System Status")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    summary = config.get_masked_summary()
    for key, val in summary.items():
        table.add_row(key, str(val))

    # Database check
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "[green]Connected[/green]"
    except Exception as e:
        db_status = f"[red]Error ({e})[/red]"

    table.add_row("DB_STATUS", db_status)

    console.print(table)


if __name__ == "__main__":
    cli()
  
