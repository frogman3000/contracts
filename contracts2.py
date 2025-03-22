import boto3
import json
import os
from datetime import datetime
import pdfkit
from jinja2 import Template
import webbrowser
import sys

# Configure path for wkhtmltopdf based on operating system
if sys.platform.startswith('win'):
    # Windows path (adjust as needed)
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
elif sys.platform.startswith('darwin'):
    # macOS path
    WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'
else:
    # Linux path
    WKHTMLTOPDF_PATH = '/usr/bin/wkhtmltopdf'

# Configure pdfkit with the path
try:
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except Exception as e:
    print(f"Error configuring pdfkit: {str(e)}")
    config = None


# State configurations dictionary
state_configs = {
    "FL": {
        "state": "Florida",
        "state_abbrev": "FL",
        "health_agency": "Florida Department of Health",
        "agency_city": "Tallahassee",
        "provider_name": "SafeRide Transit Solutions",
        "provider_city": "Orlando",
        "service_regions": ["Orange County", "Seminole County", "Osceola County"],
        "contract_date": "March 15, 2024",
        "provider_details": {
            "fleet_size": 50,
            "operating_hours": "24/7",
            "driver_count": 120,
            "term": "2-year contract with 1-year renewal option"
        }
    },
    "TX": {
        "state": "Texas",
        "state_abbrev": "TX",
        "health_agency": "Texas Health and Human Services Commission",
        "agency_city": "Austin",
        "provider_name": "Lone Star Medical Transport",
        "provider_city": "Houston",
        "service_regions": ["Harris County", "Fort Bend County", "Montgomery County"],
        "contract_date": "April 1, 2024",
        "provider_details": {
            "fleet_size": 75,
            "operating_hours": "24/7",
            "driver_count": 180,
            "term": "3-year contract with two 1-year renewal options"
        }
    },
    "CA": {
        "state": "California",
        "state_abbrev": "CA",
        "health_agency": "California Department of Health Care Services",
        "agency_city": "Sacramento",
        "provider_name": "Pacific Coast Medical Transport",
        "provider_city": "Los Angeles",
        "service_regions": ["Los Angeles County", "Orange County", "Ventura County"],
        "contract_date": "May 1, 2024",
        "provider_details": {
            "fleet_size": 100,
            "operating_hours": "24/7",
            "driver_count": 250,
            "term": "4-year contract with one 2-year renewal option"
        }
    },
    "NY": {
        "state": "New York",
        "state_abbrev": "NY",
        "health_agency": "New York State Department of Health",
        "agency_city": "Albany",
        "provider_name": "Empire State Medical Transport",
        "provider_city": "Buffalo",
        "service_regions": ["Erie County", "Niagara County", "Monroe County"],
        "contract_date": "June 1, 2024",
        "provider_details": {
            "fleet_size": 85,
            "operating_hours": "24/7",
            "driver_count": 200,
            "term": "3-year contract with one 1-year renewal option"
        }
    },
    "IL": {
        "state": "Illinois",
        "state_abbrev": "IL",
        "health_agency": "Illinois Department of Healthcare and Family Services",
        "agency_city": "Springfield",
        "provider_name": "Midwest Healthcare Transit",
        "provider_city": "Chicago",
        "service_regions": ["Cook County", "DuPage County", "Lake County"],
        "contract_date": "July 15, 2024",
        "provider_details": {
            "fleet_size": 60,
            "operating_hours": "24/7",
            "driver_count": 145,
            "term": "2-year contract with two 1-year renewal options"
        }
    },
    "PA": {
        "state": "Pennsylvania",
        "state_abbrev": "PA",
        "health_agency": "Pennsylvania Department of Human Services",
        "agency_city": "Harrisburg",
        "provider_name": "Keystone Medical Transit",
        "provider_city": "Philadelphia",
        "service_regions": ["Philadelphia County", "Montgomery County", "Bucks County"],
        "contract_date": "August 1, 2024",
        "provider_details": {
            "fleet_size": 70,
            "operating_hours": "24/7",
            "driver_count": 165,
            "term": "5-year contract with no renewal option"
        }
    },
    "OH": {
        "state": "Ohio",
        "state_abbrev": "OH",
        "health_agency": "Ohio Department of Medicaid",
        "agency_city": "Columbus",
        "provider_name": "Buckeye Medical Transport",
        "provider_city": "Cleveland",
        "service_regions": ["Cuyahoga County", "Franklin County", "Hamilton County"],
        "contract_date": "September 15, 2024",
        "provider_details": {
            "fleet_size": 55,
            "operating_hours": "24/7",
            "driver_count": 130,
            "term": "3-year contract with one 3-year renewal option"
        }
    },
    "MI": {
        "state": "Michigan",
        "state_abbrev": "MI",
        "health_agency": "Michigan Department of Health and Human Services",
        "agency_city": "Lansing",
        "provider_name": "Great Lakes Medical Transport",
        "provider_city": "Detroit",
        "service_regions": ["Wayne County", "Oakland County", "Macomb County"],
        "contract_date": "October 1, 2024",
        "provider_details": {
            "fleet_size": 65,
            "operating_hours": "24/7",
            "driver_count": 155,
            "term": "2-year contract with three 1-year renewal options"
        }
    },
    "GA": {
        "state": "Georgia",
        "state_abbrev": "GA",
        "health_agency": "Georgia Department of Community Health",
        "agency_city": "Atlanta",
        "provider_name": "Peach State Medical Transit",
        "provider_city": "Savannah",
        "service_regions": ["Fulton County", "DeKalb County", "Cobb County"],
        "contract_date": "November 15, 2024",
        "provider_details": {
            "fleet_size": 45,
            "operating_hours": "24/7",
            "driver_count": 110,
            "term": "4-year contract with two 1-year renewal options"
        }
    },
    "NC": {
        "state": "North Carolina",
        "state_abbrev": "NC",
        "health_agency": "North Carolina Department of Health and Human Services",
        "agency_city": "Raleigh",
        "provider_name": "Carolina Care Transit",
        "provider_city": "Charlotte",
        "service_regions": ["Mecklenburg County", "Wake County", "Durham County"],
        "contract_date": "December 1, 2024",
        "provider_details": {
            "fleet_size": 40,
            "operating_hours": "24/7",
            "driver_count": 95,
            "term": "1-year contract with four 1-year renewal options"
        }
    },
    "VA": {
        "state": "Virginia",
        "state_abbrev": "VA",
        "health_agency": "Virginia Department of Medical Assistance Services",
        "agency_city": "Richmond",
        "provider_name": "Commonwealth Medical Transport",
        "provider_city": "Virginia Beach",
        "service_regions": ["Fairfax County", "Virginia Beach City", "Richmond City"],
        "contract_date": "January 15, 2025",
        "provider_details": {
            "fleet_size": 50,
            "operating_hours": "24/7",
            "driver_count": 120,
            "term": "3-year contract with two 1-year renewal options"
        }
    },
    "WA": {
        "state": "Washington",
        "state_abbrev": "WA",
        "health_agency": "Washington State Health Care Authority",
        "agency_city": "Olympia",
        "provider_name": "Evergreen Medical Transport",
        "provider_city": "Seattle",
        "service_regions": ["King County", "Pierce County", "Snohomish County"],
        "contract_date": "February 1, 2025",
        "provider_details": {
            "fleet_size": 45,
            "operating_hours": "24/7",
            "driver_count": 105,
            "term": "2-year contract with two 2-year renewal options"
        }
    },
    "MA": {
        "state": "Massachusetts",
        "state_abbrev": "MA",
        "health_agency": "Massachusetts Department of Public Health",
        "agency_city": "Boston",
        "provider_name": "New England Medical Transport Services",
        "provider_city": "Worcester",
        "service_regions": ["Suffolk County", "Middlesex County", "Essex County"],
        "contract_date": "March 1, 2025",
        "provider_details": {
            "fleet_size": 35,
            "operating_hours": "24/7",
            "driver_count": 85,
            "term": "5-year contract with one 2-year renewal option"
        }
    }
}


class StateContractGenerator:
    def __init__(self, state_info):
        self.state = state_info['state']
        self.health_agency = state_info['health_agency']
        self.agency_city = state_info['agency_city']
        self.provider_name = state_info['provider_name']
        self.provider_city = state_info['provider_city']
        self.service_regions = state_info['service_regions']
        self.contract_date = state_info['contract_date']
        self.provider_details = state_info['provider_details']

    def generate_content_with_bedrock(self, prompt):
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1"
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "temperature": 0.7
        })

        try:
            response = bedrock_runtime.invoke_model(
                #modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                contentType="application/json",
                body=body
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body.get("content")[0].get("text")

        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return None

    def create_contract(self):
        prompt = f"""Create a detailed transportation services contract between {self.health_agency} and {self.provider_name}.
        Format the response as HTML with proper sections and headings.
        
        Include these key details:
        - Contract date: {self.contract_date}
        - Agency location: {self.agency_city}, {self.state}
        - Provider location: {self.provider_city}, {self.state}
        - Term: {self.provider_details['term']}
        - Service areas: {', '.join(self.service_regions)}
        - Fleet size: {self.provider_details['fleet_size']} vehicles
        - Operating hours: {self.provider_details['operating_hours']}
        - Driver count: {self.provider_details['driver_count']}

        Include standard sections:
        1. Parties and Purpose
        2. Definitions
        3. Term and Renewal
        4. Scope of Services
        5. Provider Responsibilities
        6. Agency Responsibilities
        7. Compensation
        8. Compliance and Reporting
        9. Insurance and Liability
        10. Termination
        11. General Provisions

        Format as clean HTML with proper headings and paragraphs.
        Make all details specific to {self.state} and medical transportation."""

        return self.generate_content_with_bedrock(prompt)

    def generate_rate_schedule(self):
        prompt = f"""Create an HTML table showing transportation rates for {self.provider_name} in {self.state}.
        
        Include these service types:
        - Standard Vehicle Transport
        - Wheelchair Accessible Vehicle
        - Stretcher Transport
        - Bariatric Transport
        - Group Transport

        Table columns:
        - Service Type
        - Base Rate
        - Mileage Rate
        - Wait Time Rate
        - After Hours Rate
        - Weekend/Holiday Rate

        Return a properly formatted HTML table with realistic rates for {self.state}.
        Include <thead> and <tbody> tags, and proper styling classes."""

        return self.generate_content_with_bedrock(prompt)

    def generate_service_areas(self):
        prompt = f"""Create an HTML table showing service area details for {self.provider_name} in {self.state}.
        
        Include these zones:
        - Primary Urban Areas
        - Suburban Regions
        - Rural Coverage
        - Special Service Areas

        Table columns:
        - Service Zone
        - Counties Covered
        - Response Time
        - Population Served
        - Facilities Covered
        - Special Conditions

        Return a properly formatted HTML table specific to {self.state}.
        Include <thead> and <tbody> tags, and proper styling classes."""

        return self.generate_content_with_bedrock(prompt)

    def generate_performance_standards(self):
        prompt = f"""Create an HTML table showing performance standards for {self.provider_name} in {self.state}.
        
        Include these categories:
        - On-time Performance
        - Vehicle Maintenance
        - Driver Qualifications
        - Safety Metrics
        - Complaint Resolution

        Table columns:
        - Performance Category
        - Standard Description
        - Measurement Method
        - Minimum Target
        - Non-Compliance Penalty

        Return a properly formatted HTML table with realistic standards.
        Include <thead> and <tbody> tags, and proper styling classes."""

        return self.generate_content_with_bedrock(prompt)

class ContractHTML:
    def __init__(self, title):
        self.title = title
        self.html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 20px;
                }
                .contract-date {
                    text-align: right;
                    margin: 20px 0;
                    font-style: italic;
                    color: #666;
                }
                h1 {
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                h2 {
                    color: #34495e;
                    font-size: 20px;
                    margin-top: 30px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                h3 {
                    color: #445566;
                    font-size: 18px;
                    margin-top: 25px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: #fff;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                th {
                    background-color: #34495e;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                td {
                    padding: 10px;
                    border: 1px solid #ddd;
                    font-size: 13px;
                    vertical-align: top;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .section {
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .footer {
                    margin-top: 50px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                }
                p {
                    margin-bottom: 15px;
                    text-align: justify;
                }
                ul, ol {
                    margin-bottom: 15px;
                    padding-left: 20px;
                }
                li {
                    margin-bottom: 5px;
                }
                @media print {
                    body {
                        margin: 25mm;
                    }
                    table {
                        page-break-inside: avoid;
                    }
                    h2 {
                        page-break-before: always;
                    }
                    .footer {
                        position: fixed;
                        bottom: 0;
                        width: 100%;
                    }
                    @page {
                        margin: 25mm;
                        @bottom-center {
                            content: "Page " counter(page) " of " counter(pages);
                        }
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <div class="contract-date">{{ date }}</div>
            </div>

            <div class="content">
                {{ contract_content }}
            </div>

            <div class="section">
                <h2>Attachment A: Rate Schedule</h2>
                {{ rate_schedule }}
            </div>

            <div class="section">
                <h2>Attachment B: Service Areas</h2>
                {{ service_areas }}
            </div>

            <div class="section">
                <h2>Attachment C: Performance Standards</h2>
                {{ performance_standards }}
            </div>

            <div class="footer">
                <p>Generated on {{ date }}</p>
                <p>Page {{ '{{' }} page {{ '}}' }} of {{ '{{' }} topage {{ '}}' }}</p>
            </div>
        </body>
        </html>
        """

    def create_document(self, contract_content, rate_schedule, service_areas, performance_standards):
        # Process contract content to convert markdown-style headers to HTML
        processed_content = []
        for line in contract_content.split('\n'):
            if line.strip():
                if line.startswith('#'):
                    level = line.count('#')
                    text = line.strip('#').strip()
                    processed_content.append(f"<h{level}>{text}</h{level}>")
                else:
                    processed_content.append(f"<p>{line}</p>")
        
        contract_html = '\n'.join(processed_content)

        # Render template
        template = Template(self.html_template)
        html_content = template.render(
            title=self.title,
            date=datetime.now().strftime('%B %d, %Y'),
            contract_content=contract_html,
            rate_schedule=rate_schedule,
            service_areas=service_areas,
            performance_standards=performance_standards
        )
        
        return html_content

def generate_filename(base_name, state_info):
    date_str = datetime.now().strftime("%Y%m%d")
    state_abbrev = state_info['state_abbrev']
    return f"{base_name}_{state_abbrev}_{date_str}"

def process_state(state_info):
    try:
        print(f"\nProcessing {state_info['state']}...")
        
        # Initialize generator
        generator = StateContractGenerator(state_info)

        # Generate all content
        print(f"Generating contract content for {state_info['state']}...")
        contract_text = generator.create_contract()
        
        print(f"Generating rate schedule for {state_info['state']}...")
        rate_schedule = generator.generate_rate_schedule()
        
        print(f"Generating service areas for {state_info['state']}...")
        service_areas = generator.generate_service_areas()
        
        print(f"Generating performance standards for {state_info['state']}...")
        performance_standards = generator.generate_performance_standards()

        if all([contract_text, rate_schedule, service_areas, performance_standards]):
            base_filename = generate_filename("Transportation_Contract", state_info)
            
            # Create HTML document
            print(f"Creating HTML document for {state_info['state']}...")
            html = ContractHTML(f"Transportation Services Contract - {state_info['state']}")
            html_content = html.create_document(
                contract_text,
                rate_schedule,
                service_areas,
                performance_standards
            )
            
            # Save HTML file
            html_filename = f"{base_filename}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML file saved: {html_filename}")

            # Convert to PDF
            print(f"Converting to PDF for {state_info['state']}...")
            pdf_filename = f"{base_filename}.pdf"
            
            try:
                # First, try to find wkhtmltopdf in the system path
                config = pdfkit.configuration()
                
                options = {
                    'page-size': 'Letter',
                    'margin-top': '25mm',
                    'margin-right': '25mm',
                    'margin-bottom': '25mm',
                    'margin-left': '25mm',
                    'encoding': 'UTF-8',
                    'enable-local-file-access': '',
                    'footer-right': '[page] of [topage]',
                    'footer-font-size': '9',
                    'header-font-size': '9',
                    'header-left': f"Transportation Services Contract - {state_info['state']}",
                    'header-right': datetime.now().strftime('%B %d, %Y'),
                    'header-line': '',
                    'footer-line': '',
                    'footer-left': 'Confidential and Proprietary',
                    'quiet': ''
                }

                # Try different methods of PDF generation
                try:
                    # Method 1: Direct from file
                    pdfkit.from_file(html_filename, pdf_filename, options=options, configuration=config)
                except Exception as e1:
                    print(f"First method failed, trying alternative method: {str(e1)}")
                    try:
                        # Method 2: From string
                        pdfkit.from_string(html_content, pdf_filename, options=options, configuration=config)
                    except Exception as e2:
                        print(f"Second method failed, trying final method: {str(e2)}")
                        try:
                            # Method 3: Simplified options
                            simple_options = {
                                'page-size': 'Letter',
                                'encoding': 'UTF-8',
                                'enable-local-file-access': '',
                                'quiet': ''
                            }
                            pdfkit.from_file(html_filename, pdf_filename, options=simple_options, configuration=config)
                        except Exception as e3:
                            raise Exception(f"All PDF generation methods failed: {str(e3)}")

                print(f"PDF file saved: {pdf_filename}")
                
            except Exception as e:
                print(f"Error converting to PDF: {str(e)}")
                print("Checking wkhtmltopdf installation...")
                
                # Try to get wkhtmltopdf version
                try:
                    import subprocess
                    result = subprocess.run(['wkhtmltopdf', '-V'], capture_output=True, text=True)
                    print(f"wkhtmltopdf version: {result.stdout}")
                except Exception as ve:
                    print("wkhtmltopdf not found in system path")
                    print("Please ensure wkhtmltopdf is installed:")
                    print("- Windows: Download from https://wkhtmltopdf.org/downloads.html")
                    print("- Mac: brew install wkhtmltopdf")
                    print("- Linux: sudo apt-get install wkhtmltopdf")
                
                return False
            
            print(f"Successfully generated contract for {state_info['state']}")
            return True
        else:
            print(f"Error: Failed to generate some content for {state_info['state']}")
            return False
            
    except Exception as e:
        print(f"Error processing {state_info['state']}: {str(e)}")
        return False



def main():
    # Create output directory if it doesn't exist
    output_dir = "contracts"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

    print("Starting contract generation process...")
    print(f"Output directory: {os.path.abspath(output_dir)}")
    print(f"Total states to process: {len(state_configs)}")
    print("-" * 50)

    # Process all states
    successful_states = 0
    failed_states = []
    total_states = len(state_configs)

    for i, (state_code, state_info) in enumerate(state_configs.items(), 1):
        print(f"\nProcessing state {i} of {total_states}: {state_code}")
        print("-" * 30)
        
        if process_state(state_info):
            successful_states += 1
        else:
            failed_states.append(state_code)
        
        print(f"Completed {i} of {total_states} states")
        print("-" * 30)

    # Print summary
    print("\n" + "=" * 50)
    print("Generation Summary:")
    print("=" * 50)
    print(f"Total states processed: {total_states}")
    print(f"Successfully generated: {successful_states} contracts")
    print(f"Failed states: {len(failed_states)}")
    if failed_states:
        print(f"Failed state codes: {', '.join(failed_states)}")
    print(f"\nContracts saved in: {os.path.abspath(output_dir)}")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        print("\nProcess completed")

