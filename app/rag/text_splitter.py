"""文本切片：Markdown 按标题切章节，其它按段落/长度切。

不依赖 LangChain，参数来自 Settings.chunk_size / chunk_overlap。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    section_title: str = ""
    chunk_index: int = 0


_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)


class TextSplitter:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 80):
        if chunk_size < 50:
            raise ValueError("chunk_size 过小")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str, doc_type: str = "txt") -> list[TextChunk]:
        cleaned = (text or "").strip()
        if not cleaned:
            return []

        kind = doc_type.lower().replace("text/", "")
        if kind in {"md", "markdown"}:
            raw = self._split_markdown(cleaned)
        else:
            raw = [TextChunk(content=c) for c in self._split_generic(cleaned)]

        chunks = [c for c in raw if c.content.strip()]
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
        return chunks

    def _split_markdown(self, text: str) -> list[TextChunk]:
        sections = self._parse_sections(text)
        if not sections:
            return [TextChunk(content=c) for c in self._split_generic(text)]

        result: list[TextChunk] = []
        for section in sections:
            body = text[section["start"] : section["end"]].strip()
            if not body:
                continue
            for piece in self._split_generic(body):
                result.append(TextChunk(content=piece, section_title=section["title"]))
        return result

    def _parse_sections(self, text: str) -> list[dict]:
        headings = [
            (m.start(), len(m.group(1)), m.group(2).strip())
            for m in _HEADING_RE.finditer(text)
        ]
        if not headings:
            return []

        sections: list[dict] = []
        if headings[0][0] > 0 and text[: headings[0][0]].strip():
            sections.append({"start": 0, "end": headings[0][0], "title": ""})

        for i, (pos, level, title) in enumerate(headings):
            end = headings[i + 1][0] if i + 1 < len(headings) else len(text)
            sections.append({
                "start": pos,
                "end": end,
                "title": f"{'#' * level} {title}",
            })
        return sections

    def _split_generic(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if not paragraphs:
            return self._window(text)

        pieces: list[str] = []
        buf = ""
        for para in paragraphs:
            if len(para) > self.chunk_size:
                if buf:
                    pieces.append(buf)
                    buf = ""
                pieces.extend(self._window(para))
                continue
            candidate = f"{buf}\n\n{para}".strip() if buf else para
            if len(candidate) <= self.chunk_size:
                buf = candidate
            else:
                pieces.append(buf)
                buf = para
        if buf:
            pieces.append(buf)
        return pieces

    def _window(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        step = self.chunk_size - self.chunk_overlap
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(text):
                break
            start += step
        return chunks
