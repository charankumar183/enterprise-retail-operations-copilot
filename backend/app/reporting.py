from pathlib import Path
from datetime import datetime,timezone
from html import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from .config import settings

def make_pdf(title,question,answer,sources,outpath):
    outpath=Path(outpath);outpath.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='Cover',parent=styles['Title'],fontSize=18,textColor=colors.HexColor('#163460'),spaceAfter=20))
    styles.add(ParagraphStyle(name='RetailBody',parent=styles['BodyText'],leading=16,spaceAfter=10))
    doc=SimpleDocTemplate(str(outpath),pagesize=(595,842),topMargin=55,bottomMargin=55)
    story=[Paragraph(escape(title),styles['Cover']),Paragraph('SYNTHETIC RETAIL ENTERPRISE — DEMONSTRATION REPORT',styles['Normal']),Spacer(1,18),Paragraph('Generated '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),styles['Normal']),Spacer(1,20),Paragraph('Request',styles['Heading2']),Paragraph(escape(question),styles['RetailBody']),Paragraph('Findings',styles['Heading2'])]
    for line in answer.replace('**','').split('\n'):
        if line.strip():story.append(Paragraph(escape(line[:1800]),styles['RetailBody']))
    story.append(Paragraph('Evidence and source references',styles['Heading2']))
    if sources:
        for s in sources:story.append(Paragraph(escape(f"{s['document_name']} | Section: {s['section']} | Page: {s.get('page_number') or 'Unavailable'} | Retrieval score: {s.get('retrieval_score')}"),styles['RetailBody']))
    else:story.append(Paragraph('Database-backed response. Evidence: structured inventory, sales or procurement records.',styles['RetailBody']))
    story.append(Spacer(1,12));story.append(Paragraph('Scores are retrieval relevance signals, not calibrated probabilities. Validate all operational decisions against primary records.',styles['Italic']))
    doc.build(story)
    return str(outpath)
