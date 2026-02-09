from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from src.backend.app.reports.schemas import AssessmentReportData
import os

class PDFGenerator:
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_report(self, data: AssessmentReportData) -> bytes:
        template = self.env.get_template("report.html")
        
        # Render HTML with data
        html_string = template.render(data=data)
        
        # Create PDF
        # We might need to handle Base URL for static assets (images, css)
        # For POC, we'll embed CSS or assume no external assets for now.
        
        # Define base_url to current dir?
        base_url = os.path.dirname(os.path.abspath(__file__))
        
        html = HTML(string=html_string, base_url=base_url)
        
        # Output to bytes
        buffer = BytesIO()
        html.write_pdf(target=buffer)
        
        return buffer.getvalue()
