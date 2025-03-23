# State Contract Generator: Automated Medical Transportation Contract Creation System

The State Contract Generator is a Python-based system that automates the generation of state-specific medical transportation service contracts. It leverages Amazon Bedrock for content generation and produces standardized HTML and PDF contracts with customized terms, rates, and compliance requirements for different U.S. states.

This system streamlines the contract creation process for healthcare agencies and transportation providers by automatically generating comprehensive contracts that include state-specific regulations, service areas, rate schedules, and performance standards. The generated contracts maintain consistency while accommodating variations in state requirements, provider capabilities, and service terms.

## Repository Structure
```
.
├── contracts/                      # Generated contract files by state
│   ├── Transportation_Contract_*.html  # State-specific contract documents
├── contracts.py                    # Core contract generation logic using Bedrock
└── contracts2.py                   # Additional contract generation utilities
```

## Usage Instructions
### Prerequisites
- Python 3.7+
- AWS account with Bedrock access
- boto3
- reportlab
- pdfkit
- wkhtmltopdf

### Installation
1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required Python packages:
```bash
pip install boto3 reportlab pdfkit
```

3. Install wkhtmltopdf:
```bash
# MacOS
brew install wkhtmltopdf

# Linux
sudo apt-get install wkhtmltopdf

# Windows
# Download installer from https://wkhtmltopdf.org/downloads.html
```

4. Configure AWS credentials:
```bash
aws configure
```

### Quick Start
1. Create a state configuration file:
```python
state_info = {
    "state": "Virginia",
    "health_agency": "Department of Medical Assistance Services",
    "agency_city": "Richmond",
    "provider_name": "Commonwealth Medical Transport",
    "provider_city": "Virginia Beach",
    "service_regions": ["Fairfax County", "Virginia Beach City", "Richmond City"],
    "contract_date": "2025-03-02",
    "provider_details": {
        "term": "3 years",
        "fleet_size": 50,
        "operating_hours": "24/7",
        "driver_count": 120
    }
}
```

2. Generate a contract:
```python
from contracts import StateContractGenerator, ContractPDF

# Initialize generator
generator = StateContractGenerator(state_info)

# Generate contract content
contract_content = generator.create_contract()
rate_schedule = generator.generate_rate_schedule()
service_areas = generator.generate_service_areas()
performance_standards = generator.generate_performance_standards()

# Create PDF
pdf = ContractPDF("contract.pdf", "Transportation Services Contract")
pdf.create_document(contract_content, rate_schedule, service_areas, performance_standards)
```

### More Detailed Examples
1. Generating a contract with custom rate schedules:
```python
# Generate custom rate schedule
rate_schedule = generator.generate_rate_schedule()
print(rate_schedule)
```

2. Creating service area specifications:
```python
# Generate service area details
service_areas = generator.generate_service_areas()
print(service_areas)
```

### Troubleshooting
1. Bedrock API Connection Issues
- Error: "Could not connect to Bedrock service"
  - Verify AWS credentials are properly configured
  - Check region settings in boto3 client
  - Ensure proper IAM permissions for Bedrock access

2. PDF Generation Errors
- Error: "wkhtmltopdf not found"
  - Verify wkhtmltopdf is installed and in system PATH
  - Check pdfkit configuration settings
  - Try specifying full path to wkhtmltopdf binary

3. Content Generation Issues
- Error: "Invalid response from Bedrock"
  - Check prompt formatting in generator methods
  - Verify model ID is correct
  - Review response handling in generate_content_with_bedrock method

## Data Flow
The contract generation system follows a structured data flow process that transforms state-specific requirements into standardized contract documents.

```ascii
[State Config] --> [StateContractGenerator] --> [Bedrock API]
       |                    |                        |
       |                    v                        v
       |              [Contract Content] <-- [Generated Text]
       |                    |
       v                    v
[Contract PDF] <-- [Document Assembly]
```

Component interactions:
- StateContractGenerator processes state configuration data
- Bedrock API generates contract content based on prompts
- Contract content is formatted into HTML sections
- PDF generation combines content with styling and layout
- Final document includes contract terms, rates, and requirements
- Error handling occurs at each transformation step
- Data validation ensures complete contract generation