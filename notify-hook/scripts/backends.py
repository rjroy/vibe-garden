#!/usr/bin/env python3
"""
Notification backend dispatchers for notify-hook plugin.
Supports ntfy.sh, Discord, and Slack.
Stdlib only - no external dependencies.
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Dict, Any


def send_ntfy(message: str, config: Dict[str, Any], topic: str) -> bool:
    """
    Send notification to ntfy.sh.

    Args:
        message: Message to send
        config: Backend configuration
        topic: ntfy.sh topic name

    Returns:
        True if successful, False otherwise
    """
    ntfy_config = config.get("ntfy", {})

    if not ntfy_config.get("enabled", True):
        return False

    # Build request
    url = f"https://ntfy.sh/{topic}"
    headers = {
        "Title": "Claude Code",
        "Priority": ntfy_config.get("priority", "default"),
        "Tags": ",".join(ntfy_config.get("tags", ["computer", "claude"]))
    }

    try:
        # Create request
        req = urllib.request.Request(
            url,
            data=message.encode('utf-8'),
            headers=headers,
            method='POST'
        )

        # Send with timeout
        timeout = ntfy_config.get("timeout", 5)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                print(f"✓ Sent to ntfy.sh: {topic}", file=sys.stderr)
                return True
            else:
                print(f"✗ ntfy.sh error: HTTP {response.status}", file=sys.stderr)
                return False

    except urllib.error.URLError as e:
        print(f"✗ ntfy.sh failed: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ ntfy.sh error: {e}", file=sys.stderr)
        return False


def send_discord(message: str, config: Dict[str, Any]) -> bool:
    """
    Send notification to Discord webhook.

    Args:
        message: Message to send
        config: Backend configuration

    Returns:
        True if successful, False otherwise
    """
    discord_config = config.get("discord", {})

    if not discord_config.get("enabled", False):
        return False

    webhook_url = discord_config.get("webhook_url", "")

    # Validate webhook URL
    if not webhook_url or not webhook_url.startswith("https://"):
        print("✗ Discord: Invalid or missing webhook URL", file=sys.stderr)
        return False

    # Build payload
    payload = {"content": message}

    try:
        # Create request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method='POST'
        )

        # Send with timeout
        timeout = discord_config.get("timeout", 5)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status in (200, 204):
                print("✓ Sent to Discord", file=sys.stderr)
                return True
            else:
                print(f"✗ Discord error: HTTP {response.status}", file=sys.stderr)
                return False

    except urllib.error.URLError as e:
        print(f"✗ Discord failed: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Discord error: {e}", file=sys.stderr)
        return False


def send_slack(message: str, config: Dict[str, Any]) -> bool:
    """
    Send notification to Slack webhook.

    Args:
        message: Message to send
        config: Backend configuration

    Returns:
        True if successful, False otherwise
    """
    slack_config = config.get("slack", {})

    if not slack_config.get("enabled", False):
        return False

    webhook_url = slack_config.get("webhook_url", "")

    # Validate webhook URL
    if not webhook_url or not webhook_url.startswith("https://"):
        print("✗ Slack: Invalid or missing webhook URL", file=sys.stderr)
        return False

    # Build payload
    payload = {"text": message}

    try:
        # Create request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method='POST'
        )

        # Send with timeout
        timeout = slack_config.get("timeout", 5)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                print("✓ Sent to Slack", file=sys.stderr)
                return True
            else:
                print(f"✗ Slack error: HTTP {response.status}", file=sys.stderr)
                return False

    except urllib.error.URLError as e:
        print(f"✗ Slack failed: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Slack error: {e}", file=sys.stderr)
        return False


def dispatch_all(message: str, backends_config: Dict[str, Any], topic: str = None) -> Dict[str, bool]:
    """
    Dispatch notification to all enabled backends.

    Errors are isolated - one backend failure doesn't prevent others from sending.

    Args:
        message: Message to send
        backends_config: Backends configuration dict
        topic: ntfy.sh topic (optional, uses config default if not provided)

    Returns:
        Dict mapping backend name to success status
    """
    results = {}

    # Send to ntfy.sh
    if topic:
        results["ntfy"] = send_ntfy(message, backends_config, topic)

    # Send to Discord
    results["discord"] = send_discord(message, backends_config)

    # Send to Slack
    results["slack"] = send_slack(message, backends_config)

    return results
