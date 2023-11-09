"""Main entry point."""
import asyncio

from clc import cli

def main() -> None:
    """Enter the application."""
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()