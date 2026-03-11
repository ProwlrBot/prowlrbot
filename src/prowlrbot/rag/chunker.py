# -*- coding: utf-8 -*-
"""Text chunking utilities for the RAG module."""

from __future__ import annotations

import re

from .models import ChunkingStrategy


class TextChunker:
    """Splits text into chunks using various strategies."""

    # Sentence boundary: period, exclamation, or question mark followed by
    # whitespace (or end of string).
    _SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

    def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.paragraph,
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> list[str]:
        """Split *text* into chunks according to *strategy*.

        Parameters
        ----------
        text:
            The full document text.
        strategy:
            Chunking strategy to apply.
        chunk_size:
            Target chunk size in characters (used by fixed_size and as a
            fallback upper bound for sentence/paragraph strategies).
        overlap:
            Number of overlapping characters between consecutive chunks
            (fixed_size strategy only).
        """
        if not text or not text.strip():
            return []

        if strategy == ChunkingStrategy.fixed_size:
            return self._fixed_size_chunk(text, chunk_size, overlap)
        if strategy == ChunkingStrategy.sentence:
            return self._sentence_chunk(text, chunk_size)
        if strategy == ChunkingStrategy.paragraph:
            return self._paragraph_chunk(text, chunk_size)
        # Semantic strategy falls back to paragraph for now (no embeddings).
        return self._paragraph_chunk(text, chunk_size)

    # ------------------------------------------------------------------
    # Private strategy implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _fixed_size_chunk(text: str, size: int, overlap: int) -> list[str]:
        """Split text into fixed-size character windows with overlap."""
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - overlap
        return chunks

    def _sentence_chunk(self, text: str, chunk_size: int) -> list[str]:
        """Split on sentence boundaries, merging small sentences up to *chunk_size*."""
        sentences = self._SENTENCE_RE.split(text)
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if current_len + len(sentence) > chunk_size and current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            current.append(sentence)
            current_len += len(sentence) + 1  # +1 for joining space

        if current:
            chunks.append(" ".join(current))
        return chunks

    def _paragraph_chunk(self, text: str, chunk_size: int) -> list[str]:
        """Split on paragraph boundaries (blank lines), merging small paragraphs."""
        paragraphs = re.split(r"\n\s*\n", text)
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if current_len + len(para) > chunk_size and current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(para)
            current_len += len(para) + 2  # +2 for joining "\n\n"

        if current:
            chunks.append("\n\n".join(current))
        return chunks
