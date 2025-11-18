"""
Example: Export to Excel with Multiple Sheets
Creates a comprehensive Excel report with multiple analysis sheets
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from config import Config
import pandas as pd


def create_excel_report(output_file: str = "outputs/ide_report.xlsx"):
    """Create comprehensive Excel report"""
    
    print("Creating Excel report...")
    
    db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
    
    try:
        # Get all data
        initiatives = db.get_all_initiatives()
        stats = db.get_statistics()
        
        if not initiatives:
            print("No data to export")
            return
        
        # Create main dataframe
        df = pd.DataFrame(initiatives)
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Sheet 1: All Initiatives
            df_clean = df[[
                'company_name', 'category', 'initiative', 'technology_used',
                'department', 'year_mentioned', 'expected_impact', 'digital_investment'
            ]]
            df_clean.to_excel(writer, sheet_name='All Initiatives', index=False)
            
            # Sheet 2: Summary by Company
            company_summary = df.groupby('company_name').agg({
                'id': 'count',
                'category': lambda x: x.value_counts().to_dict()
            }).rename(columns={'id': 'Total Initiatives'})
            company_summary.to_excel(writer, sheet_name='By Company')
            
            # Sheet 3: Summary by Category
            category_summary = df.groupby('category').agg({
                'id': 'count',
                'company_name': lambda x: ', '.join(x.unique())
            }).rename(columns={
                'id': 'Total Initiatives',
                'company_name': 'Companies'
            })
            category_summary.to_excel(writer, sheet_name='By Category')
            
            # Sheet 4: Summary by Year
            year_summary = df.groupby('year_mentioned').agg({
                'id': 'count',
                'category': lambda x: x.value_counts().to_dict()
            }).rename(columns={'id': 'Total Initiatives'})
            year_summary.to_excel(writer, sheet_name='By Year')
            
            # Sheet 5: Technology Analysis
            tech_df = df[df['technology_used'].notna()][['company_name', 'technology_used', 'category']]
            tech_df.to_excel(writer, sheet_name='Technologies', index=False)
            
            # Sheet 6: Investment Data
            investment_df = df[df['digital_investment'].notna() & (df['digital_investment'] != '')][
                ['company_name', 'initiative', 'digital_investment', 'year_mentioned']
            ]
            if len(investment_df) > 0:
                investment_df.to_excel(writer, sheet_name='Investments', index=False)
            
            # Sheet 7: Statistics
            stats_df = pd.DataFrame([
                ['Total Companies', stats['total_companies']],
                ['Total Reports', stats['total_reports']],
                ['Total Initiatives', stats['total_initiatives']]
            ], columns=['Metric', 'Value'])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"✓ Excel report created: {output_file}")
        print(f"  Sheets: All Initiatives, By Company, By Category, By Year, Technologies, Statistics")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create Excel report")
    parser.add_argument(
        '--output',
        default='outputs/ide_report.xlsx',
        help='Output Excel file path'
    )
    
    args = parser.parse_args()
    
    # Install openpyxl if needed
    try:
        import openpyxl
    except ImportError:
        print("Installing openpyxl...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'openpyxl'])
    
    create_excel_report(args.output)
