from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from src.backend.app.reports.schemas import AssessmentReportData
import os

# Optional weasyprint import - only needed for PDF generation
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"WeasyPrint not available: {e}. PDF generation will be disabled.")

class PDFGenerator:
    def __init__(self, template_dir: str):
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint is not installed or system dependencies are missing. "
                "PDF generation is unavailable. Install GTK+ libraries for Windows."
            )
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_report(self, data: AssessmentReportData) -> bytes:
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("PDF generation is unavailable - WeasyPrint not installed")

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
