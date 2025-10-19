"""Entry point for running Courier MCP server.

Usage:
    python -m courier_mcp
"""

import asyncio
import sys

from courier_mcp.logger import get_logger
from courier_mcp.server import main

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
