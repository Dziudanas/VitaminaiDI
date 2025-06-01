from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import os

def generate_pdf(content: str) -> BytesIO:
    buffer = BytesIO()

    # Correct font path
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVu", font_path))

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("DejaVu", 12)

    width, height = A4
    margin_left = 50
    margin_top = 50
    line_height = 15
    max_width = width - 2 * margin_left
    y = height - margin_top

    for paragraph in content.split('\n'):
        lines = simpleSplit(paragraph, "DejaVu", 12, max_width)
        for line in lines:
            if y < margin_top:
                p.showPage()
                p.setFont("DejaVu", 12)
                y = height - margin_top
            p.drawString(margin_left, y, line)
            y -= line_height

    p.save()
    buffer.seek(0)
    return buffer
