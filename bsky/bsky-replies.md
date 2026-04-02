Fetch all replies to a Bluesky post as a flat list (no login required).

Usage: /bsky-replies <at-uri-or-url> [depth]

Run this exact command, replacing URI_OR_URL and DEPTH from $ARGUMENTS (default depth 10):

    python "C:/Users/exast/.claude/commands/bsky_cli.py" replies URI_OR_URL DEPTH

Accepts either an at:// URI or a bsky.app URL. If $ARGUMENTS contains --verbose, display the full command output to the user exactly as returned — do not summarize or omit anything. Otherwise display a summary.