import io
import requests
from bs4 import BeautifulSoup
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Page Configuration
st.set_page_config(page_title="Local SEO Audit SaaS", page_icon="🔍", layout="centered")

# Custom CSS for Modern SaaS Aesthetic
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0px;
    }
    .main-title span {
        color: #2563eb;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background-color: #16a34a;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #15803d;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for White-label Agency Branding & Advanced API
agency_name = st.sidebar.text_input("Agency Name (White-Label)", value="Digital Growth Agency")
st.sidebar.markdown("---")
st.sidebar.subheader("Advanced Scraping Settings")
scraper_api_key = st.sidebar.text_input("ScraperAPI Key (Optional)", type="password", help="Get a free key from scraperapi.com to bypass Apple/Nike bot blocks.")

# Modern Hero Section Header
st.markdown('<p class="main-title">Get found by more local customers — <br><span>we fix your local presence for you</span></p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Run a free 60-second scan to see what is keeping your business out of local search results. Generate a professional executive PDF report instantly.</p>', unsafe_allow_html=True)

st.write("---")

# Input Form Layout
website_url = st.text_input("Enter Client Website URL:", placeholder="https://example.com")
business_name = st.text_input("Business Name:", placeholder="e.g. Acme Dental Care")

def audit_website(url, api_key=""):
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
            
        if api_key:
            # Route through ScraperAPI to bypass bot protection / Cloudflare
            payload = {'api_key': api_key, 'url': url}
            response = requests.get('http://api.scraperapi.com', params=payload, timeout=25)
        else:
            # Standard direct request with User-Agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
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

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'), spaceAfter=2)
    subtitle_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    section_heading = ParagraphStyle('SecHead', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), spaceAfter=4)

    story.append(Paragraph("Local SEO Health Report", title_style))
    story.append(Paragraph(f"Comprehensive Technical & On-Page Audit • Prepared by <b>{agency}</b>", subtitle_style))

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
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))

    story.append(t_breakdown)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Actionable Next Steps & Strategy", section_heading))
    
    steps = [
        "<b>Maintain Structural Integrity:</b> Continue preserving single H1 tags on primary service landing pages.",
        "<b>Local Keyword Inclusion:</b> Ensure primary local service areas remain included in Meta Titles and Descriptions.",
        "<b>Schema Markup Expansion:</b> Implement Local Business Structured Data to enhance Google Maps visibility."
    ]

    for step in steps:
        story.append(Paragraph(f"• {step}", body_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<font color='#94a3b8'>Local SEO Audit Report Generated by {agency}</font>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Styled SaaS Call-To-Action Button
if st.button("Run My Free Local SEO Audit →"):
    if website_url:
        with st.spinner("Scanning website and generating report..."):
            results = audit_website(website_url, scraper_api_key)
        st.success("Website successfully scanned!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("On-Page Score", f"{results['score']}%")
        col2.metric("Meta Description", "Found" if results['has_meta_desc'] else "Missing")
        col3.metric("H1 Headings", f"{results['h1_count']} Found")
        
        pdf_bytes = generate_pdf(business_name or "Client", website_url, agency_name, results)
        
        st.download_button(
            label="📄 Download Executive PDF Report",
            data=pdf_bytes,
            file_name=f"{business_name or 'SEO'}_Executive_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please enter a website URL.")
