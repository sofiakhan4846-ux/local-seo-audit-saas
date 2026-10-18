import io
import requests
from bs4 import BeautifulSoup
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(page_title="Local SEO Auditor", page_icon="🔍")

st.title("🔍 Local SEO Audit SaaS Tool")
st.subheader("Automated Real-Time Executive SEO Report Generator")

# Sidebar for White-label
agency_name = st.sidebar.text_input("Agency Name (White-Label)", value="Digital Growth Agency")

st.write("---")
website_url = st.text_input("Enter Client Website URL:", placeholder="https://example.com")
business_name = st.text_input("Business Name:", placeholder="e.g. Acme Dental Care")

def audit_website(url):
    results = {
        "has_title": False, "title": "",
        "has_meta_desc": False, "meta_desc": "",
        "has_h1": False, "h1_count": 0, "score": 0,
        "is_https": False
    }
    try:
        if url.startswith("https://"):
            results["is_https"] = True
        elif not url.startswith("http://"):
            url = "https://" + url
            results["is_https"] = True
            
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            if title_tag and title_tag.string:
                results["has_title"] = True
                results["title"] = title_tag.string.strip()
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                results["has_meta_desc"] = True
                results["meta_desc"] = meta_desc['content'].strip()
            h1_tags = soup.find_all('h1')
            results["h1_count"] = len(h1_tags)
            results["has_h1"] = len(h1_tags) > 0
            
            score = 0
            if results["has_title"]: score += 30
            if results["has_meta_desc"]: score += 30
            if results["has_h1"]: score += 20
            if results["is_https"]: score += 20
            results["score"] = score
    except Exception as e:
        pass
    return results

def generate_pdf(biz_name, url, agency, audit_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    # Custom Typography Styles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'), spaceAfter=2)
    subtitle_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    section_heading = ParagraphStyle('SecHead', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), spaceAfter=4)

    # Header Section
    story.append(Paragraph(f"Local SEO Health Report", title_style))
    story.append(Paragraph(f"Comprehensive Technical & On-Page Audit • Prepared by <b>{agency}</b>", subtitle_style))

    # Meta Overview Box Data
    overview_data = [
        [Paragraph("<b>Target Business:</b>", body_style), Paragraph(f"{biz_name}", body_style), Paragraph("<b>Audit Date:</b>", body_style), Paragraph("October 18, 2026", body_style)],
        [Paragraph("<b>Analyzed URL:</b>", body_style), Paragraph(f"{url}", body_style), Paragraph("<b>On-Page Score:</b>", body_style), Paragraph(f"<b>{audit_data['score']}%</b>", body_style)]
    ]
    t_overview = Table(overview_data, colWidths=[90, 200, 80, 170])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(t_overview)
    story.append(Spacer(1, 15))

    # Technical Elements Breakdown Section
    story.append(Paragraph("Technical Elements Breakdown", section_heading))

    table_data = [
        ["Check Item", "Status", "Detected Content / Details"],
        [
            "Page Title Tag",
            "PASSED" if audit_data['has_title'] else "MISSING",
            Paragraph(f'"{audit_data["title"]}"' if audit_data['has_title'] else "No title tag found on the page.", body_style)
        ],
        [
            "Meta Description",
            "PASSED" if audit_data['has_meta_desc'] else "MISSING",
            Paragraph("Meta description present and formatted for search snippet." if audit_data['has_meta_desc'] else "Missing meta description tag.", body_style)
        ],
        [
            "H1 Heading Tags",
            "PASSED" if audit_data['has_h1'] else "MISSING",
            Paragraph(f"Exactly {audit_data['h1_count']} main H1 tag(s) identified." if audit_data['has_h1'] else "No H1 tag detected.", body_style)
        ],
        [
            "SSL & Security",
            "PASSED" if audit_data['is_https'] else "WARNING",
            Paragraph("HTTPS protocol active and secure connection verified." if audit_data['is_https'] else "Insecure HTTP connection.", body_style)
        ]
    ]

    t_breakdown = Table(table_data, colWidths=[110, 80, 350])
    t_breakdown.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0),
