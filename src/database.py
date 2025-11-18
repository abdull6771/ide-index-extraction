"""
Database Management Module
SQLite database for storing digital transformation initiatives
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for digital transformation initiatives"""
    
    def __init__(self, db_path: str = "database/ide_index.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_database()
    
    def connect(self):
        """Create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE NOT NULL,
                industry TEXT,
                stock_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                report_type TEXT NOT NULL,
                report_year INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id),
                UNIQUE(company_id, report_type, report_year)
            )
        """)
        
        # Digital initiatives table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digital_initiatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                category TEXT NOT NULL,
                initiative TEXT NOT NULL,
                technology_used TEXT,
                department TEXT,
                year_mentioned TEXT,
                expected_impact TEXT,
                digital_investment TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports (id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_initiatives_company 
            ON digital_initiatives(company_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_initiatives_category 
            ON digital_initiatives(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_initiatives_year 
            ON digital_initiatives(year_mentioned)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reports_company_year 
            ON reports(company_id, report_year)
        """)
        
        conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def get_or_create_company(self, company_name: str, industry: str = None, 
                             stock_code: str = None) -> int:
        """
        Get company ID or create new company record
        
        Args:
            company_name: Company name
            industry: Industry sector (optional)
            stock_code: Stock exchange code (optional)
            
        Returns:
            Company ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing company
        cursor.execute("SELECT id FROM companies WHERE company_name = ?", (company_name,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        
        # Create new company
        cursor.execute("""
            INSERT INTO companies (company_name, industry, stock_code)
            VALUES (?, ?, ?)
        """, (company_name, industry, stock_code))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_or_create_report(self, company_id: int, report_type: str, 
                            report_year: int, filename: str, file_path: str = None) -> int:
        """
        Get report ID or create new report record
        
        Args:
            company_id: Company ID
            report_type: Type of report
            report_year: Year of the report
            filename: Report filename
            file_path: Full path to report file
            
        Returns:
            Report ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Try to get existing report
        cursor.execute("""
            SELECT id FROM reports 
            WHERE company_id = ? AND report_type = ? AND report_year = ?
        """, (company_id, report_type, report_year))
        
        row = cursor.fetchone()
        
        if row:
            return row[0]
        
        # Create new report
        cursor.execute("""
            INSERT INTO reports (company_id, report_type, report_year, filename, file_path)
            VALUES (?, ?, ?, ?, ?)
        """, (company_id, report_type, report_year, filename, file_path))
        
        conn.commit()
        return cursor.lastrowid
    
    def insert_initiatives(self, report_id: int, initiatives: List[Dict]) -> int:
        """
        Insert multiple digital initiatives
        
        Args:
            report_id: Report ID
            initiatives: List of initiative dictionaries
            
        Returns:
            Number of initiatives inserted
        """
        if not initiatives:
            return 0
        
        conn = self.connect()
        cursor = conn.cursor()
        
        inserted = 0
        for init in initiatives:
            try:
                cursor.execute("""
                    INSERT INTO digital_initiatives (
                        report_id, company_name, category, initiative,
                        technology_used, department, year_mentioned,
                        expected_impact, digital_investment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id,
                    init.get('CompanyName', ''),
                    init.get('Category', ''),
                    init.get('Initiative', ''),
                    init.get('TechnologyUsed', ''),
                    init.get('Department', ''),
                    init.get('YearMentioned', ''),
                    init.get('ExpectedImpact', ''),
                    init.get('DigitalInvestment', '')
                ))
                inserted += 1
            except Exception as e:
                logger.error(f"Error inserting initiative: {e}")
                continue
        
        conn.commit()
        logger.info(f"Inserted {inserted} initiatives for report_id {report_id}")
        return inserted
    
    def get_initiatives_by_company(self, company_name: str) -> List[Dict]:
        """Get all initiatives for a company"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM digital_initiatives
            WHERE company_name = ?
            ORDER BY year_mentioned DESC
        """, (company_name,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_initiatives_by_category(self, category: str) -> List[Dict]:
        """Get all initiatives by category"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM digital_initiatives
            WHERE category = ?
            ORDER BY company_name, year_mentioned DESC
        """, (category,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_initiatives_by_year(self, year: str) -> List[Dict]:
        """Get all initiatives for a specific year"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM digital_initiatives
            WHERE year_mentioned = ?
            ORDER BY company_name, category
        """, (year,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_initiatives(self) -> List[Dict]:
        """Get all initiatives from database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM digital_initiatives
            ORDER BY company_name, year_mentioned DESC, category
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        stats['total_companies'] = cursor.fetchone()[0]
        
        # Total reports
        cursor.execute("SELECT COUNT(*) FROM reports")
        stats['total_reports'] = cursor.fetchone()[0]
        
        # Total initiatives
        cursor.execute("SELECT COUNT(*) FROM digital_initiatives")
        stats['total_initiatives'] = cursor.fetchone()[0]
        
        # Initiatives by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM digital_initiatives
            GROUP BY category
            ORDER BY count DESC
        """)
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Initiatives by year
        cursor.execute("""
            SELECT year_mentioned, COUNT(*) as count
            FROM digital_initiatives
            WHERE year_mentioned != ''
            GROUP BY year_mentioned
            ORDER BY year_mentioned DESC
        """)
        stats['by_year'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Companies with most initiatives
        cursor.execute("""
            SELECT company_name, COUNT(*) as count
            FROM digital_initiatives
            GROUP BY company_name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_companies'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        return stats
    
    def export_to_json(self, output_path: str):
        """Export all data to JSON file"""
        data = {
            'initiatives': self.get_all_initiatives(),
            'statistics': self.get_statistics(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported database to {output_path}")


if __name__ == "__main__":
    # Test the database
    db = DatabaseManager(db_path="../database/ide_index.db")
    
    # Test company creation
    company_id = db.get_or_create_company("Test Company", "Technology", "TEST")
    print(f"Company ID: {company_id}")
    
    # Test report creation
    report_id = db.get_or_create_report(
        company_id, "Annual Report", 2023, "test_report.pdf"
    )
    print(f"Report ID: {report_id}")
    
    # Test initiative insertion
    test_initiatives = [
        {
            "CompanyName": "Test Company",
            "Category": "Digital Infrastructure",
            "Initiative": "Cloud migration to AWS",
            "TechnologyUsed": "Amazon Web Services",
            "Department": "IT",
            "YearMentioned": "2023",
            "ExpectedImpact": "30% cost reduction",
            "DigitalInvestment": "RM 2M"
        }
    ]
    
    db.insert_initiatives(report_id, test_initiatives)
    
    # Get statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(json.dumps(stats, indent=2))
    
    db.close()
