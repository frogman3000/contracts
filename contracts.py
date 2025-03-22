import boto3
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, PageTemplate, Frame,
                               Table, TableStyle, Spacer)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from textwrap import wrap
from reportlab.platypus.doctemplate import PageBreak

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
        prompt = f"""Generate a detailed contract between the {self.health_agency} (located in {self.agency_city}, {self.state}) 
        and {self.provider_name} (a transportation provider headquartered in {self.provider_city}, {self.state}). 

        Use these specific details:
        - Contract date: {self.contract_date}
        - Term: {self.provider_details['term']}
        - Service area: {', '.join(self.service_regions)}
        - Provider details: 
            * Fleet size: {self.provider_details['fleet_size']} vehicles
            * Operating hours: {self.provider_details['operating_hours']}
            * Number of certified drivers: {self.provider_details['driver_count']}
        
        The response should be in a format that can be parsed into sections, with clear headings marked by '#' symbols.
        Include standard contract sections but make all details specific to {self.state} and medical transportation."""

        return self.generate_content_with_bedrock(prompt)

    def generate_rate_schedule(self):
        prompt = f"""Generate a detailed transportation rate schedule for {self.health_agency} contract with {self.provider_name} 
        in {self.state}. The response should be in a format that can be converted to a table with the following columns:
        
        Service Type | Base Rate | Mileage Rate | Wait Time Rate | After Hours | Weekend/Holiday
        
        Include these service types:
        - Standard Vehicle Transport
        - Wheelchair Accessible Vehicle
        - Stretcher Transport
        - Bariatric Transport
        - Group Transport
        
        Consider {self.state}'s:
        - Cost of living
        - Fuel costs
        - Urban vs rural rates
        - State regulations
        
        Make rates realistic for {self.state} market in 2024.
        Format the response as pipe-separated values for easy table creation."""

        return self.generate_content_with_bedrock(prompt)

    def generate_service_areas(self):
        prompt = f"""Generate a detailed service area coverage table for {self.provider_name}'s contract in {self.state}.
        The response should be in a format that can be converted to a table with the following columns:

        Service Zone | Counties Covered | Response Time | Population Served | Facilities Covered | Special Conditions

        Create entries for:
        - Primary urban zones
        - Suburban areas
        - Rural coverage
        - Special service areas
        
        Consider {self.state}'s:
        - Geographic features
        - Population distribution
        - Healthcare facility locations
        - Emergency service requirements

        Format the response as pipe-separated values for easy table creation."""

        return self.generate_content_with_bedrock(prompt)

    def generate_performance_standards(self):
        prompt = f"""Generate detailed performance standards for {self.provider_name}'s contract in {self.state}.
        The response should be in a format that can be converted to a table with the following columns:

        Performance Category | Standard | Measurement Method | Minimum Target | Penalty for Non-Compliance

        Include standards for:
        - On-time performance
        - Vehicle maintenance
        - Driver qualifications
        - Customer service
        - Safety metrics
        - Complaint resolution
        
        Consider {self.state}'s:
        - Healthcare regulations
        - Quality metrics
        - Reporting requirements
        
        Format the response as pipe-separated values for easy table creation."""

        return self.generate_content_with_bedrock(prompt)

class ContractPDF:
    def __init__(self, filename, title):
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.story = []
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            ParagraphStyle(name='TOCHeading1', fontSize=12, leftIndent=20),
            ParagraphStyle(name='TOCHeading2', fontSize=10, leftIndent=40),
            ParagraphStyle(name='TOCHeading3', fontSize=10, leftIndent=60),
        ]

    def create_table_from_data(self, data, table_title):
        """Convert pipe-separated data into a formatted table with flexible column widths"""
        # Split data into rows
        rows = [row.strip().split('|') for row in data.strip().split('\n')]
        # Strip whitespace from each cell
        rows = [[cell.strip() for cell in row] for row in rows]
        
        # Calculate column widths based on content
        col_widths = []
        for col_idx in range(len(rows[0])):
            max_width = max(len(str(row[col_idx])) for row in rows)
            col_widths.append(min(max_width * 0.1 * inch, self.doc.width/len(rows[0])))
        
        # Create the table
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        
        # Add style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ])
        table.setStyle(style)
        
        # Add table title
        elements = []
        elements.append(Paragraph(f"<b>{table_title}</b>", 
                                ParagraphStyle('TableTitle', 
                                             fontSize=12, 
                                             spaceAfter=10,
                                             spaceBefore=20)))
        elements.append(table)
        elements.append(Spacer(1, 20))  # Add space after table
        
        return elements

    def header(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(72, 800, f"{self.title}")
        canvas.drawString(72, 785, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        canvas.restoreState()

    def footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = f"Page {canvas.getPageNumber()}"
        canvas.drawString(500, 50, page_num)
        canvas.drawString(72, 50, "Confidential and Proprietary")
        canvas.restoreState()

    def header_footer(self, canvas, doc):
        self.header(canvas, doc)
        self.footer(canvas, doc)

    def create_document(self, contract_content, rate_schedule, service_areas, performance_standards):
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        self.story.append(Paragraph(self.title, title_style))
        self.story.append(PageBreak())
        
        # Add table of contents
        self.story.append(Paragraph('Table of Contents', styles['Heading1']))
        self.story.append(self.toc)
        self.story.append(PageBreak())
        
        # Process main contract content
        for section in contract_content.split('\n'):
            if section.strip():
                if section.startswith('#'):
                    level = section.count('#')
                    text = section.strip('#').strip()
                    self.story.append(Paragraph(text, styles[f'Heading{level}']))
                else:
                    self.story.append(Paragraph(section, styles['Normal']))
        
        # Add attachments section
        self.story.append(Paragraph('Attachments', styles['Heading1']))
        
        # Add Rate Schedule
        self.story.extend(self.create_table_from_data(rate_schedule, 'Attachment A: Rate Schedule'))
        
        # Add Service Areas
        self.story.extend(self.create_table_from_data(service_areas, 'Attachment B: Service Areas'))
        
        # Add Performance Standards
        self.story.extend(self.create_table_from_data(performance_standards, 'Attachment C: Performance Standards'))
        
        # Create page template
        frame = Frame(
            self.doc.leftMargin,
            self.doc.bottomMargin,
            self.doc.width,
            self.doc.height,
            id='normal'
        )
        template = PageTemplate(
            id='custom',
            frames=frame,
            onPage=self.header_footer
        )
        self.doc.addPageTemplates([template])
        
        # Build document
        self.doc.multiBuild(self.story)

def generate_filename(base_name, state_info):
    date_str = datetime.now().strftime("%Y%m%d")
    state_abbrev = state_info['state_abbrev']
    return f"{base_name}_{state_abbrev}_{date_str}.pdf"

def process_state(state_info):
    try:
        print(f"\nProcessing {state_info['state']}...")
        
        # Initialize generator
        generator = StateContractGenerator(state_info)

        # Generate all content
        contract_text = generator.create_contract()
        rate_schedule = generator.generate_rate_schedule()
        service_areas = generator.generate_service_areas()
        performance_standards = generator.generate_performance_standards()

        if all([contract_text, rate_schedule, service_areas, performance_standards]):
            filename = generate_filename("Transportation_Contract", state_info)
            pdf = ContractPDF(
                filename,
                f"Transportation Services Contract - {state_info['state']}"
            )
            
            pdf.create_document(
                contract_text,
                rate_schedule,
                service_areas,
                performance_standards
            )
            
            print(f"Successfully generated contract for {state_info['state']}")
            print(f"Saved as: {filename}")
            return True
        else:
            print(f"Error: Failed to generate some content for {state_info['state']}")
            return False
            
    except Exception as e:
        print(f"Error processing {state_info['state']}: {str(e)}")
        return False

def main():


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
    
    # Create output directory if it doesn't exist
    output_dir = "contracts"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

    # Process all states
    successful_states = 0
    failed_states = []

    for state_code, state_info in state_configs.items():
        if process_state(state_info):
            successful_states += 1
        else:
            failed_states.append(state_code)

    # Print summary
    print("\nGeneration Summary:")
    print(f"Successfully generated: {successful_states} contracts")
    if failed_states:
        print(f"Failed states: {', '.join(failed_states)}")
    print(f"Contracts saved in: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
