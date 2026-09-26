"""
CLI Interface module for IMM.
Provides comprehensive terminal commands for discovering reels, managing approval queues,
submitting comments, managing blacklists/whitelists, running daemon, and viewing analytics.
"""

import click
from rich.console import Console
from rich.table import Table
from app.config import config
from app.database import init_db, get_db_connection
from app.services.pipeline import AutomationPipeline
from app.services.list_service import ListService
from app.services.approval import ApprovalService
from app.services.scheduler import DaemonScheduler
from app.services.analytics import AnalyticsService
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
    """Displays current system configuration and database status."""
    table = Table(title="IMM System Status")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    summary = config.get_masked_summary()
    for key, val in summary.items():
        table.add_row(key, str(val))

    try:
        conn = get_db_connection()
        conn.close()
        db_status = "[green]Connected[/green]"
    except Exception as e:
        db_status = f"[red]Error ({e})[/red]"

    table.add_row("DB_STATUS", db_status)
    console.print(table)


@cli.command()
@click.option("--target", "-t", required=True, help="Target username or keyword")
@click.option("--mode", "-m", type=click.Choice(["username", "keyword"]), default="username", help="Discovery mode")
@click.option("--limit", "-l", default=5, type=int, help="Number of reels to process")
@click.option("--keyword", "-k", multiple=True, help="Required keyword in caption")
def discover(target: str, mode: str, limit: int, keyword: tuple):
    """Discovers reels, applies filters, and populates pending comment queue."""
    console.print(f"[bold yellow]Searching for reels target: '{target}' ({mode})...[/bold yellow]")
    pipeline = AutomationPipeline()

    criteria = {}
    if keyword:
        criteria["required_keywords"] = list(keyword)

    try:
        stats = pipeline.run_discovery_and_generation(
            target=target,
            mode=mode,
            limit=limit,
            criteria=criteria
        )

        table = Table(title="Discovery Results Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Discovered Reels", str(stats["discovered"]))
        table.add_row("Passed Filters", str(stats["passed_filters"]))
        table.add_row("Unique New Reels", str(stats["unique"]))
        table.add_row("Generated Pending Comments", str(stats["comments_generated"]))

        console.print(table)
    finally:
        pipeline.close()


@cli.command()
def pending():
    """Lists all comments waiting for approval."""
    approval_svc = ApprovalService()
    items = approval_svc.get_pending_comments()

    if not items:
        console.print("[bold green]No pending comments in queue.[/bold green]")
        return

    table = Table(title=f"Pending Comments Queue ({len(items)} items)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Reel ID", style="yellow")
    table.add_column("Comment Text", style="white")
    table.add_column("Status", style="magenta")

    for item in items:
        table.add_row(str(item.id), item.reel_id, item.comment_text, item.status)

    console.print(table)


@cli.command()
@click.option("--id", "comment_id", type=int, help="Specific comment ID to approve")
@click.option("--all", "approve_all", is_flag=True, help="Approve all pending comments")
@click.option("--text", help="Update comment text before approving")
def approve(comment_id: int, approve_all: bool, text: str):
    """Approves pending comment(s) for submission."""
    approval_svc = ApprovalService()

    if approve_all:
        pending_items = approval_svc.get_pending_comments()
        for item in pending_items:
            approval_svc.approve_comment(item.id)
        console.print(f"[bold green]✓ Approved all {len(pending_items)} pending comments![/bold green]")
    elif comment_id:
        approval_svc.approve_comment(comment_id, updated_text=text)
        console.print(f"[bold green]✓ Approved comment ID {comment_id}![/bold green]")
    else:
        console.print("[bold red]Please specify --id <ID> or --all[/bold red]")


@cli.command()
@click.option("--limit", "-l", default=5, type=int, help="Max batch submission count")
def submit(limit: int):
    """Submits approved comments queue with rate limiting."""
    console.print("[bold yellow]Processing approved submission batch...[/bold yellow]")
    pipeline = AutomationPipeline()
    try:
        results = pipeline.process_approved_submissions(batch_limit=limit)

        table = Table(title="Submission Results")
        table.add_column("Status", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Successfully Submitted", str(results["submitted"]))
        table.add_row("Failed", str(results["failed"]))
        table.add_row("Skipped (Rate Limit)", str(results["skipped_rate_limit"]))

        console.print(table)
    finally:
        pipeline.close()


@cli.command()
@click.option("--add", help="Add username or term to list")
@click.option("--type", "list_type", type=click.Choice(["blacklist", "whitelist"]), default="blacklist")
@click.option("--reason", help="Reason for adding entry")
@click.option("--show", type=click.Choice(["blacklist", "whitelist"]), help="Display entries")
def lists(add: str, list_type: str, reason: str, show: str):
    """Manages blacklists and whitelists."""
    list_svc = ListService()

    if add:
        success = list_svc.add_entry(add, list_type, reason)
        if success:
            console.print(f"[bold green]✓ Added '{add}' to {list_type}.[/bold green]")
        else:
            console.print(f"[bold red]Failed to add entry.[/bold red]")
    elif show:
        entries = list_svc.get_entries(show)
        table = Table(title=f"{show.capitalize()} Entries ({len(entries)})")
        table.add_column("Value", style="cyan")
        table.add_column("Reason", style="yellow")
        table.add_column("Added At", style="magenta")

        for entry in entries:
            table.add_row(entry["entry_value"], entry["reason"] or "-", entry["created_at"])

        console.print(table)
    else:
        console.print("[bold yellow]Use --add <value> --type <type> or --show <type>[/bold yellow]")


@cli.command()
@click.option("--target", "-t", required=True, help="Target username or keyword")
@click.option("--interval", "-i", default=30, type=int, help="Interval between runs in minutes")
@click.option("--mode", "-m", type=click.Choice(["username", "keyword"]), default="username", help="Discovery mode")
@click.option("--limit", "-l", default=5, type=int, help="Batch limit per run")
@click.option("--auto-submit", is_flag=True, help="Automatically submit approved comments each cycle")
def daemon(target: str, interval: int, mode: str, limit: int, auto_submit: bool):
    """Runs IMM pipeline continuously in background daemon mode."""
    console.print(f"[bold green]Starting IMM Daemon for target '{target}' every {interval} minutes...[/bold green]")
    console.print("[dim]Press Ctrl+C to stop smoothly.[/dim]")

    scheduler = DaemonScheduler(interval_minutes=interval)
    scheduler.start(
        target=target,
        mode=mode,
        limit=limit,
        auto_submit=auto_submit
    )


@cli.command()
@click.option("--export", "-e", help="Export analytics summary to JSON file path")
def report(export: str):
    """Displays system activity analytics and performance metrics."""
    analytics_svc = AnalyticsService()
    stats = analytics_svc.get_summary_stats()

    table = Table(title="IMM Activity Analytics")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Total Discovered Reels", str(stats["total_reels"]))
    table.add_row("Total Comments Created", str(stats["total_comments"]))
    table.add_row("Pending Approval", str(stats["pending_comments"]))
    table.add_row("Approved (Ready)", str(stats["approved_comments"]))
    table.add_row("Successfully Submitted", str(stats["submitted_comments"]))
    table.add_row("Rejected", str(stats["rejected_comments"]))
    table.add_row("Failed", str(stats["failed_comments"]))
    table.add_row("Success Rate (%)", f"{stats['success_rate_pct']}%")

    console.print(table)

    if export:
        success = analytics_svc.export_report_json(export)
        if success:
            console.print(f"[bold green]✓ Report exported successfully to {export}[/bold green]")
        else:
            console.print("[bold red]✗ Failed to export report.[/bold red]")


if __name__ == "__main__":
    cli()
    
