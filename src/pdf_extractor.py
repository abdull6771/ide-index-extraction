"""
PDF Text Extraction Module
Extracts text from Annual Reports, Corporate Governance Reports, and Sustainability Reports
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from PyPDF2 import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF text extraction and metadata parsing"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.supported_years = [2022, 2023, 2024, 2025]
        
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Extract company name, report type, and year from filename
        
        Expected patterns:
        - CompanyName - Annual Report 2023.pdf
        - CompanyName - Corporate Governance Report 2024.pdf
        - CompanyName - Sustainability Report 2023.pdf
        - CompanyName_Annual Report_2023.pdf
        """
        metadata = {
            'company_name': '',
            'report_type': '',
            'year': '',
            'filename': filename
        }
        
        # Extract year (2022-2025)
        year_match = re.search(r'(2022|2023|2024|2025)', filename)
        if year_match:
            metadata['year'] = year_match.group(1)
        
        # Extract report type
        if 'Annual Report' in filename or 'Annual_Report' in filename:
            metadata['report_type'] = 'Annual Report'
        elif 'Corporate Governance' in filename or 'CG Report' in filename:
            metadata['report_type'] = 'Corporate Governance Report'
        elif 'Sustainability' in filename or 'ESG' in filename:
            metadata['report_type'] = 'Sustainability Report'
        else:
            metadata['report_type'] = 'Other'
        
        # Extract company name (everything before the report type or year)
        # Remove file extension first
        name_part = filename.replace('.pdf', '').replace('.PDF', '')
        
        # Remove year
        if metadata['year']:
            name_part = name_part.replace(metadata['year'], '')
        
        # Remove report type indicators
        for indicator in ['Annual Report', 'Annual_Report', 'Corporate Governance Report', 
                         'Corporate_Governance_Report', 'CG Report', 'Sustainability Report',
                         'Sustainability_Report', 'ESG Report']:
            name_part = name_part.replace(indicator, '')
        
        # Clean up separators and whitespace
        company_name = re.sub(r'[-_\s]+', ' ', name_part).strip()
        metadata['company_name'] = company_name
        
        return metadata
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract all text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {pdf_path.name} ({num_pages} pages)")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num} ---\n{page_text}"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")
                        continue
                
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 3000, overlap: int = 500) -> List[str]:
        """
        Split text into overlapping chunks for LLM processing
        
        Args:
            text: Full text to chunk
            chunk_size: Target size of each chunk (characters)
            overlap: Overlap between chunks (characters)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at a paragraph or sentence boundary
            if end < text_length:
                # Look for paragraph break
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break > start:
                    end = paragraph_break
                else:
                    # Look for sentence break
                    sentence_break = text.rfind('. ', start, end)
                    if sentence_break > start:
                        end = sentence_break + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def process_all_pdfs(self) -> List[Dict]:
        """
        Process all PDFs in the data directory
        
        Returns:
            List of dictionaries containing metadata and extracted text
        """
        results = []
        
        if not self.data_dir.exists():
            logger.error(f"Data directory {self.data_dir} does not exist")
            return results
        
        pdf_files = list(self.data_dir.glob("*.pdf")) + list(self.data_dir.glob("*.PDF"))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            logger.info(f"\nProcessing: {pdf_path.name}")
            
            # Extract metadata from filename
            metadata = self.extract_metadata_from_filename(pdf_path.name)
            
            # Extract text
            full_text = self.extract_text_from_pdf(pdf_path)
            
            if not full_text:
                logger.warning(f"No text extracted from {pdf_path.name}")
                continue
            
            # Chunk the text
            chunks = self.chunk_text(full_text)
            
            result = {
                'company_name': metadata['company_name'],
                'report_type': metadata['report_type'],
                'year': metadata['year'],
                'filename': metadata['filename'],
                'full_text': full_text,
                'chunks': chunks,
                'num_chunks': len(chunks),
                'file_path': str(pdf_path)
            }
            
            results.append(result)
            
            logger.info(f"  Company: {metadata['company_name']}")
            logger.info(f"  Report Type: {metadata['report_type']}")
            logger.info(f"  Year: {metadata['year']}")
            logger.info(f"  Text length: {len(full_text):,} characters")
            logger.info(f"  Number of chunks: {len(chunks)}")
        
        return results


if __name__ == "__main__":
    # Test the extractor
    import sys
    from pathlib import Path
    
    # Get the correct data directory path
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    
    extractor = PDFExtractor(data_dir=str(data_dir))
    results = extractor.process_all_pdfs()
    
    print(f"\n{'='*60}")
    print(f"Processed {len(results)} PDF files")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\n{result['company_name']} - {result['report_type']} ({result['year']})")
        print(f"  Chunks: {result['num_chunks']}")
