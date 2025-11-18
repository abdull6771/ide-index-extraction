# Islamic Digital Economy (IDE) Index

## Automated Digital Transformation Extraction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**Automated extraction of digital transformation initiatives from Malaysian corporate reports**

</div>

---

## 🎯 Project Overview

This system automates the extraction of digital transformation initiatives from publicly available corporate reports of Malaysian listed companies, contributing to the Islamic Digital Economy (IDE) Index.

### Key Features

- ✅ **Automated PDF Text Extraction** - Extracts text from Annual Reports, Corporate Governance Reports, and Sustainability Reports
- ✅ **AI-Powered Analysis** - Uses OpenAI's GPT models to identify and extract digital initiatives
- ✅ **Structured Data Storage** - Stores initiatives in SQLite database with proper schema
- ✅ **Multi-Year Support** - Processes reports from 2022, 2023, 2024, and 2025
- ✅ **JSON Export** - Exports data in structured JSON format for further analysis
- ✅ **Category Classification** - Automatically categorizes initiatives into 5 key areas

### Digital Transformation Categories

1. **Digital Infrastructure** - ERP systems, cloud migration, IT upgrades, digital tools
2. **AI & Automation** - AI/ML, analytics, RPA, blockchain, IoT
3. **Cybersecurity** - IT security, data protection, governance, compliance
4. **Customer Experience** - E-commerce, mobile platforms, chatbots, digital marketing
5. **ESG Tech** - Green IT, sustainability tech, social/environmental platforms

---

## 📁 Project Structure

```
final/
├── data/                           # PDF files directory
│   ├── DNeX - Annual Report 2024.pdf
│   ├── DNeX - Corporate Governance Report 2024.pdf
│   ├── Genetec_Annual Report 2024.pdf
│   └── ...
├── src/                            # Source code
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── pdf_extractor.py            # PDF text extraction
│   ├── llm_extractor.py            # LLM-based extraction
│   ├── database.py                 # Database management
│   ├── main.py                     # Main pipeline orchestrator
│   └── query.py                    # Query and analysis tools
├── database/                       # SQLite database
│   └── ide_index.db
├── outputs/                        # JSON output files
│   ├── all_initiatives_*.json
│   └── database_export_*.json
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- PDF files (Annual Reports, CG Reports, or Sustainability Reports)

### Installation

1. **Clone or navigate to the project directory**

```bash
cd "/Users/mac/Documents/🧠/final"
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### File Naming Convention

Place your PDF files in the `data/` folder with the following naming convention:

```
CompanyName - Report Type YYYY.pdf
CompanyName_Report Type_YYYY.pdf
```

**Examples:**

```
DNeX - Annual Report 2024.pdf
Genetec_Corporate Governance Report 2023.pdf
TechCorp - Sustainability Report 2024.pdf
```

---

## 💻 Usage

### Running the Full Pipeline

To process all PDF files and extract digital transformation initiatives:

```bash
python src/main.py
```

This will:

1. Extract text from all PDFs in the `data/` folder
2. Analyze text using OpenAI's GPT model
3. Extract structured digital initiatives
4. Store results in SQLite database
5. Generate JSON output files in `outputs/` folder

### Command Line Options

```bash
# Process only first 10 chunks per document (for testing)
python src/main.py --max-chunks 10

# Skip JSON file generation
python src/main.py --no-json

# Combine options
python src/main.py --max-chunks 5 --no-json
```

---

## 🔍 Querying Data

Use the `query.py` script to analyze extracted data:

### View Statistics

```bash
python src/query.py stats
```

Output:

```
Total Companies: 5
Total Reports: 12
Total Initiatives: 47

Initiatives by Category:
  Digital Infrastructure: 15
  AI & Automation: 12
  Cybersecurity: 8
  Customer Experience: 7
  ESG Tech: 5
```

### List All Companies

```bash
python src/query.py companies
```

### Query by Company

```bash
python src/query.py company "DNeX"
```

### Query by Category

```bash
python src/query.py category "AI & Automation"
```

### Query by Year

```bash
python src/query.py year 2024
```

### Export to CSV

```bash
python src/query.py export outputs/initiatives.csv
```

---

## 📊 Output Format

### JSON Structure

Each extracted initiative follows this structure:

```json
{
  "CompanyName": "DNeX",
  "Category": "Digital Infrastructure",
  "Initiative": "Migrated enterprise ERP system to SAP S/4HANA Cloud",
  "TechnologyUsed": "SAP S/4HANA Cloud",
  "Department": "IT Department",
  "YearMentioned": "2024",
  "ExpectedImpact": "30% improvement in operational efficiency",
  "DigitalInvestment": "RM 5.2 million",
  "source_file": "DNeX - Annual Report 2024.pdf",
  "report_type": "Annual Report"
}
```

### Database Schema

**Companies Table:**

- `id` - Primary key
- `company_name` - Company name
- `industry` - Industry sector
- `stock_code` - Stock exchange code

**Reports Table:**

- `id` - Primary key
- `company_id` - Foreign key to companies
- `report_type` - Type of report
- `report_year` - Year of the report
- `filename` - PDF filename
- `file_path` - Full path to file

**Digital Initiatives Table:**

- `id` - Primary key
- `report_id` - Foreign key to reports
- `company_name` - Company name
- `category` - Digital transformation category
- `initiative` - Description of initiative
- `technology_used` - Technology/platform used
- `department` - Implementing department
- `year_mentioned` - Year mentioned
- `expected_impact` - Expected outcomes
- `digital_investment` - Investment amount

---

## ⚙️ Configuration

Edit `src/config.py` or use environment variables:

| Variable                  | Default       | Description                    |
| ------------------------- | ------------- | ------------------------------ |
| `OPENAI_API_KEY`          | -             | Your OpenAI API key (required) |
| `OPENAI_MODEL`            | `gpt-4o-mini` | GPT model to use               |
| `CHUNK_SIZE`              | `3000`        | Characters per text chunk      |
| `CHUNK_OVERLAP`           | `500`         | Overlap between chunks         |
| `MAX_CHUNKS_PER_DOCUMENT` | `0`           | Max chunks per doc (0 = all)   |

### Available Models

- `gpt-4o-mini` - Cost-effective, fast (recommended)
- `gpt-4o` - Most capable, higher cost
- `gpt-3.5-turbo` - Fastest, lowest cost

---

## 📈 Cost Estimation

Based on OpenAI pricing (as of 2024):

**GPT-4o-mini pricing:**

- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Example:**

- 100-page PDF ≈ 50,000 words ≈ 67,000 tokens
- Processing cost: ~$0.01-0.02 per document

**Total for 10 documents:** ~$0.10-0.20

---

## 🛠️ Development

### Running Tests

```bash
# Test PDF extraction
python src/pdf_extractor.py

# Test LLM extraction
python src/llm_extractor.py

# Test database
python src/database.py

# Test configuration
python src/config.py
```

### Adding New Features

The codebase is modular and easy to extend:

- **New extraction patterns:** Modify `llm_extractor.py`
- **New report types:** Update `pdf_extractor.py`
- **New database queries:** Extend `database.py`
- **New analysis tools:** Add to `query.py`

---

## 📝 Examples

### Example 1: Quick Start

```bash
# 1. Add your PDF files to data/ folder
# 2. Set up your API key
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run the pipeline
python src/main.py

# 4. View results
python src/query.py stats
```

### Example 2: Test Run (Limited Processing)

```bash
# Process only 5 chunks per document for testing
python src/main.py --max-chunks 5
```

### Example 3: Export and Analyze

```bash
# Export to CSV for Excel analysis
python src/query.py export outputs/initiatives.csv

# Query specific company
python src/query.py company "Genetec"

# Check 2024 initiatives
python src/query.py year 2024
```

---

## 🔐 Security & Privacy

- **API Keys:** Never commit `.env` file to version control
- **Data Privacy:** All processing happens locally; only text chunks sent to OpenAI API
- **Database:** SQLite database stored locally in `database/` folder
- **PDF Files:** Keep sensitive reports secure; system only reads, never modifies

---

## 🐛 Troubleshooting

### Common Issues

**1. "OPENAI_API_KEY is not set"**

```bash
# Solution: Create .env file with your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

**2. "No PDFs found or processed"**

```bash
# Solution: Check that PDF files are in data/ folder
ls data/*.pdf
```

**3. "Error reading PDF"**

```bash
# Solution: Ensure PDF is not encrypted or corrupted
# Try opening it manually first
```

**4. Rate limit errors**

```bash
# Solution: The system has built-in delays
# If still occurring, reduce --max-chunks or use gpt-3.5-turbo
```

---

## 📊 Dashboard Development (Future)

The extracted data is ready for dashboard visualization:

### Recommended Tools:

- **Streamlit** - Python-based dashboards
- **Plotly Dash** - Interactive visualizations
- **Power BI** - Connect to SQLite database
- **Tableau** - Import CSV exports

### Example Dashboard Features:

- Digital maturity scores by company
- Year-over-year investment trends
- Technology adoption heatmaps
- Category distribution charts
- Investment vs. impact analysis

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add support for scanned PDFs (OCR)
- [ ] Implement vector storage (Pinecone/ChromaDB)
- [ ] Build Streamlit dashboard
- [ ] Add more extraction categories
- [ ] Improve initiative deduplication
- [ ] Add multilingual support (Bahasa Malaysia)

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Support

For questions or issues:

1. Check the troubleshooting section above
2. Review the code comments in `src/` files
3. Test individual modules using the test commands

---

## 🎓 Citation

If you use this system in research, please cite:

```
Islamic Digital Economy (IDE) Index - Digital Transformation Extraction System
Automated extraction of digital transformation initiatives from Malaysian corporate reports
2024
```

---

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

<div align="center">

**Built with ❤️ for the Islamic Digital Economy Initiative**

[⬆ Back to Top](#islamic-digital-economy-ide-index)

</div>
