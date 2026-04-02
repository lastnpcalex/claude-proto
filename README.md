# claude-proto

ATProto skills and tools for [Claude Code](https://code.claude.com) — public API access to the AT Protocol ecosystem. No login required.

## Skills

### [bsky/](bsky/) — Bluesky

Browse posts, profiles, threads, and replies using the public Bluesky ATProto XRPC endpoints.

| Skill | Description |
|-------|-------------|
| `/bsky-get-feed` | Fetch an author's recent posts |
| `/bsky-get-post` | Fetch a single post with thread context, URIs, URLs |
| `/bsky-get-thread` | Fetch a post and its reply thread (indented tree) |
| `/bsky-replies` | Flat list of all replies to a post |
| `/bsky-profile` | Fetch an actor's profile (bio, followers, labels) |
| `/bsky-resolve` | Resolve a handle to its DID |
| `/bsky-search` | Search posts (may require auth) |
| `/bsky-uri2url` | Convert `at://` URI to `https://bsky.app` URL |
| `/bsky-url2uri` | Convert `https://bsky.app` URL to `at://` URI |

All post/thread/replies commands accept either an `at://` URI or a `bsky.app` URL. Use `--verbose` for full unabridged output.

## Install

```bash
# Copy bsky skills + CLI into your Claude Code commands directory
cp bsky/bsky_cli.py bsky/bsky-*.md ~/.claude/commands/
```

Then update the path in each `.md` file to point to wherever you put `bsky_cli.py`.

## Dependencies

Python 3.10+ standard library only (`urllib`, `json`, `re`). No pip packages needed.

## Usage

As Claude Code slash commands:
```
/bsky-get-feed lastnpcalex.agency
/bsky-get-post https://bsky.app/profile/handle/post/rkey
/bsky-replies at://did:plc:xxx/app.bsky.feed.post/rkey
/bsky-profile bsky.app --verbose
```

Or directly from the CLI:
```bash
python bsky_cli.py feed lastnpcalex.agency 10
python bsky_cli.py thread https://bsky.app/profile/handle/post/rkey 6
python bsky_cli.py url2uri https://bsky.app/profile/handle/post/rkey
```

## License

MIT
