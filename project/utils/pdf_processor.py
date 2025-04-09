# utils/pdf_processor.py
import os
import re

import pdfplumber


class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path


    def extract_text(self, ignore_tables: bool = True) -> str:
        """Extract text from a PDF, optionally ignoring tables."""

        full_text = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = self._clean_text(page_text)
                    full_text.append(cleaned_text)

                # 提取表格（可选）
                if not ignore_tables:
                    tables = page.extract_tables()
                    for table in tables:
                        full_text.append("\n[Table] " + str(table))
        return "\n".join(full_text)

    def _clean_text(self, text: str) -> str:
       # Clean up text: Remove page numbers, references, redundant Spaces

        # Remove Page numbers
        text = re.sub(r'Page\s+\d+', '', text, flags=re.IGNORECASE)
        # Remove the references section
        text = re.sub(r'References?\s*.*', '', text, flags=re.DOTALL)
        # Merge consecutive line breaks
        text = re.sub(r'\n+', '\n', text)
        return text.strip()


# 示例用法
if __name__ == "__main__":
    path = "../data/"
    file_name = "The top-down approach to computer networking, 8th edition.pdf"

    processor = PDFProcessor(os.path.join(path, file_name))

    text = processor.extract_text(ignore_tables=False)

    print("Extracted Text:", text[:500])
