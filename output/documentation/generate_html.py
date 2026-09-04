from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).parents[2]
OUTPUT = Path(__file__).with_name("index.html")

DOCUMENTS = [
    ROOT / "01-steckbrief.md",
    ROOT / "02-meilensteine.md",
    ROOT / "03-offene-fragen.md",
    ROOT / "04-decisions.md",
    ROOT / "06-logbuch.md",
    ROOT / "07-anforderungsliste.md",
    ROOT / "08-aufgaben-texte.md",
    ROOT / "output" / "source-code" / "README.md",
    ROOT / "output" / "documentation" / "graph.md",
    ROOT / "output" / "documentation" / "agents.md",
]


def slug(text):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return value or "section"


def inline(text):
    text = escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def render_markdown(source):
    lines = source.splitlines()
    html = []
    headings = []
    index = 0
    in_code = False
    code_lines = []
    list_type = None
    table_rows = []

    def close_list():
        nonlocal list_type
        if list_type:
            html.append(f"</{list_type}>")
            list_type = None

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        html.append("<table>")
        for row_index, row in enumerate(table_rows):
            tag = "th" if row_index == 0 else "td"
            html.append("<tr>" + "".join(f"<{tag}>{inline(cell.strip())}</{tag}>" for cell in row) + "</tr>")
        html.append("</table>")
        table_rows = []

    for line in lines:
        if line.startswith("```"):
            close_list()
            flush_table()
            if in_code:
                html.append("<pre><code>" + escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", line)
        if heading:
            close_list()
            flush_table()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = f"section-{index}-{slug(title)}"
            index += 1
            headings.append((level, title, anchor))
            html.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            continue

        if re.match(r"^\s*[-*]\s+", line):
            flush_table()
            if list_type != "ul":
                close_list()
                html.append("<ul>")
                list_type = "ul"
            item = re.sub(r"^\s*[-*]\s+", "", line)
            item = re.sub(r"^\[[ xX]\]\s*", "", item)
            html.append(f"<li>{inline(item)}</li>")
            continue

        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if ordered:
            flush_table()
            if list_type != "ol":
                close_list()
                html.append("<ol>")
                list_type = "ol"
            html.append(f"<li>{inline(ordered.group(1))}</li>")
            continue

        if "|" in line and line.strip().startswith("|"):
            close_list()
            cells = [cell for cell in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells):
                table_rows.append(cells)
            continue

        close_list()
        flush_table()
        if not line.strip():
            continue
        if line.startswith("> "):
            html.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        else:
            html.append(f"<p>{inline(line)}</p>")

    close_list()
    flush_table()
    return "\n".join(html), headings


def build():
    content = []
    all_headings = []
    for document in DOCUMENTS:
        if not document.exists():
            continue
        rendered, headings = render_markdown(document.read_text(encoding="utf-8"))
        title = document.relative_to(ROOT).as_posix()
        content.append(f'<section class="document"><p class="source">Quelle: {escape(title)}</p>{rendered}</section>')
        all_headings.extend(headings)

    toc = []
    for level, title, anchor in all_headings:
        toc.append(f'<li class="level-{level}"><a href="#{anchor}">{inline(title)}</a></li>')

    page = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Agent Delivery Simulator Dokumentation</title>
  <style>
    :root { color-scheme: light; --ink: #17212b; --muted: #5d6b78; --line: #d8e0e6; --accent: #176b87; --paper: #ffffff; --wash: #eef4f6; }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: var(--wash); font: 16px/1.6 Georgia, serif; }
    main { max-width: 1180px; margin: 0 auto; padding: 40px 24px 80px; }
    header { padding: 42px 0 30px; border-bottom: 3px solid var(--accent); }
    h1, h2, h3, h4, h5, h6 { font-family: "Trebuchet MS", sans-serif; line-height: 1.2; }
    h1 { font-size: 2.4rem; margin: 0 0 8px; }
    h2 { margin-top: 2.4rem; color: var(--accent); }
    h3 { margin-top: 1.8rem; }
    .subtitle, .source { color: var(--muted); }
    .layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 32px; align-items: start; }
    nav { position: sticky; top: 20px; background: var(--paper); border: 1px solid var(--line); padding: 20px; max-height: calc(100vh - 40px); overflow: auto; }
    nav h2 { font-size: 1.1rem; margin: 0 0 12px; color: var(--ink); }
    nav ol { margin: 0; padding-left: 18px; }
    nav li { margin: 5px 0; font-size: .92rem; }
    nav .level-1 { font-weight: 700; margin-top: 12px; }
    nav .level-2 { margin-left: 8px; }
    nav .level-3, nav .level-4 { margin-left: 16px; font-size: .86rem; }
    a { color: var(--accent); }
    article { min-width: 0; }
    .document { background: var(--paper); border: 1px solid var(--line); padding: 28px 34px; margin-bottom: 24px; }
    .source { border-bottom: 1px solid var(--line); padding-bottom: 10px; font: .82rem/1.4 Consolas, monospace; }
    code { background: #edf1f3; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; font-size: .9em; }
    pre { overflow-x: auto; background: #18242c; color: #eef5f7; padding: 16px; border-radius: 4px; }
    pre code { background: none; padding: 0; }
    table { width: 100%; border-collapse: collapse; margin: 18px 0; }
    th, td { border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }
    th { background: #e5eff2; font-family: "Trebuchet MS", sans-serif; }
    blockquote { border-left: 4px solid var(--accent); margin: 18px 0; padding: 8px 18px; color: var(--muted); }
    @media (max-width: 800px) { main { padding: 20px 12px 50px; } .layout { display: block; } nav { position: static; margin-bottom: 20px; max-height: none; } .document { padding: 20px; } h1 { font-size: 1.9rem; } }
  </style>
</head>
<body>
<main>
  <header><h1>Multi-Agent Delivery Simulator</h1><p class="subtitle">Gesamtdokumentation aus den Projekt-Markdown-Dateien</p></header>
  <div class="layout">
    <nav><h2>Inhaltsverzeichnis</h2><ol>__TOC__</ol></nav>
    <article>__CONTENT__</article>
  </div>
</main>
</body>
</html>
"""
    OUTPUT.write_text(page.replace("__TOC__", "\n".join(toc)).replace("__CONTENT__", "\n".join(content)), encoding="utf-8")


if __name__ == "__main__":
    build()