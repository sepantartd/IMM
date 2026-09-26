"""
Main entry point for IMM (Instagram Modular Manager).
Handles top-level execution and routes CLI commands smoothly.
"""

import sys
from app.cli.interface import cli


def main():
    """Executes IMM CLI interface with global exception protection."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\n[IMM] Operation cancelled by user. Exiting cleanly...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[IMM Critical Error] An unhandled exception occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
