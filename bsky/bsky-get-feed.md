Fetch a Bluesky author's recent posts (no login required).

Usage: /bsky-get-feed <handle-or-DID> [limit]

Run this exact command, replacing ACTOR and LIMIT from $ARGUMENTS (default limit 25):

    python "C:/Users/exast/.claude/commands/bsky_cli.py" feed ACTOR LIMIT

If $ARGUMENTS contains --verbose, display the full command output to the user exactly as returned — do not summarize or omit anything. Otherwise display a summary.