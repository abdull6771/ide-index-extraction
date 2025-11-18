"""
Query and Analysis Script
Query the database and analyze digital transformation initiatives
"""

import sys
import json
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager
from config import Config


def query_by_company(db: DatabaseManager, company_name: str):
    """Query initiatives by company"""
    initiatives = db.get_initiatives_by_company(company_name)
    
    print(f"\n{'='*80}")
    print(f"INITIATIVES FOR: {company_name}")
    print(f"{'='*80}")
    print(f"Total Initiatives: {len(initiatives)}\n")
    
    for init in initiatives:
        print(f"Category: {init['category']}")
        print(f"Year: {init['year_mentioned']}")
        print(f"Initiative: {init['initiative']}")
        print(f"Technology: {init['technology_used']}")
        if init['department']:
            print(f"Department: {init['department']}")
        if init['expected_impact']:
            print(f"Impact: {init['expected_impact']}")
        if init['digital_investment']:
            print(f"Investment: {init['digital_investment']}")
        print("-" * 80)


def query_by_category(db: DatabaseManager, category: str):
    """Query initiatives by category"""
    initiatives = db.get_initiatives_by_category(category)
    
    print(f"\n{'='*80}")
    print(f"INITIATIVES IN CATEGORY: {category}")
    print(f"{'='*80}")
    print(f"Total Initiatives: {len(initiatives)}\n")
    
    # Group by company
    by_company = {}
    for init in initiatives:
        company = init['company_name']
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(init)
    
    for company, inits in by_company.items():
        print(f"\n{company} ({len(inits)} initiatives)")
        print("-" * 80)
        for init in inits:
            print(f"  • {init['initiative']}")
            print(f"    Technology: {init['technology_used']}")
            print(f"    Year: {init['year_mentioned']}")


def query_by_year(db: DatabaseManager, year: str):
    """Query initiatives by year"""
    initiatives = db.get_initiatives_by_year(year)
    
    print(f"\n{'='*80}")
    print(f"INITIATIVES IN YEAR: {year}")
    print(f"{'='*80}")
    print(f"Total Initiatives: {len(initiatives)}\n")
    
    # Group by category
    by_category = {}
    for init in initiatives:
        category = init['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(init)
    
    for category, inits in by_category.items():
        print(f"\n{category} ({len(inits)} initiatives)")
        print("-" * 80)
        for init in inits:
            print(f"  • [{init['company_name']}] {init['initiative']}")


def show_statistics(db: DatabaseManager):
    """Show database statistics"""
    stats = db.get_statistics()
    
    print(f"\n{'='*80}")
    print("DATABASE STATISTICS")
    print(f"{'='*80}\n")
    
    print(f"Total Companies: {stats['total_companies']}")
    print(f"Total Reports: {stats['total_reports']}")
    print(f"Total Initiatives: {stats['total_initiatives']}\n")
    
    print("Initiatives by Category:")
    for category, count in stats['by_category'].items():
        print(f"  {category}: {count}")
    
    print("\nInitiatives by Year:")
    for year, count in sorted(stats['by_year'].items(), reverse=True):
        print(f"  {year}: {count}")
    
    print("\nTop Companies:")
    for company, count in stats['top_companies'].items():
        print(f"  {company}: {count} initiatives")


def list_companies(db: DatabaseManager):
    """List all companies in database"""
    conn = db.connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.company_name, COUNT(DISTINCT r.id) as reports, COUNT(i.id) as initiatives
        FROM companies c
        LEFT JOIN reports r ON c.id = r.company_id
        LEFT JOIN digital_initiatives i ON r.id = i.report_id
        GROUP BY c.company_name
        ORDER BY initiatives DESC
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print("ALL COMPANIES")
    print(f"{'='*80}\n")
    
    for row in rows:
        print(f"{row[0]}")
        print(f"  Reports: {row[1]} | Initiatives: {row[2]}")


def export_to_csv(db: DatabaseManager, output_file: str):
    """Export all initiatives to CSV"""
    import csv
    
    initiatives = db.get_all_initiatives()
    
    if not initiatives:
        print("No initiatives to export")
        return
    
    # Define CSV columns
    fieldnames = [
        'company_name', 'category', 'initiative', 'technology_used',
        'department', 'year_mentioned', 'expected_impact', 'digital_investment'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for init in initiatives:
            row = {k: init.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    print(f"Exported {len(initiatives)} initiatives to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Query digital transformation initiatives")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List companies
    subparsers.add_parser('companies', help='List all companies')
    
    # Query by company
    company_parser = subparsers.add_parser('company', help='Query by company')
    company_parser.add_argument('name', help='Company name')
    
    # Query by category
    category_parser = subparsers.add_parser('category', help='Query by category')
    category_parser.add_argument('name', help='Category name')
    
    # Query by year
    year_parser = subparsers.add_parser('year', help='Query by year')
    year_parser.add_argument('year', help='Year (e.g., 2023)')
    
    # Export to CSV
    export_parser = subparsers.add_parser('export', help='Export to CSV')
    export_parser.add_argument('output', help='Output CSV file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
    
    try:
        if args.command == 'stats':
            show_statistics(db)
        elif args.command == 'companies':
            list_companies(db)
        elif args.command == 'company':
            query_by_company(db, args.name)
        elif args.command == 'category':
            query_by_category(db, args.name)
        elif args.command == 'year':
            query_by_year(db, args.year)
        elif args.command == 'export':
            export_to_csv(db, args.output)
    finally:
        db.close()


if __name__ == "__main__":
    main()
