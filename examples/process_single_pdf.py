"""
Example: Process Single PDF
Process a single PDF file without running the full pipeline
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pdf_extractor import PDFExtractor
from llm_extractor import DigitalTransformationExtractor
from database import DatabaseManager
from config import Config
import json


def process_single_pdf(pdf_path: str, max_chunks: int = None):
    """
    Process a single PDF file
    
    Args:
        pdf_path: Path to PDF file
        max_chunks: Maximum chunks to process (None = all)
    """
    
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    print(f"Processing: {pdf_path.name}")
    print("="*60)
    
    # Initialize extractors
    pdf_extractor = PDFExtractor()
    llm_extractor = DigitalTransformationExtractor(
        api_key=Config.OPENAI_API_KEY,
        model=Config.OPENAI_MODEL
    )
    
    # Extract metadata
    metadata = pdf_extractor.extract_metadata_from_filename(pdf_path.name)
    print(f"\nMetadata:")
    print(f"  Company: {metadata['company_name']}")
    print(f"  Report Type: {metadata['report_type']}")
    print(f"  Year: {metadata['year']}")
    
    # Extract text
    print(f"\nExtracting text...")
    full_text = pdf_extractor.extract_text_from_pdf(pdf_path)
    print(f"  Extracted {len(full_text):,} characters")
    
    # Chunk text
    chunks = pdf_extractor.chunk_text(full_text)
    print(f"  Created {len(chunks)} chunks")
    
    # Extract initiatives
    print(f"\nExtracting initiatives...")
    initiatives = llm_extractor.extract_from_document(
        chunks=chunks,
        company_name=metadata['company_name'],
        year=metadata['year'],
        report_type=metadata['report_type'],
        max_chunks=max_chunks
    )
    
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"Total initiatives found: {len(initiatives)}")
    
    if initiatives:
        # Group by category
        by_category = {}
        for init in initiatives:
            cat = init['Category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(init)
        
        print(f"\nBy Category:")
        for cat, inits in by_category.items():
            print(f"  {cat}: {len(inits)}")
        
        # Show sample initiatives
        print(f"\nSample Initiatives:")
        for i, init in enumerate(initiatives[:3], 1):
            print(f"\n{i}. {init['Category']}")
            print(f"   Initiative: {init['Initiative'][:100]}...")
            print(f"   Technology: {init['TechnologyUsed']}")
        
        # Save to JSON
        output_file = Config.OUTPUT_DIR / f"{metadata['company_name']}_{metadata['year']}_single.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(initiatives, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to: {output_file}")
        
        # Ask to save to database
        save_to_db = input("\nSave to database? (y/n): ")
        if save_to_db.lower() == 'y':
            db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
            try:
                company_id = db.get_or_create_company(metadata['company_name'])
                year = int(metadata['year']) if metadata['year'].isdigit() else 0
                report_id = db.get_or_create_report(
                    company_id=company_id,
                    report_type=metadata['report_type'],
                    report_year=year,
                    filename=pdf_path.name,
                    file_path=str(pdf_path)
                )
                db.insert_initiatives(report_id, initiatives)
                print("✓ Saved to database")
            finally:
                db.close()
    
    print(f"\n{'='*60}")
    print("Processing complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process a single PDF file")
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument(
        '--max-chunks',
        type=int,
        default=None,
        help='Maximum chunks to process (default: all)'
    )
    
    args = parser.parse_args()
    
    process_single_pdf(args.pdf_path, args.max_chunks)
