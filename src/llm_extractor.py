"""
LLM-based Digital Transformation Initiative Extractor
Uses OpenAI/LangChain to extract structured digital initiatives from corporate reports
"""

import json
import os
from typing import List, Dict, Optional
import logging
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DigitalInitiative(BaseModel):
    """Pydantic model for a digital transformation initiative"""
    
    CompanyName: str = Field(description="Name of the company")
    Category: str = Field(
        description="Category: Digital Infrastructure, AI & Automation, Cybersecurity, Customer Experience, or ESG Tech"
    )
    Initiative: str = Field(description="Description of the digital initiative")
    TechnologyUsed: str = Field(description="Specific technology, platform, or system used")
    Department: Optional[str] = Field(description="Department or business unit implementing the initiative", default="")
    YearMentioned: str = Field(description="Year the initiative was mentioned or implemented")
    ExpectedImpact: Optional[str] = Field(description="Expected or actual impact/outcome", default="")
    DigitalInvestment: Optional[str] = Field(description="Investment amount or budget allocated", default="")
    
    @field_validator('Category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [
            'Digital Infrastructure',
            'AI & Automation',
            'Cybersecurity',
            'Customer Experience',
            'ESG Tech'
        ]
        if v and v not in valid_categories:
            # Try to map to closest category
            v_lower = v.lower()
            if any(term in v_lower for term in ['infrastructure', 'erp', 'cloud', 'it upgrade']):
                return 'Digital Infrastructure'
            elif any(term in v_lower for term in ['ai', 'automation', 'analytics', 'rpa', 'blockchain']):
                return 'AI & Automation'
            elif any(term in v_lower for term in ['security', 'cyber', 'protection', 'compliance']):
                return 'Cybersecurity'
            elif any(term in v_lower for term in ['customer', 'ecommerce', 'mobile', 'chatbot']):
                return 'Customer Experience'
            elif any(term in v_lower for term in ['esg', 'sustainability', 'green', 'environment']):
                return 'ESG Tech'
        return v


class DigitalTransformationExtractor:
    """Extracts digital transformation initiatives using LLM"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the extractor
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: OpenAI model to use (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0,
            api_key=self.api_key
        )
        
        # Create the prompt template
        self.prompt_template = self._create_prompt_template()
        
    def _create_prompt_template(self) -> PromptTemplate:
        """Create the extraction prompt template"""
        
        template = """You are a research analyst specializing in digital economy transformation.
Analyze the following excerpt from a company's annual report. Identify and extract all relevant digital transformation efforts under these key areas:

1. Digital Infrastructure – ERP systems, cloud migration, IT upgrades, digital tools
2. AI & Automation – AI/ML, analytics, RPA, blockchain, IoT
3. Cybersecurity – IT security, data protection, governance, compliance
4. Customer Experience – E-commerce, mobile platforms, chatbots, digital marketing
5. ESG Tech – Green IT, sustainability tech, social/environmental platforms

Your task is to extract real initiatives, not generic statements. Focus on what the company *did*, *what tech was used*, and *why*.

IMPORTANT INSTRUCTIONS:
- Only extract SPECIFIC, CONCRETE initiatives with actual implementation details
- Skip generic statements like "we are committed to digital transformation"
- Look for: specific systems named, technologies deployed, projects completed, platforms launched
- Extract technology names, vendor names, system names when mentioned
- Include financial figures if mentioned (investments, budgets, savings)
- If no specific initiatives are found, return an empty JSON array: []

Company Name: {company_name}
Report Year: {year}
Report Type: {report_type}

Return the output as a valid JSON array of objects. Each object should have these fields:
- CompanyName: string
- Category: string (must be one of: "Digital Infrastructure", "AI & Automation", "Cybersecurity", "Customer Experience", "ESG Tech")
- Initiative: string (specific description of what was done)
- TechnologyUsed: string (specific tech, platform, or system)
- Department: string (optional, which department/unit)
- YearMentioned: string (the year, usually {year})
- ExpectedImpact: string (optional, outcomes or benefits)
- DigitalInvestment: string (optional, budget or investment amount)

Text:
{text_chunk}

Return ONLY a valid JSON array, no additional text or explanation:"""

        return PromptTemplate(
            template=template,
            input_variables=["company_name", "year", "report_type", "text_chunk"]
        )
    
    def extract_from_chunk(
        self, 
        text_chunk: str, 
        company_name: str, 
        year: str,
        report_type: str
    ) -> List[Dict]:
        """
        Extract digital initiatives from a single text chunk
        
        Args:
            text_chunk: Text excerpt to analyze
            company_name: Name of the company
            year: Report year
            report_type: Type of report (Annual, CG, Sustainability)
            
        Returns:
            List of extracted initiatives as dictionaries
        """
        try:
            # Format the prompt
            prompt = self.prompt_template.format(
                company_name=company_name,
                year=year,
                report_type=report_type,
                text_chunk=text_chunk
            )
            
            # Call the LLM
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse the JSON
            initiatives = json.loads(response_text)
            
            # Ensure it's a list
            if not isinstance(initiatives, list):
                initiatives = [initiatives]
            
            # Validate and enrich each initiative
            validated_initiatives = []
            for init in initiatives:
                # Ensure company name and year are set
                if not init.get('CompanyName'):
                    init['CompanyName'] = company_name
                if not init.get('YearMentioned'):
                    init['YearMentioned'] = year
                
                validated_initiatives.append(init)
            
            return validated_initiatives
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error extracting from chunk: {e}")
            return []
    
    def extract_from_document(
        self,
        chunks: List[str],
        company_name: str,
        year: str,
        report_type: str,
        max_chunks: Optional[int] = None
    ) -> List[Dict]:
        """
        Extract initiatives from all chunks of a document
        
        Args:
            chunks: List of text chunks
            company_name: Company name
            year: Report year
            report_type: Report type
            max_chunks: Maximum number of chunks to process (None = all)
            
        Returns:
            Consolidated list of all extracted initiatives
        """
        all_initiatives = []
        
        chunks_to_process = chunks if max_chunks is None else chunks[:max_chunks]
        total_chunks = len(chunks_to_process)
        
        logger.info(f"\nProcessing {total_chunks} chunks for {company_name} ({year})")
        
        for i, chunk in enumerate(chunks_to_process, 1):
            logger.info(f"  Processing chunk {i}/{total_chunks}...")
            
            initiatives = self.extract_from_chunk(
                text_chunk=chunk,
                company_name=company_name,
                year=year,
                report_type=report_type
            )
            
            if initiatives:
                logger.info(f"    Found {len(initiatives)} initiative(s)")
                all_initiatives.extend(initiatives)
            
            # Small delay to avoid rate limits
            import time
            time.sleep(0.5)
        
        logger.info(f"Total initiatives extracted: {len(all_initiatives)}")
        
        return all_initiatives
    
    def save_to_json(self, initiatives: List[Dict], output_path: str):
        """Save extracted initiatives to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(initiatives, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(initiatives)} initiatives to {output_path}")


if __name__ == "__main__":
    # Test the extractor
    extractor = DigitalTransformationExtractor()
    
    test_chunk = """
    During 2023, we successfully migrated our entire enterprise resource planning (ERP) 
    system to SAP S/4HANA Cloud, representing a digital investment of RM 5.2 million. 
    This initiative, led by our IT Department, is expected to improve operational 
    efficiency by 30% and provide real-time analytics capabilities across all business units.
    
    We also deployed an AI-powered chatbot on our customer portal, developed using 
    Microsoft Azure Bot Framework. The chatbot handles over 10,000 customer inquiries 
    monthly, reducing response time by 60%.
    """
    
    result = extractor.extract_from_chunk(
        text_chunk=test_chunk,
        company_name="Test Company",
        year="2023",
        report_type="Annual Report"
    )
    
    print(json.dumps(result, indent=2))
