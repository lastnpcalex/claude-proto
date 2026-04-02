#!/usr/bin/env python3
"""Bluesky public API CLI — no login required.

Wraps the public ATProto XRPC endpoints so CC skills can just call:
    python bsky_cli.py feed lastnpcalex.agency
    python bsky_cli.py profile bsky.app
    python bsky_cli.py post at://did:plc:abc/app.bsky.feed.post/xyz
    python bsky_cli.py thread at://did:plc:abc/app.bsky.feed.post/xyz
    python bsky_cli.py resolve bsky.app
    python bsky_cli.py search "atproto developers" 15
"""

import io
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE = "https://public.api.bsky.app/xrpc"


def _get(endpoint: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    url = f"{BASE}/{endpoint}?{qs}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "bsky-cli/1.0 (Loom; +https://github.com/lastnpcalex/a-shadow-loom)",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
            msg = err.get("message", body)
        except json.JSONDecodeError:
            msg = body[:200]
        if e.code == 403:
            print(f"Error 403: Access denied for {endpoint}. This endpoint may require authentication.", file=sys.stderr)
        else:
            print(f"Error {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)


def _ts(iso: str) -> str:
    """Format ISO timestamp to readable short form."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d %H:%M")
    except Exception:
        return iso[:16]


# ── Commands ──────────────────────────────────────────────────────────────

def cmd_feed(actor: str, limit: int = 25):
    data = _get("app.bsky.feed.getAuthorFeed", {"actor": actor, "limit": min(limit, 100)})
    posts = data.get("feed", [])
    if not posts:
        print(f"No posts found for {actor}")
        return
    print(f"Recent posts from {actor} ({len(posts)} shown):\n")
    for i, item in enumerate(posts, 1):
        # Skip reposts
        if item.get("reason", {}).get("$type", "") == "app.bsky.feed.defs#reasonRepost":
            continue
        p = item["post"]
        rec = p.get("record", {})
        text = rec.get("text", "").replace("\n", " ")[:200]
        ts = _ts(rec.get("createdAt", ""))
        likes = p.get("likeCount", 0)
        reposts = p.get("repostCount", 0)
        replies = p.get("replyCount", 0)
        uri = p.get("uri", "")
        print(f"{i}. [{ts}] {text}")
        print(f"   ♥ {likes}  ♻ {reposts}  💬 {replies}")
        print(f"   {uri}")
        print()


def cmd_profile(actor: str):
    data = _get("app.bsky.actor.getProfile", {"actor": actor})
    name = data.get("displayName", "(none)")
    handle = data.get("handle", "?")
    did = data.get("did", "?")
    bio = data.get("description", "").replace("\n", " ")[:300]
    followers = data.get("followersCount", 0)
    following = data.get("followsCount", 0)
    posts = data.get("postsCount", 0)
    labels = [l.get("val", "") for l in data.get("labels", [])]

    print(f"Profile: {name} (@{handle})")
    print(f"DID: {did}")
    if bio:
        print(f"Bio: {bio}")
    print(f"Posts: {posts}  Followers: {followers}  Following: {following}")
    if labels:
        print(f"Labels: {', '.join(labels)}")


def _at_uri_to_url(at_uri: str, handle: str = "") -> str:
    """Convert at:// URI to a bsky.app web URL."""
    # at://did:plc:xxx/app.bsky.feed.post/rkey → https://bsky.app/profile/handle/post/rkey
    parts = at_uri.replace("at://", "").split("/")
    if len(parts) >= 3 and parts[1] == "app.bsky.feed.post":
        actor = handle or parts[0]
        return f"https://bsky.app/profile/{actor}/post/{parts[2]}"
    return ""


def _url_to_at_uri(url: str) -> str:
    """Convert a bsky.app URL to an at:// URI. Resolves handle to DID if needed."""
    # https://bsky.app/profile/handle/post/rkey → at://did:plc:xxx/app.bsky.feed.post/rkey
    import re
    m = re.match(r'https?://bsky\.app/profile/([^/]+)/post/([^/?#]+)', url)
    if not m:
        return url  # Not a bsky URL, return as-is (might already be at://)
    actor, rkey = m.group(1), m.group(2)
    # If actor is already a DID, use it directly
    if actor.startswith("did:"):
        return f"at://{actor}/app.bsky.feed.post/{rkey}"
    # Resolve handle to DID
    data = _get("com.atproto.identity.resolveHandle", {"handle": actor})
    did = data.get("did", actor)
    return f"at://{did}/app.bsky.feed.post/{rkey}"


def _ensure_at_uri(value: str) -> str:
    """Accept either an at:// URI or a bsky.app URL, always return at:// URI."""
    if value.startswith("at://"):
        return value
    if "bsky.app" in value:
        return _url_to_at_uri(value)
    return value  # Assume it's an at:// URI missing the prefix


def cmd_post(at_uri: str):
    at_uri = _ensure_at_uri(at_uri)
    data = _get("app.bsky.feed.getPosts", {"uris": at_uri})
    posts = data.get("posts", [])
    if not posts:
        print(f"Post not found: {at_uri}")
        return
    p = posts[0]
    author = p.get("author", {})
    rec = p.get("record", {})
    handle = author.get("handle", "?")

    print(f"@{handle} ({author.get('displayName', '')})")
    print(f"  {_ts(rec.get('createdAt', ''))}")
    print()
    print(rec.get("text", "(no text)"))
    print()
    print(f"♥ {p.get('likeCount', 0)}  ♻ {p.get('repostCount', 0)}  💬 {p.get('replyCount', 0)}  📑 {p.get('quoteCount', 0)}")

    # URIs and URLs
    uri = p.get("uri", "")
    print(f"\nURI: {uri}")
    web_url = _at_uri_to_url(uri, handle)
    if web_url:
        print(f"URL: {web_url}")

    # Thread position
    reply = rec.get("reply", {})
    if reply:
        parent_uri = reply.get("parent", {}).get("uri", "")
        root_uri = reply.get("root", {}).get("uri", "")
        if parent_uri:
            print(f"\nParent URI: {parent_uri}")
            parent_url = _at_uri_to_url(parent_uri)
            if parent_url:
                print(f"Parent URL: {parent_url}")
        if root_uri and root_uri != parent_uri:
            print(f"Root URI:   {root_uri}")
            root_url = _at_uri_to_url(root_uri)
            if root_url:
                print(f"Root URL:   {root_url}")
        print("(This post is a reply in a thread — use /bsky-get-thread on the root URI to see full context)")
    else:
        print("\n(Top-level post — not a reply)")

    # Embeds
    embed = p.get("embed", {})
    etype = embed.get("$type", "")
    if "images" in etype:
        for img in embed.get("images", []):
            print(f"  [Image] {img.get('alt', '(no alt)')}: {img.get('fullsize', '')}")
    if "external" in etype:
        ext = embed.get("external", {})
        print(f"  [Link] {ext.get('title', '')}: {ext.get('uri', '')}")
    if "record" in etype:
        qr = embed.get("record", {})
        if isinstance(qr, dict) and qr.get("uri"):
            print(f"  [Quote] {qr.get('uri', '')}")


def cmd_thread(at_uri: str, depth: int = 6):
    at_uri = _ensure_at_uri(at_uri)
    data = _get("app.bsky.feed.getPostThread", {"uri": at_uri, "depth": min(depth, 20)})
    thread = data.get("thread", {})
    if not thread or thread.get("$type") == "app.bsky.feed.defs#notFoundPost":
        print(f"Thread not found: {at_uri}")
        return

    def print_node(node, indent=0):
        if node.get("$type") == "app.bsky.feed.defs#blockedPost":
            print(f"{'  ' * indent}[blocked]")
            return
        p = node.get("post", {})
        if not p:
            return
        author = p.get("author", {})
        rec = p.get("record", {})
        text = rec.get("text", "").replace("\n", " ")[:200]
        handle = author.get("handle", "?")
        ts = _ts(rec.get("createdAt", ""))
        likes = p.get("likeCount", 0)
        replies = p.get("replyCount", 0)
        uri = p.get("uri", "")
        web_url = _at_uri_to_url(uri, handle)
        prefix = "  " * indent
        print(f"{prefix}@{handle} [{ts}] (♥ {likes}  💬 {replies})")
        print(f"{prefix}  {text}")
        print(f"{prefix}  {uri}")
        if web_url:
            print(f"{prefix}  {web_url}")
        print()
        for reply in node.get("replies", []):
            print_node(reply, indent + 1)

    # Print parent chain if available
    parent = thread.get("parent")
    parents = []
    while parent and parent.get("post"):
        parents.append(parent)
        parent = parent.get("parent")
    if parents:
        print("─── Parent chain ───")
        for p in reversed(parents):
            print_node(p)
        print("─── This post ───")

    print_node(thread)


def cmd_replies(at_uri: str, depth: int = 10):
    at_uri = _ensure_at_uri(at_uri)
    data = _get("app.bsky.feed.getPostThread", {"uri": at_uri, "depth": min(depth, 20)})
    thread = data.get("thread", {})
    if not thread or thread.get("$type") == "app.bsky.feed.defs#notFoundPost":
        print(f"Post not found: {at_uri}")
        return

    # Show the original post briefly
    root_post = thread.get("post", {})
    root_author = root_post.get("author", {})
    root_rec = root_post.get("record", {})
    root_handle = root_author.get("handle", "?")
    print(f"Replies to @{root_handle}: {root_rec.get('text', '')[:100]}")
    print(f"  {at_uri}")
    root_url = _at_uri_to_url(at_uri, root_handle)
    if root_url:
        print(f"  {root_url}")
    print()

    # Flatten all replies
    all_replies = []

    def collect(node, depth_level=0):
        for reply in node.get("replies", []):
            if reply.get("$type") == "app.bsky.feed.defs#blockedPost":
                continue
            p = reply.get("post", {})
            if p:
                all_replies.append((p, depth_level))
            collect(reply, depth_level + 1)

    collect(thread)

    if not all_replies:
        print("No replies.")
        return

    print(f"{len(all_replies)} replies:\n")
    for i, (p, level) in enumerate(all_replies, 1):
        author = p.get("author", {})
        rec = p.get("record", {})
        handle = author.get("handle", "?")
        text = rec.get("text", "").replace("\n", " ")[:200]
        ts = _ts(rec.get("createdAt", ""))
        likes = p.get("likeCount", 0)
        reply_count = p.get("replyCount", 0)
        uri = p.get("uri", "")
        web_url = _at_uri_to_url(uri, handle)
        indent = "  " * level
        print(f"{indent}{i}. @{handle} [{ts}] (♥ {likes}  💬 {reply_count})")
        print(f"{indent}   {text}")
        print(f"{indent}   {uri}")
        if web_url:
            print(f"{indent}   {web_url}")
        print()


def cmd_uri2url(at_uri: str):
    at_uri = _ensure_at_uri(at_uri)
    url = _at_uri_to_url(at_uri)
    if url:
        print(f"{at_uri}")
        print(f"→ {url}")
    else:
        print(f"Cannot convert to URL: {at_uri}")
        print("(Only app.bsky.feed.post URIs are supported)")


def cmd_url2uri(url: str):
    if not "bsky.app" in url:
        print(f"Not a bsky.app URL: {url}")
        return
    uri = _url_to_at_uri(url)
    print(f"{url}")
    print(f"→ {uri}")


def cmd_resolve(handle: str):
    data = _get("com.atproto.identity.resolveHandle", {"handle": handle})
    did = data.get("did", "?")
    print(f"{handle} → {did}")
    print(f"\nUse this DID with other /bsky-* commands as the actor parameter.")


def cmd_search(query: str, limit: int = 20):
    data = _get("app.bsky.feed.searchPosts", {"q": query, "limit": min(limit, 100)})
    posts = data.get("posts", [])
    total = data.get("hitsTotal", len(posts))
    if not posts:
        print(f"No results for '{query}'. Try different keywords.")
        return
    print(f"Search: '{query}' — {total} total hits, showing {len(posts)}:\n")
    for i, p in enumerate(posts, 1):
        author = p.get("author", {})
        rec = p.get("record", {})
        text = rec.get("text", "").replace("\n", " ")[:200]
        ts = _ts(rec.get("createdAt", ""))
        likes = p.get("likeCount", 0)
        uri = p.get("uri", "")
        print(f"{i}. @{author.get('handle', '?')} [{ts}] (♥ {likes})")
        print(f"   {text}")
        print(f"   {uri}")
        print()


# ── CLI dispatch ──────────────────────────────────────────────────────────

COMMANDS = {
    "feed": (cmd_feed, "feed <handle> [limit]"),
    "profile": (cmd_profile, "profile <handle-or-DID>"),
    "post": (cmd_post, "post <at-uri-or-url>"),
    "thread": (cmd_thread, "thread <at-uri-or-url> [depth]"),
    "replies": (cmd_replies, "replies <at-uri-or-url> [depth]"),
    "resolve": (cmd_resolve, "resolve <handle>"),
    "uri2url": (cmd_uri2url, "uri2url <at-uri>"),
    "url2uri": (cmd_url2uri, "url2uri <bsky-url>"),
    "search": (cmd_search, 'search "<query>" [limit]'),
}


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
        print("Usage: python bsky_cli.py <command> <args>")
        print("\nCommands:")
        for name, (_, usage) in COMMANDS.items():
            print(f"  {usage}")
        sys.exit(1)

    cmd_name = sys.argv[1]
    func, _ = COMMANDS[cmd_name]
    args = sys.argv[2:]

    if cmd_name in ("feed", "search", "thread", "replies"):
        # First arg is required, second is optional int
        main_arg = args[0]
        extra = int(args[1]) if len(args) > 1 else None
        if extra is not None:
            func(main_arg, extra)
        else:
            func(main_arg)
    else:
        func(args[0])


if __name__ == "__main__":
    main()
