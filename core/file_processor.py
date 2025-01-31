"""
File processor for handling different file formats.
"""
from typing import Dict, Tuple
from io import BytesIO
import base64

from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from docx import Document
import markdown

class FileProcessor:
    """Handles processing of different file formats."""

    SUPPORTED_FORMATS = {'pdf', 'html', 'docx', 'txt', 'md'}

    @staticmethod
    def detect_file_type(content: str, metadata: Dict = None) -> str:
        """
        Detect the file type from content and metadata.
        
        Args:
            content: The file content as string (may be base64 encoded)
            metadata: Optional metadata containing file type hints
            
        Returns:
            str: Detected file type
        """
        if metadata and 'file_type' in metadata:
            file_type = metadata['file_type'].lower()
            if file_type in FileProcessor.SUPPORTED_FORMATS:
                return file_type

        # Try to detect from content
        if content.startswith('data:application/pdf;base64,'):
            return 'pdf'
        elif content.startswith('data:text/html;base64,') or content.strip().startswith('<!DOCTYPE html>'):
            return 'html'
        elif content.startswith('data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,'):
            return 'docx'
        elif content.startswith('data:text/markdown;base64,') or content.startswith('#'):
            return 'md'
        else:
            return 'txt'  # Default to txt if no other format detected

    @staticmethod
    def _extract_base64_content(content: str) -> Tuple[bytes, str]:
        """
        Extract content and format from base64 encoded string.
        
        Args:
            content: Base64 encoded content with format prefix
            
        Returns:
            Tuple[bytes, str]: (decoded content, format)
        """
        if ';base64,' in content:
            format_prefix = content.split(';base64,')[0]
            raw_content = content.split(';base64,')[1]
            return base64.b64decode(raw_content), format_prefix
        return content.encode(), 'text/plain'

    def process_content(self, content: str, file_type: str) -> str:
        """
        Process content based on file type.
        
        Args:
            content: The content to process
            file_type: Type of file (pdf, html, docx, txt, md)
            
        Returns:
            str: Extracted and processed text content
        """
        if file_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Extract content if base64 encoded
        raw_bytes, _ = self._extract_base64_content(content)

        try:
            if file_type == 'pdf':
                return self._process_pdf(raw_bytes)
            elif file_type == 'html':
                return self._process_html(raw_bytes)
            elif file_type == 'docx':
                return self._process_docx(raw_bytes)
            elif file_type == 'md':
                return self._process_markdown(raw_bytes)
            else:  # txt
                return raw_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error processing {file_type} content: {str(e)}")

    def _process_pdf(self, content: bytes) -> str:
        """Process PDF content."""
        pdf_file = BytesIO(content)
        try:
            text = extract_text(pdf_file)
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

    def _process_html(self, content: bytes) -> str:
        """Process HTML content."""
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise ValueError(f"Failed to process HTML: {str(e)}")

    def _process_docx(self, content: bytes) -> str:
        """Process DOCX content."""
        docx_file = BytesIO(content)
        try:
            doc = Document(docx_file)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            return '\n'.join(full_text)
        except Exception as e:
            raise ValueError(f"Failed to process DOCX: {str(e)}")

    def _process_markdown(self, content: bytes) -> str:
        """Process Markdown content."""
        try:
            md_text = content.decode('utf-8')
            # Convert to HTML first
            html = markdown.markdown(md_text)
            # Then extract text from HTML
            soup = BeautifulSoup(html, 'lxml')
            return soup.get_text()
        except Exception as e:
            raise ValueError(f"Failed to process Markdown: {str(e)}")
