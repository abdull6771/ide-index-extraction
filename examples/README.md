# Examples Directory

This folder contains example scripts demonstrating various use cases and advanced features of the IDE Index extraction system.

## Available Examples

### 1. Custom Analysis (`custom_analysis.py`)

Performs advanced analysis on extracted data:

- Technology trend analysis
- Investment pattern analysis
- Department distribution
- Impact statement analysis

**Usage:**

```bash
python examples/custom_analysis.py
```

**Features:**

- Identifies most mentioned technologies
- Analyzes investment amounts
- Shows which departments drive digital transformation
- Evaluates impact statements

---

### 2. Export to Excel (`export_to_excel.py`)

Creates a comprehensive Excel report with multiple sheets.

**Usage:**

```bash
python examples/export_to_excel.py
python examples/export_to_excel.py --output my_report.xlsx
```

**Output Sheets:**

- All Initiatives - Complete data
- By Company - Summary per company
- By Category - Summary per category
- By Year - Trend analysis
- Technologies - Technology catalog
- Investments - Investment data
- Statistics - Overall statistics

**Requirements:**

```bash
pip install openpyxl
```

---

### 3. Process Single PDF (`process_single_pdf.py`)

Process a single PDF file without running the full pipeline.

**Usage:**

```bash
python examples/process_single_pdf.py data/DNeX-Annual-Report-2024.pdf
python examples/process_single_pdf.py path/to/report.pdf --max-chunks 10
```

**Features:**

- Process one PDF at a time
- Preview results before saving to database
- Useful for testing extraction quality
- Optional database save

---

## Creating Your Own Examples

You can create custom analysis scripts by importing the necessary modules:

```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from config import Config
import pandas as pd

# Your custom analysis
db = DatabaseManager(str(Config.DATABASE_PATH))
initiatives = db.get_all_initiatives()
df = pd.DataFrame(initiatives)

# Your analysis code here...

db.close()
```

## Common Tasks

### Analyze Specific Company

```python
from database import DatabaseManager
from config import Config

db = DatabaseManager(str(Config.DATABASE_PATH))
dnex_initiatives = db.get_initiatives_by_company("DNeX")

for init in dnex_initiatives:
    print(f"{init['category']}: {init['initiative']}")

db.close()
```

### Find All Cloud Initiatives

```python
from database import DatabaseManager
from config import Config
import pandas as pd

db = DatabaseManager(str(Config.DATABASE_PATH))
all_init = db.get_all_initiatives()
df = pd.DataFrame(all_init)

# Filter for cloud-related initiatives
cloud = df[df['technology_used'].str.contains('cloud|aws|azure|gcp', case=False, na=False)]

print(f"Found {len(cloud)} cloud initiatives")
for _, row in cloud.iterrows():
    print(f"{row['company_name']}: {row['technology_used']}")

db.close()
```

### Calculate Statistics

```python
from database import DatabaseManager
from config import Config

db = DatabaseManager(str(Config.DATABASE_PATH))
stats = db.get_statistics()

print(f"Total Companies: {stats['total_companies']}")
print(f"Total Initiatives: {stats['total_initiatives']}")
print("\nBy Category:")
for cat, count in stats['by_category'].items():
    print(f"  {cat}: {count}")

db.close()
```

## Tips

1. **Always close the database connection** when done
2. **Use pandas** for complex data analysis
3. **Test with max_chunks** when developing to save API costs
4. **Export results** to CSV/Excel for sharing with stakeholders
5. **Check Config** for paths and settings

## Need Help?

- Review the main README.md for core concepts
- Check src/ files for available functions
- See COMMANDS.md for command reference
- Refer to QUICKSTART.md for basic usage

---

**Happy analyzing! 📊**
