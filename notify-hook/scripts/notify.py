#!/usr/bin/env python3
import json
import sys
import subprocess
from datetime import datetime

def main():
    try:
        # Read JSON from stdin
        data = json.load(sys.stdin)
        
        # Extract message and title from JSON
        message = data.get('message', 'Claude Code needs your attention')
        title = data.get('title', 'Claude Code')
        
        # Create timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        # Get repo owner and name from git remote
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                               capture_output=True, text=True, check=True)
        remote_url = result.stdout.strip()
        
        # Extract owner and repo name from URL
        if remote_url.startswith('https://github.com/'):
            parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            owner, repo = parts[0], parts[1]
        elif remote_url.startswith('git@github.com:'):
            parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
            owner, repo = parts[0], parts[1]
        else:
            # Fallback if not a GitHub URL
            owner, repo = 'unknown', 'unknown'
        
        topic = f"claude-{owner}-{repo}"
        curl_cmd = [
            'curl', '-s',
            '-d', full_message,
            '-H', f'Title: {title}',
            '-H', 'Priority: default',
            '-H', 'Tags: computer,claude',
            f'https://ntfy.sh/{topic}'
        ]
        
        subprocess.run(curl_cmd, stdout=subprocess.DEVNULL, check=True)
        print(f"Notification sent: {full_message}")
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Failed to send notification", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()