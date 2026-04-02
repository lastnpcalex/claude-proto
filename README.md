# claude-proto

Skills for [Claude Code](https://code.claude.com) — slash commands that extend CC with new capabilities.

## Skills

### [ooda/](ooda/) — Structured reasoning

Forces Boyd's OODA loop (Observe-Orient-Decide-Act) before any code changes. Particularly useful for debugging, where jumping to fixes without understanding the problem creates compounding bugs.

| Skill | Description |
|-------|-------------|
| `/ooda` | Work through OODA loop on any task before writing code |

```
/ooda the admin server restart doesn't work
/ooda this function is returning null when it shouldn't
```

### [bsky/](bsky/) — Bluesky

Browse posts, profiles, threads, and replies using the public Bluesky ATProto XRPC endpoints. No login required.

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
# Copy skills into your Claude Code commands directory
cp ooda/ooda.md ~/.claude/commands/
cp bsky/bsky_cli.py bsky/bsky-*.md ~/.claude/commands/
```

For bsky skills, update the path in each `.md` file to point to wherever you put `bsky_cli.py`.

## Dependencies

- **ooda**: None (prompt-only skill)
- **bsky**: Python 3.10+ standard library only (`urllib`, `json`, `re`)

## License

MIT
