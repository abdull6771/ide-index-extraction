"""
Main Pipeline Script
Orchestrates the entire extraction process from PDF to database
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import List, Dict

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor import PDFExtractor
from llm_extractor import DigitalTransformationExtractor
from database import DatabaseManager
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExtractionPipeline:
    """Main pipeline for extracting digital transformation initiatives"""
    
    def __init__(self):
        """Initialize pipeline components"""
        logger.info("Initializing extraction pipeline...")
        
        # Validate configuration
        if not Config.validate():
            raise ValueError("Configuration validation failed")
        
        # Initialize components
        self.pdf_extractor = PDFExtractor(data_dir=str(Config.DATA_DIR))
        self.llm_extractor = DigitalTransformationExtractor(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL
        )
        self.db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
        
        # Create output directory
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info("Pipeline initialized successfully")
    
    def run(self, max_chunks_per_doc: int = None, save_json: bool = True):
        """
        Run the complete extraction pipeline
        
        Args:
            max_chunks_per_doc: Maximum chunks to process per document (None = all)
            save_json: Whether to save results to JSON files
        """
        start_time = datetime.now()
        
        logger.info("="*80)
        logger.info("STARTING DIGITAL TRANSFORMATION EXTRACTION PIPELINE")
        logger.info("="*80)
        
        Config.print_config()
        
        # Step 1: Extract text from PDFs
        logger.info("\n" + "="*80)
        logger.info("STEP 1: EXTRACTING TEXT FROM PDF FILES")
        logger.info("="*80)
        
        pdf_results = self.pdf_extractor.process_all_pdfs()
        
        if not pdf_results:
            logger.error("No PDFs found or processed. Exiting.")
            return
        
        logger.info(f"\nSuccessfully extracted text from {len(pdf_results)} PDF files")
        
        # Step 2: Extract digital initiatives using LLM
        logger.info("\n" + "="*80)
        logger.info("STEP 2: EXTRACTING DIGITAL INITIATIVES USING LLM")
        logger.info("="*80)
        
        all_initiatives = []
        
        for i, pdf_result in enumerate(pdf_results, 1):
            logger.info(f"\n--- Processing Document {i}/{len(pdf_results)} ---")
            logger.info(f"Company: {pdf_result['company_name']}")
            logger.info(f"Report: {pdf_result['report_type']} ({pdf_result['year']})")
            
            # Determine max chunks
            max_chunks = max_chunks_per_doc or Config.MAX_CHUNKS_PER_DOCUMENT
            if max_chunks == 0:
                max_chunks = None
            
            # Extract initiatives
            initiatives = self.llm_extractor.extract_from_document(
                chunks=pdf_result['chunks'],
                company_name=pdf_result['company_name'],
                year=pdf_result['year'],
                report_type=pdf_result['report_type'],
                max_chunks=max_chunks
            )
            
            # Add metadata
            for init in initiatives:
                init['source_file'] = pdf_result['filename']
                init['report_type'] = pdf_result['report_type']
            
            all_initiatives.extend(initiatives)
            
            # Store in database
            if initiatives:
                self._store_in_database(pdf_result, initiatives)
            
            # Save individual JSON file
            if save_json and initiatives:
                output_file = Config.OUTPUT_DIR / f"{pdf_result['company_name']}_{pdf_result['year']}_{pdf_result['report_type'].replace(' ', '_')}.json"
                self.llm_extractor.save_to_json(initiatives, str(output_file))
        
        # Step 3: Save consolidated results
        logger.info("\n" + "="*80)
        logger.info("STEP 3: SAVING CONSOLIDATED RESULTS")
        logger.info("="*80)
        
        if save_json and all_initiatives:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            consolidated_file = Config.OUTPUT_DIR / f"all_initiatives_{timestamp}.json"
            
            consolidated_data = {
                'metadata': {
                    'total_initiatives': len(all_initiatives),
                    'total_documents': len(pdf_results),
                    'extraction_date': datetime.now().isoformat(),
                    'model': Config.OPENAI_MODEL
                },
                'initiatives': all_initiatives
            }
            
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved consolidated results to {consolidated_file}")
        
        # Step 4: Generate statistics
        logger.info("\n" + "="*80)
        logger.info("STEP 4: GENERATING STATISTICS")
        logger.info("="*80)
        
        stats = self.db.get_statistics()
        
        logger.info(f"\nTotal Companies: {stats['total_companies']}")
        logger.info(f"Total Reports: {stats['total_reports']}")
        logger.info(f"Total Initiatives: {stats['total_initiatives']}")
        
        logger.info("\nInitiatives by Category:")
        for category, count in stats['by_category'].items():
            logger.info(f"  {category}: {count}")
        
        logger.info("\nInitiatives by Year:")
        for year, count in stats['by_year'].items():
            logger.info(f"  {year}: {count}")
        
        logger.info("\nTop Companies:")
        for company, count in stats['top_companies'].items():
            logger.info(f"  {company}: {count} initiatives")
        
        # Export database to JSON
        if save_json:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = Config.OUTPUT_DIR / f"database_export_{timestamp}.json"
            self.db.export_to_json(str(export_file))
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Documents Processed: {len(pdf_results)}")
        logger.info(f"Total Initiatives Extracted: {len(all_initiatives)}")
        logger.info(f"Database: {Config.DATABASE_PATH}")
        logger.info(f"Output Directory: {Config.OUTPUT_DIR}")
        logger.info("="*80)
    
    def _store_in_database(self, pdf_result: Dict, initiatives: List[Dict]):
        """Store extracted initiatives in database"""
        try:
            # Get or create company
            company_id = self.db.get_or_create_company(
                company_name=pdf_result['company_name']
            )
            
            # Get or create report
            year = int(pdf_result['year']) if pdf_result['year'].isdigit() else 0
            report_id = self.db.get_or_create_report(
                company_id=company_id,
                report_type=pdf_result['report_type'],
                report_year=year,
                filename=pdf_result['filename'],
                file_path=pdf_result['file_path']
            )
            
            # Insert initiatives
            self.db.insert_initiatives(report_id, initiatives)
            
        except Exception as e:
            logger.error(f"Error storing in database: {e}")
    
    def close(self):
        """Clean up resources"""
        self.db.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract digital transformation initiatives from corporate reports"
    )
    parser.add_argument(
        '--max-chunks',
        type=int,
        default=0,
        help='Maximum chunks to process per document (0 = all chunks)'
    )
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Skip saving JSON output files'
    )
    
    args = parser.parse_args()
    
    try:
        pipeline = ExtractionPipeline()
        pipeline.run(
            max_chunks_per_doc=args.max_chunks if args.max_chunks > 0 else None,
            save_json=not args.no_json
        )
        pipeline.close()
        
    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
