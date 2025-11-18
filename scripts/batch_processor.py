#!/usr/bin/env python3
"""
Memory-Efficient Batch Processor
Process PDFs one at a time with memory cleanup between each file
Ideal for cloud GPU environments with limited RAM
"""

import sys
import os
import gc
from pathlib import Path
import argparse
import logging
from datetime import datetime
import json

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pdf_extractor import PDFExtractor
from llm_extractor import DigitalTransformationExtractor
from database import DatabaseManager
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def process_pdf_with_cleanup(pdf_path: Path, max_chunks: int, db_path: str):
    """
    Process a single PDF with memory cleanup
    
    Args:
        pdf_path: Path to PDF file
        max_chunks: Maximum chunks to process
        db_path: Database path
        
    Returns:
        dict: Processing results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Processing: {pdf_path.name}")
    logger.info(f"{'='*80}")
    
    # Initialize components (fresh for each PDF)
    pdf_extractor = PDFExtractor(data_dir=str(pdf_path.parent))
    llm_extractor = DigitalTransformationExtractor(
        api_key=Config.OPENAI_API_KEY,
        model=Config.OPENAI_MODEL
    )
    db = DatabaseManager(db_path=db_path)
    
    try:
        # Extract text
        logger.info("Extracting text from PDF...")
        result = pdf_extractor.process_pdf(str(pdf_path))
        
        if not result:
            logger.error(f"Failed to extract text from {pdf_path.name}")
            return None
        
        logger.info(f"  Company: {result['company_name']}")
        logger.info(f"  Report: {result['report_type']} ({result['year']})")
        logger.info(f"  Total chunks: {len(result['chunks'])}")
        logger.info(f"  Processing: {min(max_chunks, len(result['chunks']))} chunks")
        
        # Extract initiatives
        logger.info("Extracting digital initiatives...")
        initiatives = llm_extractor.extract_from_document(
            chunks=result['chunks'],
            company_name=result['company_name'],
            year=result['year'],
            report_type=result['report_type'],
            max_chunks=max_chunks
        )
        
        logger.info(f"Extracted {len(initiatives)} initiatives")
        
        # Store in database
        if initiatives:
            company_id = db.add_company(
                company_name=result['company_name'],
                industry=None,
                market_cap=None
            )
            
            report_id = db.add_report(
                company_id=company_id,
                report_type=result['report_type'],
                year=result['year'],
                source_file=result['filename']
            )
            
            for init in initiatives:
                db.add_initiative(
                    report_id=report_id,
                    initiative_name=init['initiative_name'],
                    category=init['category'],
                    description=init['description'],
                    impact=init.get('impact'),
                    investment=init.get('investment'),
                    confidence_score=init.get('confidence_score', 0.0)
                )
            
            logger.info(f"Stored in database: {len(initiatives)} initiatives")
        
        # Save individual JSON
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = Config.OUTPUT_DIR / f"{result['company_name']}_{result['year']}_{result['report_type'].replace(' ', '_')}.json"
        
        output_data = {
            'metadata': {
                'company': result['company_name'],
                'report_type': result['report_type'],
                'year': result['year'],
                'source_file': result['filename'],
                'processed_chunks': min(max_chunks, len(result['chunks'])),
                'extraction_date': datetime.now().isoformat(),
                'total_initiatives': len(initiatives)
            },
            'initiatives': initiatives
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved to: {output_file}")
        
        return {
            'filename': pdf_path.name,
            'company': result['company_name'],
            'report_type': result['report_type'],
            'year': result['year'],
            'initiatives_count': len(initiatives),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error processing {pdf_path.name}: {e}", exc_info=True)
        return {
            'filename': pdf_path.name,
            'success': False,
            'error': str(e)
        }
    
    finally:
        # Close database connection
        db.close()
        
        # Force garbage collection
        del pdf_extractor
        del llm_extractor
        del db
        gc.collect()
        
        logger.info("Memory cleanup completed")


def main():
    parser = argparse.ArgumentParser(
        description='Memory-efficient batch processor for cloud GPU environments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script processes PDFs one at a time with memory cleanup between each file.
Ideal for cloud GPU environments with limited RAM.

Examples:
  # Process all PDFs with 10 chunks each
  python batch_processor.py --max-chunks 10
  
  # Process with 5 chunks (very memory-efficient)
  python batch_processor.py --max-chunks 5
  
  # Process specific PDFs only
  python batch_processor.py --max-chunks 10 --files "data/Company1_*.pdf" "data/Company2_*.pdf"
        """
    )
    
    parser.add_argument(
        '--max-chunks',
        type=int,
        default=10,
        help='Maximum chunks to process per document (default: 10)'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        default=None,
        help='Specific PDF files to process (default: all PDFs in data directory)'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        if not Config.validate():
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        logger.info("="*80)
        logger.info("MEMORY-EFFICIENT BATCH PROCESSOR")
        logger.info("="*80)
        logger.info(f"Max chunks per document: {args.max_chunks}")
        logger.info(f"Model: {Config.OPENAI_MODEL}")
        logger.info(f"Database: {Config.DATABASE_PATH}")
        logger.info("="*80)
        
        # Get PDF files
        if args.files:
            pdf_files = []
            for pattern in args.files:
                pdf_files.extend(Path().glob(pattern))
        else:
            pdf_files = list(Config.DATA_DIR.glob("*.pdf"))
        
        pdf_files = sorted(pdf_files)
        
        if not pdf_files:
            logger.error("No PDF files found")
            sys.exit(1)
        
        logger.info(f"\nFound {len(pdf_files)} PDF files to process:")
        for i, pdf in enumerate(pdf_files, 1):
            logger.info(f"  {i}. {pdf.name}")
        
        # Process each PDF
        results = []
        start_time = datetime.now()
        
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"PDF {i}/{len(pdf_files)}")
            logger.info(f"{'='*80}")
            
            result = process_pdf_with_cleanup(
                pdf_path=pdf_path,
                max_chunks=args.max_chunks,
                db_path=str(Config.DATABASE_PATH)
            )
            
            if result:
                results.append(result)
        
        # Print summary
        elapsed_time = datetime.now() - start_time
        
        logger.info("\n" + "="*80)
        logger.info("BATCH PROCESSING SUMMARY")
        logger.info("="*80)
        logger.info(f"Total PDFs processed: {len(results)}")
        logger.info(f"Successful: {sum(1 for r in results if r['success'])}")
        logger.info(f"Failed: {sum(1 for r in results if not r['success'])}")
        logger.info(f"Total time: {elapsed_time}")
        logger.info("")
        
        total_initiatives = 0
        logger.info("Results by file:")
        for r in results:
            if r['success']:
                logger.info(f"  ✅ {r['filename']}: {r['initiatives_count']} initiatives")
                total_initiatives += r['initiatives_count']
            else:
                logger.info(f"  ❌ {r['filename']}: {r['error']}")
        
        logger.info("")
        logger.info(f"Total initiatives extracted: {total_initiatives}")
        logger.info("="*80)
        
        # Print database statistics
        logger.info("\nDatabase Statistics:")
        db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
        stats = db.get_statistics()
        db.close()
        
        logger.info(f"  Total Companies: {stats['total_companies']}")
        logger.info(f"  Total Reports: {stats['total_reports']}")
        logger.info(f"  Total Initiatives: {stats['total_initiatives']}")
        
        logger.info("\n✅ Batch processing completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\nBatch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
