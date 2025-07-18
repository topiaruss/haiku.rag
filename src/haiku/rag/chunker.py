from typing import ClassVar

import tiktoken

from haiku.rag.config import Config


class Chunker:
    """A class that chunks text into smaller pieces for embedding and retrieval.

    Args:
        chunk_size: The maximum size of a chunk in tokens.
        chunk_overlap: The number of tokens of overlap between chunks.
    """

    encoder: ClassVar[tiktoken.Encoding] = tiktoken.encoding_for_model("gpt-4o")

    def __init__(
        self,
        chunk_size: int = Config.CHUNK_SIZE,
        chunk_overlap: int = Config.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def chunk(self, text: str) -> list[str]:
        """Split the text into chunks based on token boundaries.

        Args:
            text: The text to be split into chunks.

        Returns:
            A list of text chunks with token-based boundaries and overlap.
        """
        if not text:
            return []

        encoded_tokens = self.encoder.encode(text, disallowed_special=())

        if self.chunk_size > len(encoded_tokens):
            return [text]

        chunks = []
        i = 0
        split_id_counter = 0
        while i < len(encoded_tokens):
            # Overlap
            start_i = i
            end_i = min(i + self.chunk_size, len(encoded_tokens))

            chunk_tokens = encoded_tokens[start_i:end_i]
            chunk_text = self.encoder.decode(chunk_tokens)

            chunks.append(chunk_text)
            split_id_counter += 1

            # Exit loop if this was the last possible chunk
            if end_i == len(encoded_tokens):
                break

            i += (
                self.chunk_size - self.chunk_overlap
            )  # Step forward, considering overlap
        return chunks


chunker = Chunker()
