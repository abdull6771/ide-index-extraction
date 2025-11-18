"""
Example: Custom Analysis Script
Analyze specific patterns in digital transformation initiatives
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from config import Config
import pandas as pd


def analyze_technology_trends(db: DatabaseManager):
    """Analyze which technologies are most mentioned"""
    initiatives = db.get_all_initiatives()
    df = pd.DataFrame(initiatives)
    
    print("\n" + "="*60)
    print("TECHNOLOGY TREND ANALYSIS")
    print("="*60)
    
    # Extract technology keywords
    tech_keywords = {
        'Cloud': ['cloud', 'aws', 'azure', 'gcp'],
        'AI/ML': ['ai', 'machine learning', 'ml', 'artificial intelligence'],
        'ERP': ['erp', 'sap', 'oracle', 's/4hana'],
        'Data Analytics': ['analytics', 'big data', 'data warehouse', 'bi'],
        'Automation': ['automation', 'rpa', 'robotic process'],
        'Mobile': ['mobile', 'app', 'ios', 'android'],
        'IoT': ['iot', 'internet of things', 'sensors'],
        'Blockchain': ['blockchain', 'distributed ledger'],
        'Cybersecurity': ['security', 'encryption', 'firewall', 'authentication']
    }
    
    results = {}
    for tech_name, keywords in tech_keywords.items():
        count = 0
        for _, row in df.iterrows():
            text = f"{row['initiative']} {row['technology_used']}".lower()
            if any(kw in text for kw in keywords):
                count += 1
        results[tech_name] = count
    
    # Sort by count
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTechnology Adoption:")
    for tech, count in sorted_results:
        if count > 0:
            print(f"  {tech}: {count} initiatives")
    
    return results


def analyze_investment_patterns(db: DatabaseManager):
    """Analyze investment amounts mentioned"""
    initiatives = db.get_all_initiatives()
    df = pd.DataFrame(initiatives)
    
    print("\n" + "="*60)
    print("INVESTMENT ANALYSIS")
    print("="*60)
    
    # Filter initiatives with investment amounts
    with_investment = df[df['digital_investment'].notna() & (df['digital_investment'] != '')]
    
    print(f"\nTotal initiatives: {len(df)}")
    print(f"With investment data: {len(with_investment)}")
    print(f"Percentage: {len(with_investment)/len(df)*100:.1f}%")
    
    if len(with_investment) > 0:
        print("\nInvestments mentioned:")
        for _, row in with_investment.iterrows():
            print(f"  {row['company_name']}: {row['digital_investment']}")
            print(f"    Initiative: {row['initiative'][:80]}...")


def analyze_department_distribution(db: DatabaseManager):
    """Analyze which departments are driving digital transformation"""
    initiatives = db.get_all_initiatives()
    df = pd.DataFrame(initiatives)
    
    print("\n" + "="*60)
    print("DEPARTMENT ANALYSIS")
    print("="*60)
    
    # Filter initiatives with department info
    with_dept = df[df['department'].notna() & (df['department'] != '')]
    
    if len(with_dept) > 0:
        dept_counts = with_dept['department'].value_counts()
        print("\nInitiatives by Department:")
        for dept, count in dept_counts.items():
            print(f"  {dept}: {count}")
    else:
        print("\nNo department information available")


def analyze_impact_statements(db: DatabaseManager):
    """Analyze expected impact patterns"""
    initiatives = db.get_all_initiatives()
    df = pd.DataFrame(initiatives)
    
    print("\n" + "="*60)
    print("IMPACT ANALYSIS")
    print("="*60)
    
    # Filter initiatives with impact statements
    with_impact = df[df['expected_impact'].notna() & (df['expected_impact'] != '')]
    
    print(f"\nTotal initiatives: {len(df)}")
    print(f"With impact data: {len(with_impact)}")
    print(f"Percentage: {len(with_impact)/len(df)*100:.1f}%")
    
    # Look for quantifiable impacts
    quantifiable = with_impact[
        with_impact['expected_impact'].str.contains('%|million|thousand|increase|decrease|improve', 
                                                    case=False, na=False)
    ]
    
    print(f"With quantifiable impact: {len(quantifiable)}")
    
    if len(quantifiable) > 0:
        print("\nSample quantifiable impacts:")
        for _, row in quantifiable.head(5).iterrows():
            print(f"\n  Company: {row['company_name']}")
            print(f"  Category: {row['category']}")
            print(f"  Impact: {row['expected_impact']}")


def main():
    """Run custom analysis"""
    print("="*60)
    print("CUSTOM DIGITAL TRANSFORMATION ANALYSIS")
    print("="*60)
    
    db = DatabaseManager(db_path=str(Config.DATABASE_PATH))
    
    try:
        analyze_technology_trends(db)
        analyze_investment_patterns(db)
        analyze_department_distribution(db)
        analyze_impact_statements(db)
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
