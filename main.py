import argparse
import logging
import sys
import os
from dotenv import load_dotenv

from app.database import Database
from app.services.pipeline import PipelineManager

# Setup logging system
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("IMM")


def cmd_init(args):
    """Initializes project database and required directories."""
    print("Initializing IMM environment...")
    db = Database()
    print("Database and tables initialized successfully at data/imm.db")


def cmd_status(args):
    """Displays system status, active sessions, and current rate limit cooldowns."""
    load_dotenv()
    db = Database()
    session_id = os.getenv("INSTAGRAM_SESSION_ID")
    session_file_exists = os.path.exists("data/session.json")

    print("\n=================== IMM System Status ===================")
    print(f"Session JSON File (data/session.json) : {'PRESENT' if session_file_exists else 'MISSING'}")
    print(f"ENV Session ID (INSTAGRAM_SESSION_ID) : {'PRESENT' if session_id else 'MISSING'}")

    print("\n---------------- Rate Limit Status ----------------")
    endpoints = ["user_lookup", "reels_discovery", "session_init"]
    any_rate_limit = False

    for ep in endpoints:
        info = db.get_rate_limit_info(ep)
        if info:
            any_rate_limit = True
            is_active = db.is_rate_limited(ep)
            status_text = "ACTIVE COOLDOWN (PAUSED)" if is_active else "EXPIRED (CLEARED)"
            print(f"Endpoint: {ep:<15} | Status: {status_text:<25} | Until: {info['cooldown_until']}")

    if not any_rate_limit:
        print("No rate limits or cooldowns recorded in database.")
    print("=========================================================\n")


def cmd_health(args):
    """Checks the health and connectivity of internal components."""
    print("\n=================== IMM Health Check ===================")
    try:
        db = Database()
        print("[OK] Database connection: Healthy")
    except Exception as e:
        print(f"[FAIL] Database connection: Error - {e}")

    session_file_exists = os.path.exists("data/session.json")
    session_env = os.getenv("INSTAGRAM_SESSION_ID")
    if session_file_exists or session_env:
        print("[OK] Session configuration: Healthy")
    else:
        print("[WARNING] Session configuration: Neither session.json nor INSTAGRAM_SESSION_ID found.")
    print("========================================================\n")


def cmd_discover(args):
    """Executes target reel discovery pipeline stage."""
    load_dotenv()
    target = args.target
    limit = args.limit

    if not target:
        print("Error: Target username is required (-t / --target)")
        sys.exit(1)

    print(f"\n[INFO] Starting discovery pipeline for @{target} (Limit: {limit})...")
    pipeline = PipelineManager()
    result = pipeline.run_discovery(target_username=target, limit=limit)

    print("\n=================== Discovery Summary ===================")
    print(f"Target Username : @{target}")
    print(f"Pipeline Status : {result['status'].upper()}")

    if result["status"] == "rate_limited":
        print("Execution Result: Stopped due to active Rate Limit Cooldown (HTTP 429 safety).")
    elif result["status"] == "success":
        details = result.get("details", {})
        print(f"Discovered Reels: {details.get('discovered_count', 0)}")
        print(f"Unique New Reels Saved: {details.get('new_count', 0)}")
    else:
        print(f"Execution Error : {result.get('message', 'Unknown failure')}")
    print("========================================================\n")


def main():
    parser = argparse.ArgumentParser(description="IMM - Instagram Management and Monitoring Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available CLI commands")

    # Command: init
    subparsers.add_parser("init", help="Initialize database and directory structures")

    # Command: status
    subparsers.add_parser("status", help="Show system status and rate limit cooldowns")

    # Command: health
    subparsers.add_parser("health", help="Check health status of internal components")

    # Command: discover
    discover_parser = subparsers.add_parser("discover", help="Discover target user reels")
    discover_parser.add_argument("-t", "--target", type=str, required=True, help="Target Instagram username")
    discover_parser.add_argument("-l", "--limit", type=int, default=10, help="Maximum reels to discover (default: 10)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "discover":
        cmd_discover(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
        
