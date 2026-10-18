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
st.subheader("Automated Real-Time SEO Report Generator")

# Sidebar for White-label
agency_name = st.sidebar.text_input("Agency Name (White-Label)", value="Digital Growth Agency")

st.write("---")
website_url = st.text_input("Enter Client Website URL:", placeholder="https://example.com")
business_name = st.text_input("Business Name:", placeholder="e.g. Acme Dental Care")

def audit_website(url):
    results = {
        "has_title": False, "title": "",
        "has_meta_desc": False, "meta_desc": "",
        "has_h1": False, "h1_count": 0, "score": 0
    }
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
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
            if results["has_title"]: score += 40
            if results["has_meta_desc"]: score += 40
            if results["has_h1"]: score += 20
            results["score"] = score
    except Exception as e:
        pass
    return results

def generate_pdf(biz_name, url, agency, audit_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15)

    story.append(Paragraph(f"Local SEO Health Report: <b>{biz_name}</b>", title_style))
    story.append(Paragraph(f"Prepared by <b>{agency}</b> • Target: {url}", subtitle_style))

    table_data = [
        ["SEO Health Score", "Meta Title", "Meta Description", "H1 Headings"],
        [
            f"{audit_data['score']}%",
            "Found" if audit_data['has_title'] else "Missing",
            "Found" if audit_data['has_meta_desc'] else "Missing",
            f"{audit_data['h1_count']} Found"
        ]
    ]

    t = Table(table_data, colWidths=[130, 130, 130, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,1), (-1,1), 10),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Actionable Recommendations:</b>", styles['Heading2']))
    story.append(Spacer(1, 6))

    recs = []
    if not audit_data['has_title']: recs.append("• <b>High Priority:</b> Add an SEO-optimized Title tag.")
    if not audit_data['has_meta_desc']: recs.append("• <b>High Priority:</b> Add a compelling Meta Description for higher search CTR.")
    if not audit_data['has_h1']: recs.append("• <b>Medium Priority:</b> Add a main H1 tag on the homepage.")
    if audit_data['score'] == 100: recs.append("• <b>Great Job!</b> On-page core meta tags are well structured.")

    for r in recs:
        story.append(Paragraph(r, styles['Normal']))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- YAHAN HAI MAIN BUTTON CODE JO MISS HO GAYA THA ---
if st.button("Run SEO Audit"):
    if website_url:
        with st.spinner("Scanning website..."):
            results = audit_website(website_url)
        st.success("Website successfully scanned!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("On-Page Score", f"{results['score']}%")
        col2.metric("Meta Description", "Found" if results['has_meta_desc'] else "Missing")
        col3.metric("H1 Headings", f"{results['h1_count']} Found")
        
        pdf_bytes = generate_pdf(business_name or "Client", website_url, agency_name, results)
        
        st.download_button(
            label="📄 Download Updated PDF Report",
            data=pdf_bytes,
            file_name=f"{business_name or 'SEO'}_Audit_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please enter a website URL.")
