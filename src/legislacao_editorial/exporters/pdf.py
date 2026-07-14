from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from ..models import LegalDocument


def _page_number(canvas, _doc) -> None:
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0] / 2, 0.8 * cm, str(canvas.getPageNumber()))
    canvas.restoreState()


def export_pdf(document: LegalDocument, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#263238"), spaceAfter=24))
    styles.add(ParagraphStyle(name="Legal", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=9.2, leading=13, spaceAfter=8))
    styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], fontSize=8,
                              textColor=colors.HexColor("#555555"), leading=11))
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.6 * cm,
                            title=document.source.name)
    source = document.source
    story = [
        Spacer(1, 4 * cm),
        Paragraph(source.name, styles["Cover"]),
        Paragraph(f"Fonte oficial: {source.url}", styles["Meta"]),
        Paragraph(f"Coleta: {source.collected_at.isoformat()}", styles["Meta"]),
        Paragraph(f"SHA-256: {source.content_hash}", styles["Meta"]),
        Paragraph(f"Artigos incluídos: {len(document.articles)}", styles["Meta"]),
        PageBreak(),
    ]
    previous_path: tuple[str, ...] = ()
    for article in document.articles:
        if article.heading_path != previous_path:
            for heading in article.heading_path:
                story.extend([Paragraph(heading, styles["Heading2"]), Spacer(1, 4)])
            previous_path = article.heading_path
        safe_text = article.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_text = safe_text.replace("\n", "<br/>")
        story.append(Paragraph(safe_text, styles["Legal"]))
    doc.build(story, onFirstPage=_page_number, onLaterPages=_page_number)
    return target

