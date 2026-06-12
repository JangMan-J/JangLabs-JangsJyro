#!/usr/bin/env python3
"""Convert a saved Steam Community guide HTML page to Markdown.

Preserves the chapter index (table of contents) linked to chapter headings,
converts Steam bbcode-rendered markup (bb_h1/2/3, bb_ul, bb_table,
bb_blockquote, bb_link) to Markdown, and drops all image/media-only content.
"""
import re
import sys
from urllib.parse import unquote, urlparse, parse_qs

from bs4 import BeautifulSoup, NavigableString, Tag

SRC = '/home/jangmanj/Downloads/steam_g_3.html'
DST = '/home/jangmanj/Downloads/steam_g_3.md'

BLOCK_CLASSES = {
    'bb_h1': '###', 'bb_h2': '####', 'bb_h3': '#####',
}


def slugify(title):
    """GitHub-style heading anchor."""
    s = title.strip().lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s', '-', s)
    return s


def clean_href(href):
    if not href:
        return None
    if 'linkfilter' in href:
        q = parse_qs(urlparse(href).query)
        for key in ('u', 'url'):
            if key in q:
                return q[key][0]
        return unquote(href)
    return href


def is_media_anchor(a):
    """Anchor that exists only to show an image/video (no meaningful text)."""
    if a.find('img') is not None and not a.get_text(strip=True):
        return True
    classes = a.get('class') or []
    if 'modalContentLink' in classes and not a.get_text(strip=True):
        return True
    return False


def render_inline_node(child):
    """Render a single node (tag or string) as inline markdown."""
    if isinstance(child, NavigableString):
        return re.sub(r'\s+', ' ', str(child))
    if not isinstance(child, Tag):
        return ''
    name = child.name
    if name == 'br':
        return '\n'
    if name == 'img':
        return ''
    if name == 'a':
        if is_media_anchor(child):
            return ''
        text = inline_text(child).strip()
        href = clean_href(child.get('href'))
        if not text:
            return ''
        if href and not str(href).startswith(('javascript:', '#')):
            return f'[{text}]({href})'
        return text
    if name in ('b', 'strong'):
        text = inline_text(child).strip()
        return f'**{text}**' if text else ''
    if name in ('i', 'em'):
        # italic wrapper may contain block content (lists); recurse as blocks
        if child.find(['ul', 'ol', 'div', 'blockquote']):
            return render_blocks(child)
        text = inline_text(child).strip()
        return f'*{text}*' if text else ''
    if name in ('span', 'u', 'font'):
        return inline_text(child)
    if name in ('ul', 'ol', 'div', 'blockquote', 'table'):
        return '\n' + render_block_element(child).rstrip() + '\n'
    return inline_text(child)


def inline_text(node):
    """Render a node's contents as inline markdown (no block structure)."""
    return ''.join(render_inline_node(c) for c in node.children)


def render_list(node, depth=0, ordered=False):
    lines = []
    idx = 0
    for li in node.find_all('li', recursive=False):
        idx += 1
        # split nested lists out of the li
        nested = []
        for sub in li.find_all(['ul', 'ol'], recursive=False):
            nested.append(sub.extract())
        text = inline_text(li).strip()
        text = re.sub(r'\s*\n\s*', '\n', text)
        bullet = f'{idx}.' if ordered else '-'
        pad = '  ' * depth
        if text:
            first, *rest = text.split('\n')
            lines.append(f'{pad}{bullet} {first}')
            for r in rest:
                if r.strip():
                    lines.append(f'{pad}  {r.strip()}')
        for sub in nested:
            lines.append(render_list(sub, depth + 1, ordered=sub.name == 'ol'))
    return '\n'.join(l for l in lines if l)


def render_table(node):
    rows = node.select('.bb_table_tr')
    if not rows:
        return ''
    out_rows = []
    for tr in rows:
        cells = tr.select('.bb_table_th, .bb_table_td')
        rendered = []
        for c in cells:
            text = inline_text(c).strip()
            text = re.sub(r'\s*\n\s*', ' <br> ', text)
            text = text.replace('|', '\\|')
            rendered.append(text)
        # drop rows whose cells are all empty (e.g. image-only rows)
        if any(cell for cell in rendered):
            out_rows.append(rendered)
    if not out_rows:
        return ''  # entire table was media-only
    ncols = max(len(r) for r in out_rows)
    for r in out_rows:
        r += [''] * (ncols - len(r))
    lines = ['| ' + ' | '.join(out_rows[0]) + ' |',
             '|' + '---|' * ncols]
    for r in out_rows[1:]:
        lines.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(lines)


def render_block_element(child):
    classes = child.get('class') or []
    if child.name == 'div':
        for cls, prefix in BLOCK_CLASSES.items():
            if cls in classes:
                return f'{prefix} {inline_text(child).strip()}\n'
        if 'bb_table' in classes:
            return render_table(child) + '\n'
        return render_blocks(child)
    if child.name in ('ul', 'ol'):
        return render_list(child, ordered=child.name == 'ol') + '\n'
    if child.name == 'blockquote':
        inner = render_blocks(child).strip()
        return '\n'.join('> ' + l for l in inner.split('\n')) + '\n'
    return inline_text(child)


def render_blocks(container):
    """Render a mixed inline/block container to markdown paragraphs."""
    parts = []      # finished block strings
    buf = []        # accumulating inline run

    def flush():
        text = ''.join(buf).strip()
        buf.clear()
        if not text:
            return
        # collapse 3+ newlines, trim per-line whitespace
        lines = [l.strip() for l in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # single newlines inside a paragraph become hard breaks via blank line?
        # Keep as-is: Steam uses <br> for intentional line breaks.
        if text:
            parts.append(text)

    for child in container.children:
        if isinstance(child, NavigableString):
            buf.append(re.sub(r'\s+', ' ', str(child)))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name
        classes = child.get('class') or []
        is_block = (
            name in ('ul', 'ol', 'blockquote', 'table')
            or (name == 'div' and (set(classes) & set(BLOCK_CLASSES) or 'bb_table' in classes))
            or (name == 'div')
        )
        if is_block:
            flush()
            rendered = render_block_element(child).rstrip()
            if rendered.strip():
                parts.append(rendered)
        else:
            buf.append(render_inline_node(child))
    flush()
    return '\n\n'.join(parts) + '\n'


def main():
    with open(SRC) as f:
        soup = BeautifulSoup(f, 'lxml')

    title = soup.select_one('.workshopItemTitle').get_text(strip=True)
    overview = soup.select_one('.guideTopDescription')
    sections = soup.select('div.subSection.detailBox')

    skip = {'Games in this guide - Part 1', 'Games in this guide - Part 2'}
    chapters = []
    for sec in sections:
        st = sec.select_one('.subSectionTitle').get_text(strip=True)
        if st in skip:
            continue
        body = render_blocks(sec.select_one('.subSectionDesc')).strip()
        chapters.append((st, body))

    md = [f'# {title}', '']

    if overview:
        ov = render_blocks(overview).strip()
        if ov:
            md += ['## Overview', '', ov, '']

    md += ['## Table of Contents', '']
    for i, (st, _) in enumerate(chapters, 1):
        md.append(f'{i}. [{st}](#{slugify(st)})')
    md.append('')

    for st, body in chapters:
        md += [f'## {st}', '', body, '']

    text = '\n'.join(md)
    # post-pass: drop lines that are empty markdown artifacts
    text = re.sub(r'\n{3,}', '\n\n', text)
    # drop stray lines that only contain leftover formatting like lone '*' or '**'
    text = '\n'.join(l for l in text.split('\n')
                     if l.strip() not in ('*', '**', '_', '__'))
    with open(DST, 'w') as f:
        f.write(text.rstrip() + '\n')
    print(f'wrote {DST}: {len(text)} chars, {len(chapters)} chapters')


if __name__ == '__main__':
    main()
