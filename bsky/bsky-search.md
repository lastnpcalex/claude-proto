Search Bluesky posts (no login required, may require auth on some instances).

Usage: /bsky-search <query> [limit]

Run this exact command, replacing QUERY and LIMIT from $ARGUMENTS (default limit 20):

    python "C:/Users/exast/.claude/commands/bsky_cli.py" search "QUERY" LIMIT

If $ARGUMENTS contains --verbose, display the full command output to the user exactly as returned — do not summarize or omit anything. Otherwise display a summary. If the command fails (403), note that the search endpoint may require authentication.