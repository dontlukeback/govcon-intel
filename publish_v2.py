#!/usr/bin/env python3
"""
Substack Publisher v2 — Premium formatting via ProseMirror JSON.

Builds Substack posts with proper bold, bullet lists, ordered lists,
blockquotes, section dividers, and heading hierarchy by constructing
the exact ProseMirror JSON schema Substack's editor uses.

Usage:
    # Preview: generate HTML file to inspect formatting locally
    python3 publish_v2.py --file output/substack-post-1.md --preview

    # Create draft on Substack (requires auth)
    python3 publish_v2.py --file output/substack-post-1.md \
        --title "GovCon Weekly Intelligence: March 18, 2026" \
        --subtitle "1,173 awards tracked | $8.7B total value | 9 IT verticals" \
        --draft

    # Publish immediately
    python3 publish_v2.py --file output/substack-post-1.md \
        --title "GovCon Weekly Intelligence: March 18, 2026" \
        --draft  # always use --draft first, review, then publish from dashboard

    # Login first time
    python3 publish_v2.py --login

    # With cookie auth
    python3 publish_v2.py --file output/substack-post-1.md --title "Title" --cookie YOUR_SID --draft
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLICATION_URL = "https://govconintelligence.substack.com"


# ---------------------------------------------------------------------------
# ProseMirror JSON Builder — the core of v2
# ---------------------------------------------------------------------------

def parse_inline_marks(text: str) -> List[Dict]:
    """
    Parse inline markdown (bold, italic, links) into ProseMirror text nodes
    with proper marks. This replaces the buggy library version.
    """
    if not text or not text.strip():
        return []

    tokens = []
    # Patterns ordered by priority: links > bold > italic
    link_pat = r'\[([^\]]+)\]\(([^)]+)\)'
    bold_pat = r'\*\*(.+?)\*\*'
    italic_pat = r'(?<!\*)\*([^*]+)\*(?!\*)'

    matches = []
    for m in re.finditer(link_pat, text):
        matches.append((m.start(), m.end(), "link", m.group(1), m.group(2)))
    for m in re.finditer(bold_pat, text):
        if not any(s <= m.start() < e for s, e, *_ in matches):
            matches.append((m.start(), m.end(), "strong", m.group(1), None))
    for m in re.finditer(italic_pat, text):
        if not any(s <= m.start() < e for s, e, *_ in matches):
            matches.append((m.start(), m.end(), "em", m.group(1), None))

    matches.sort(key=lambda x: x[0])

    last = 0
    for start, end, mtype, content, url in matches:
        if start > last:
            tokens.append({"type": "text", "text": text[last:start]})
        node = {"type": "text", "text": content}
        if mtype == "link":
            node["marks"] = [{"type": "link", "attrs": {"href": url}}]
        elif mtype == "strong":
            node["marks"] = [{"type": "strong"}]
        elif mtype == "em":
            node["marks"] = [{"type": "em"}]
        tokens.append(node)
        last = end

    if last < len(text):
        tokens.append({"type": "text", "text": text[last:]})

    return [t for t in tokens if t.get("text")]


def make_paragraph(text: str) -> Dict:
    """Create a paragraph node with inline formatting."""
    content = parse_inline_marks(text)
    node = {"type": "paragraph"}
    if content:
        node["content"] = content
    return node


def make_heading(text: str, level: int) -> Dict:
    """Create a heading node."""
    # Strip any markdown bold from headings (common pattern)
    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": clean}]
    }


def make_horizontal_rule() -> Dict:
    return {"type": "horizontal_rule"}


def make_blockquote(lines: List[str]) -> Dict:
    """Create a blockquote node from one or more lines."""
    paragraphs = []
    current = []
    for line in lines:
        if line.strip():
            current.append(line)
        else:
            if current:
                paragraphs.append(make_paragraph(" ".join(current)))
                current = []
    if current:
        paragraphs.append(make_paragraph(" ".join(current)))
    return {"type": "blockquote", "content": paragraphs}


def make_bullet_list(items: List[str]) -> Dict:
    """Create a bullet_list node with proper list_item children."""
    list_items = []
    for item_text in items:
        content = parse_inline_marks(item_text)
        para = {"type": "paragraph"}
        if content:
            para["content"] = content
        list_items.append({
            "type": "list_item",
            "content": [para]
        })
    return {"type": "bullet_list", "content": list_items}


def make_ordered_list(items: List[str]) -> Dict:
    """Create an ordered_list node with proper list_item children."""
    list_items = []
    for item_text in items:
        content = parse_inline_marks(item_text)
        para = {"type": "paragraph"}
        if content:
            para["content"] = content
        list_items.append({
            "type": "list_item",
            "content": [para]
        })
    return {"type": "ordered_list", "attrs": {"order": 1}, "content": list_items}


def make_table_as_text(table_lines: List[str]) -> List[Dict]:
    """
    Convert a markdown table into styled paragraphs.
    Substack doesn't support HTML tables. We render each row as a
    bold-header: value paragraph for readability.
    """
    nodes = []
    # Parse header row
    if not table_lines:
        return nodes

    headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]

    for line in table_lines[1:]:
        # Skip separator row
        if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not any(cells):
            continue
        # Build a readable line: "Rank 1 | General Dynamics IT | $1.2B | Won JADC2"
        parts = []
        for h, c in zip(headers, cells):
            if c:
                parts.append(f"{c}")
        # First cell bold, rest normal
        if len(cells) >= 2:
            text_parts = []
            text_parts.append({"type": "text", "text": cells[1] if len(cells) > 1 else cells[0],
                              "marks": [{"type": "strong"}]})
            rest = " — " + " | ".join(c for c in cells[2:] if c)
            if rest.strip() != "—":
                text_parts.append({"type": "text", "text": rest})
            nodes.append({
                "type": "paragraph",
                "content": text_parts
            })

    return nodes


# ---------------------------------------------------------------------------
# Markdown -> ProseMirror Document
# ---------------------------------------------------------------------------

def md_to_prosemirror(md_text: str) -> Dict:
    """
    Convert a full markdown document into a ProseMirror JSON document
    that Substack's API accepts natively.
    """
    doc_content = []
    lines = md_text.split("\n")
    i = 0

    def collect_paragraph_lines():
        """Collect contiguous non-special lines into a paragraph."""
        nonlocal i
        para_lines = []
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                break
            if stripped.startswith("#"):
                break
            if stripped in ("---", "***", "___"):
                break
            if stripped.startswith("- ") or stripped.startswith("* "):
                break
            if re.match(r'^\d+\.\s', stripped):
                break
            if stripped.startswith("> "):
                break
            if stripped.startswith("|"):
                break
            para_lines.append(stripped)
            i += 1
        return " ".join(para_lines)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # H1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            doc_content.append(make_heading(stripped[2:].strip(), 1))
            i += 1
            continue

        # H2
        if stripped.startswith("## ") and not stripped.startswith("### "):
            doc_content.append(make_heading(stripped[3:].strip(), 2))
            i += 1
            continue

        # H3
        if stripped.startswith("### ") and not stripped.startswith("#### "):
            doc_content.append(make_heading(stripped[4:].strip(), 3))
            i += 1
            continue

        # H4
        if stripped.startswith("#### "):
            doc_content.append(make_heading(stripped[5:].strip(), 4))
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            doc_content.append(make_horizontal_rule())
            i += 1
            continue

        # Blockquote (collect consecutive > lines)
        if stripped.startswith("> "):
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                bq_lines.append(lines[i].strip()[2:])
                i += 1
            doc_content.append(make_blockquote(bq_lines))
            continue

        # Bullet list (collect consecutive - or * items)
        if stripped.startswith("- ") or (stripped.startswith("* ") and not stripped.startswith("**")):
            items = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("- "):
                    items.append(s[2:])
                    i += 1
                elif s.startswith("* ") and not s.startswith("**"):
                    items.append(s[2:])
                    i += 1
                elif not s:
                    # Check if next non-empty line is also a bullet
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and (lines[j].strip().startswith("- ") or
                                           (lines[j].strip().startswith("* ") and not lines[j].strip().startswith("**"))):
                        i += 1  # skip blank line within list
                    else:
                        break
                else:
                    break
            doc_content.append(make_bullet_list(items))
            continue

        # Ordered list
        if re.match(r'^\d+\.\s', stripped):
            items = []
            while i < len(lines):
                s = lines[i].strip()
                m = re.match(r'^\d+\.\s+(.*)', s)
                if m:
                    items.append(m.group(1))
                    i += 1
                elif not s:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and re.match(r'^\d+\.\s', lines[j].strip()):
                        i += 1
                    else:
                        break
                else:
                    break
            doc_content.append(make_ordered_list(items))
            continue

        # Table
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            table_nodes = make_table_as_text(table_lines)
            if table_nodes:
                doc_content.extend(table_nodes)
            continue

        # Italic-only line (like *subtitle text*)
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            inner = stripped[1:-1]
            doc_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": inner, "marks": [{"type": "em"}]}]
            })
            i += 1
            continue

        # Regular paragraph
        para_text = collect_paragraph_lines()
        if para_text:
            doc_content.append(make_paragraph(para_text))

    return {"type": "doc", "content": doc_content}


# ---------------------------------------------------------------------------
# Executive Summary Extraction — make the lede a blockquote
# ---------------------------------------------------------------------------

def enhance_for_substack(doc: Dict) -> Dict:
    """
    Post-process the ProseMirror doc to add premium newsletter styling:
    - Convert the first substantial paragraph (after H1 + subtitle) into a blockquote
    - This makes the executive summary stand out
    """
    content = doc["content"]
    new_content = []
    found_first_hr = False
    found_second_hr = False
    lede_converted = False

    for i, node in enumerate(content):
        # After first HR and before second HR, wrap paragraphs in blockquote
        if node["type"] == "horizontal_rule":
            if not found_first_hr:
                found_first_hr = True
                new_content.append(node)
                continue
            elif not found_second_hr:
                found_second_hr = True

        # Convert the paragraph(s) between first and second HR into a blockquote
        if found_first_hr and not found_second_hr and node["type"] == "paragraph" and not lede_converted:
            # Collect all paragraphs until next HR
            bq_paragraphs = [node]
            j = i + 1
            while j < len(content) and content[j]["type"] == "paragraph":
                bq_paragraphs.append(content[j])
                j += 1
            new_content.append({"type": "blockquote", "content": bq_paragraphs})
            lede_converted = True
            # Skip the paragraphs we just consumed
            # We'll handle this by tracking what to skip
            continue

        # Skip paragraphs already consumed by blockquote
        if found_first_hr and not found_second_hr and node["type"] == "paragraph" and lede_converted:
            continue

        new_content.append(node)

    doc["content"] = new_content
    return doc


# ---------------------------------------------------------------------------
# HTML Preview Generator
# ---------------------------------------------------------------------------

PREVIEW_CSS = """
<style>
    body {
        font-family: 'Spectral', Georgia, serif;
        max-width: 680px;
        margin: 40px auto;
        padding: 0 20px;
        color: #1a1a1a;
        line-height: 1.7;
        background: #fff;
    }
    h1 { font-size: 2em; margin-bottom: 0.3em; letter-spacing: -0.02em; }
    h2 { font-size: 1.5em; margin-top: 2em; margin-bottom: 0.5em; border-bottom: 1px solid #e0e0e0; padding-bottom: 0.3em; }
    h3 { font-size: 1.2em; margin-top: 1.5em; color: #333; }
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 2em 0; }
    blockquote {
        border-left: 3px solid #1a8917;
        margin: 1.5em 0;
        padding: 0.8em 1.2em;
        background: #f7faf7;
        font-style: italic;
        color: #2d2d2d;
    }
    blockquote p { margin: 0.5em 0; }
    ul, ol { padding-left: 1.5em; }
    li { margin-bottom: 0.5em; }
    strong { font-weight: 700; }
    em { font-style: italic; }
    a { color: #1a8917; text-decoration: underline; }
    .subtitle { color: #666; font-size: 0.95em; margin-bottom: 2em; }
    .table-row { padding: 0.3em 0; border-bottom: 1px solid #f0f0f0; }
    .footer { color: #999; font-size: 0.85em; margin-top: 3em; border-top: 1px solid #e0e0e0; padding-top: 1em; }
    @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;700&display=swap');
</style>
"""


def prosemirror_to_html(doc: Dict) -> str:
    """Convert ProseMirror JSON to HTML for preview."""

    def render_text_node(node: Dict) -> str:
        text = node.get("text", "")
        # Escape HTML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        marks = node.get("marks", [])
        for mark in marks:
            mtype = mark["type"]
            if mtype == "strong":
                text = f"<strong>{text}</strong>"
            elif mtype == "em":
                text = f"<em>{text}</em>"
            elif mtype == "link":
                href = mark.get("attrs", {}).get("href", "#")
                text = f'<a href="{href}">{text}</a>'
        return text

    def render_content(nodes: List[Dict]) -> str:
        return "".join(render_text_node(n) for n in nodes if n.get("type") == "text")

    def render_node(node: Dict) -> str:
        ntype = node["type"]
        content = node.get("content", [])

        if ntype == "paragraph":
            inner = render_content(content)
            return f"<p>{inner}</p>\n" if inner else "<p></p>\n"

        elif ntype == "heading":
            level = node.get("attrs", {}).get("level", 2)
            inner = render_content(content)
            return f"<h{level}>{inner}</h{level}>\n"

        elif ntype == "horizontal_rule":
            return "<hr>\n"

        elif ntype == "blockquote":
            inner = "".join(render_node(c) for c in content)
            return f"<blockquote>{inner}</blockquote>\n"

        elif ntype == "bullet_list":
            items = "".join(
                f"<li>{render_content(li['content'][0].get('content', []))}</li>\n"
                for li in content if li["type"] == "list_item"
            )
            return f"<ul>\n{items}</ul>\n"

        elif ntype == "ordered_list":
            items = "".join(
                f"<li>{render_content(li['content'][0].get('content', []))}</li>\n"
                for li in content if li["type"] == "list_item"
            )
            return f"<ol>\n{items}</ol>\n"

        else:
            # Fallback: render content if present
            if content:
                return "".join(render_node(c) for c in content)
            return ""

    body = "".join(render_node(n) for n in doc.get("content", []))
    return body


def generate_preview(doc: Dict, title: str, subtitle: str, output_path: str):
    """Generate a local HTML preview file styled like Substack."""
    body_html = prosemirror_to_html(doc)
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    {PREVIEW_CSS}
</head>
<body>
    <h1>{title}</h1>
    {subtitle_html}
    {body_html}
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Preview saved: {output_path}")
    print(f"Open in browser: open {output_path}")


# ---------------------------------------------------------------------------
# Substack API Integration
# ---------------------------------------------------------------------------

def create_draft(api, title: str, subtitle: str, doc: Dict) -> str:
    """Create a Substack draft using raw ProseMirror JSON."""
    user_id = api.get_user_id()

    payload = {
        "draft_title": title,
        "draft_subtitle": subtitle or "",
        "draft_body": json.dumps(doc),
        "draft_bylines": [{"id": int(user_id), "is_guest": False}],
        "audience": "everyone",
        "draft_section_id": None,
        "section_chosen": True,
        "write_comment_permissions": "everyone",
    }

    response = api._session.post(f"{api.publication_url}/drafts", json=payload)
    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text[:500]}")
        sys.exit(1)

    draft = response.json()
    draft_id = draft.get("id")
    return draft_id


def authenticate(email: str, cookie: str = None):
    """Authenticate with Substack."""
    from substack import Api

    api = Api(
        email=email,
        password=None,
        publication_url=PUBLICATION_URL,
    )

    if cookie:
        api._session.cookies.set("substack.sid", cookie)

    return api


def login_flow(email: str):
    """Interactive login flow."""
    from substack import Api

    print(f"Logging in as {email}...")
    print("Substack will send a magic link to your email.")

    api = Api(email=email, password=None, publication_url=PUBLICATION_URL)
    try:
        user_id = api.get_user_id()
        print(f"Logged in. User ID: {user_id}")
        return api
    except Exception as e:
        print(f"Auto-login failed: {e}")
        print()
        print("Manual auth: log in via browser, then copy your substack.sid cookie.")
        print("  1. Open https://govconintelligence.substack.com in browser")
        print("  2. Log in normally")
        print("  3. DevTools > Application > Cookies > copy 'substack.sid' value")
        print("  4. Run: python3 publish_v2.py --cookie YOUR_COOKIE --title ... --file ...")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def extract_title_from_md(md_text: str) -> Tuple[str, str]:
    """Extract title and subtitle from markdown H1 and first italic line."""
    title = ""
    subtitle = ""
    for line in md_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped[2:].strip()
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            subtitle = stripped[1:-1].strip()
            break
    return title, subtitle


def main():
    parser = argparse.ArgumentParser(
        description="Substack Publisher v2 — Premium formatting via ProseMirror JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview locally (always do this first)
  python3 publish_v2.py --file output/substack-post-1.md --preview

  # Create draft on Substack
  python3 publish_v2.py --file output/substack-post-1.md \\
      --title "GovCon Weekly Intelligence" --draft --cookie YOUR_SID

  # Dump ProseMirror JSON (for debugging)
  python3 publish_v2.py --file output/substack-post-1.md --dump-json
        """
    )
    parser.add_argument("--login", action="store_true", help="Interactive login flow")
    parser.add_argument("--email", default="lukebaek@gmail.com")
    parser.add_argument("--cookie", help="substack.sid cookie value")
    parser.add_argument("--title", help="Post title (auto-detected from H1 if omitted)")
    parser.add_argument("--subtitle", help="Post subtitle (auto-detected from italic line if omitted)")
    parser.add_argument("--file", help="Markdown file to publish")
    parser.add_argument("--draft", action="store_true", help="Create draft only (recommended)")
    parser.add_argument("--preview", action="store_true", help="Generate local HTML preview")
    parser.add_argument("--preview-output", default=None, help="Preview output path (default: same dir as input)")
    parser.add_argument("--dump-json", action="store_true", help="Dump ProseMirror JSON to stdout")
    parser.add_argument("--image", action="append", help="Header image URL (use multiple times for inline images)")
    args = parser.parse_args()

    if args.login:
        login_flow(args.email)
        return

    if not args.file:
        parser.error("--file is required")

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    # Read and parse markdown
    with open(args.file) as f:
        md_text = f.read()

    # Auto-detect title/subtitle from markdown
    auto_title, auto_subtitle = extract_title_from_md(md_text)
    title = args.title or auto_title or "Untitled"
    subtitle = args.subtitle or auto_subtitle or ""

    # Convert to ProseMirror JSON
    doc = md_to_prosemirror(md_text)

    # Enhance: convert lede paragraph to blockquote
    doc = enhance_for_substack(doc)

    # Add header image if provided
    if args.image:
        for img_url in args.image:
            img_node = {
                "type": "captionedImage",
                "content": [{
                    "type": "image2",
                    "attrs": {
                        "src": img_url,
                        "fullscreen": False,
                        "imageSize": "full",
                        "height": None,
                        "width": None,
                        "resizeWidth": None,
                        "bytes": None,
                        "alt": None,
                        "title": None,
                        "type": None,
                        "href": None,
                        "belowTheFold": False,
                        "internalRedirect": None,
                    }
                }]
            }
            # Insert after first heading or at top
            insert_pos = 0
            for idx, node in enumerate(doc["content"]):
                if node["type"] == "heading":
                    insert_pos = idx + 1
                    break
            doc["content"].insert(insert_pos, img_node)

    # Dump JSON for debugging
    if args.dump_json:
        print(json.dumps(doc, indent=2))
        return

    # Preview mode
    if args.preview:
        base = os.path.splitext(args.file)[0]
        output_path = args.preview_output or f"{base}-preview.html"
        generate_preview(doc, title, subtitle, output_path)
        return

    # Publish mode — requires auth
    if not args.title and not auto_title:
        parser.error("--title is required when publishing (or include an H1 in your markdown)")

    try:
        from substack import Api
    except ImportError:
        print("Install dependency: pip3 install python-substack")
        sys.exit(1)

    api = authenticate(args.email, args.cookie)

    print(f"Creating draft: '{title}'")
    print(f"Subtitle: '{subtitle}'")
    print(f"Document: {len(doc['content'])} nodes")

    draft_id = create_draft(api, title, subtitle, doc)
    print(f"Draft created: ID {draft_id}")
    print(f"Review at: {PUBLICATION_URL}/publish/post/{draft_id}")

    if not args.draft:
        print()
        print("To publish, use --draft flag and review first.")
        print("Then publish from the Substack dashboard.")
    else:
        print()
        print("Draft saved. Review and publish from your Substack dashboard.")


if __name__ == "__main__":
    main()
