from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from typing import Optional
from app.models.schemas import AnalysisResponse

class ReportGenerator:
    def __init__(self, template_dir="app/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def generate_html(self, analysis: AnalysisResponse) -> str:
        template = self.env.get_template("report.html")
        return template.render(analysis=analysis)
        
    def generate_pdf(self, analysis: AnalysisResponse) -> bytes:
        html_content = self.generate_html(analysis)
        return HTML(string=html_content).write_pdf()

report_generator = ReportGenerator()
