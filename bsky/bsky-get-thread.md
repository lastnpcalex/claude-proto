Fetch a Bluesky post and its reply thread (no login required).

Usage: /bsky-get-thread <at-uri> [depth]

Run this exact command, replacing AT_URI and DEPTH from $ARGUMENTS (default depth 6):

    python "C:/Users/exast/.claude/commands/bsky_cli.py" thread AT_URI DEPTH

If $ARGUMENTS contains --verbose, display the full command output to the user exactly as returned — do not summarize or omit anything. Otherwise display a summary.