import requests
import re
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import (
    INNOCENTS_ABROAD_URL,
    BOOK_RAW_PATH,
    BOOK_CLEAN_PATH,
    BOOK_PROCESSED_PATH,
    LANGCHAIN_CHUNK_SIZE,
    LANGCHAIN_CHUNK_OVERLAP
)

logger = logging.getLogger(__name__)


class GutenbergDownloader:
    """Downloads and processes text from Project Gutenberg"""

    def __init__(self):
        # Ensure data directory exists
        BOOK_RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    def download_innocents_abroad(self) -> Optional[Path]:
        """
        Download 'The Innocents Abroad' by Mark Twain from Project Gutenberg
        Returns path to cleaned text file
        """
        try:
            logger.info("Downloading 'The Innocents Abroad' from Project Gutenberg...")
            response = requests.get(INNOCENTS_ABROAD_URL)
            response.raise_for_status()

            # Save raw text
            with open(BOOK_RAW_PATH, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"Raw text saved to: {BOOK_RAW_PATH}")

            # Process and clean the text
            cleaned_text = self._clean_gutenberg_text(response.text)

            # Save cleaned text
            with open(BOOK_CLEAN_PATH, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            logger.info(f"Clean text saved to: {BOOK_CLEAN_PATH}")

            # Create searchable chunks
            chunks = self._create_text_chunks(cleaned_text)
            self._save_processed_chunks(chunks)
            logger.info(f"Processed chunks saved to: {BOOK_PROCESSED_PATH}")

            return BOOK_CLEAN_PATH

        except Exception as e:
            logger.error(f"Error downloading book: {e}")
            return None

    def _clean_gutenberg_text(self, text: str) -> str:
        """Clean Project Gutenberg text by removing headers/footers"""

        # Find start of actual book content
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG EBOOK",
            "*** START OF THIS PROJECT GUTENBERG EBOOK",
            "THE INNOCENTS ABROAD"
        ]

        start_pos = 0
        for marker in start_markers:
            pos = text.find(marker)
            if pos != -1:
                # Skip the header line itself
                next_line = text.find('\n', pos)
                if next_line != -1:
                    start_pos = next_line + 1
                break

        # Find end of book content
        end_markers = [
            "*** END OF THE PROJECT GUTENBERG EBOOK",
            "*** END OF THIS PROJECT GUTENBERG EBOOK",
            "End of the Project Gutenberg"
        ]

        end_pos = len(text)
        for marker in end_markers:
            pos = text.find(marker)
            if pos != -1:
                end_pos = pos
                break

        # Extract main content
        content = text[start_pos:end_pos]

        # Clean up formatting
        content = re.sub(r'\r\n', '\n', content)  # Normalize line endings
        content = re.sub(r'\n{3,}', '\n\n', content)  # Reduce excessive newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Normalize whitespace
        content = content.strip()

        return content

    def _extract_chapters(self, text: str) -> List[Dict[str, any]]:
        """Extract chapters and their metadata from the book"""
        # Pattern to match chapter headers (Roman numerals)
        chapter_pattern = r'(^|\n)(?:CHAPTER\s+)?([IVXLCDM]+)\.\s*\n'

        chapters = []
        matches = list(re.finditer(chapter_pattern, text, re.MULTILINE))

        for i, match in enumerate(matches):
            chapter_num = match.group(2)
            start_pos = match.end()

            # Find end position (start of next chapter or end of text)
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            chapter_text = text[start_pos:end_pos].strip()

            # Extract chapter title (first line after chapter number)
            lines = chapter_text.split('\n', 1)
            title = lines[0].strip() if lines else ""
            content = lines[1].strip() if len(lines) > 1 else chapter_text

            chapters.append({
                'chapter_number': chapter_num,
                'chapter_title': title,
                'content': content,
                'start_pos': start_pos,
                'end_pos': end_pos
            })

        return chapters

    def _create_text_chunks(self, text: str) -> List[Dict[str, any]]:
        """Create overlapping text chunks with chapter metadata using LangChain's text splitter"""
        # First extract chapter information
        chapters = self._extract_chapters(text)

        # Initialize LangChain text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=LANGCHAIN_CHUNK_SIZE,
            chunk_overlap=LANGCHAIN_CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
            keep_separator=True
        )

        # Process each chapter separately to maintain metadata
        all_chunks = []
        chunk_id = 0

        for chapter in chapters:
            chapter_text = chapter['content']
            chapter_chunks = text_splitter.split_text(chapter_text)

            for chunk_idx, chunk_text in enumerate(chapter_chunks):
                all_chunks.append({
                    'id': chunk_id,
                    'text': chunk_text.strip(),
                    'length': len(chunk_text),
                    'chunk_index': chunk_id,
                    'chapter_number': chapter['chapter_number'],
                    'chapter_title': chapter['chapter_title'],
                    'chunk_in_chapter': chunk_idx,
                    'total_chunks_in_chapter': len(chapter_chunks)
                })
                chunk_id += 1

        return all_chunks

    def _save_processed_chunks(self, chunks: List[Dict[str, any]]) -> None:
        """Save processed chunks to JSON file"""
        with open(BOOK_PROCESSED_PATH, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

    def load_book_chunks(self) -> Optional[List[Dict[str, any]]]:
        """Load processed book chunks from JSON file"""
        try:
            if BOOK_PROCESSED_PATH.exists():
                with open(BOOK_PROCESSED_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading book chunks: {e}")
            return None

    def is_book_downloaded(self) -> bool:
        """Check if the book has been downloaded and processed"""
        return (BOOK_CLEAN_PATH.exists() and
                BOOK_PROCESSED_PATH.exists() and
                BOOK_CLEAN_PATH.stat().st_size > 0)


if __name__ == "__main__":
    downloader = GutenbergDownloader()
    if not downloader.is_book_downloaded():
        downloader.download_innocents_abroad()
    else:
        logger.info("Book already downloaded and processed.")
