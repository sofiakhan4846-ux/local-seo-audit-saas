import streamlit as st
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

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
        "status": "Success",
        "has_title": False,
        "title_text": "",
        "has_meta_desc": False,
        "has_h1": False,
        "h1_count": 0,
        "score": 0
    }
    
    try:
        if not url.startswith("http"):
            url = "https://" + url
            
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title Check
            if soup.title and soup.title.string:
                results["has_title"] = True
                results["title_text"] = soup.title.string.strip()
                results["score"] += 35
                
            # Meta Description Check
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                results["has_meta_desc"] = True
                results["score"] += 35
                
            # H1 Tag Check
            h1_tags = soup.find_all('h1')
            if h1_tags:
                results["has_h1"] = True
                results["h1_count"] = len(h1_tags)
                results["score"] += 30
        else:
            results["status"] = f"Failed (HTTP {response.status_code})"
    except Exception as e:
        results["status"] = f"Error connecting to website"
        
    return results

def generate_pdf(biz_name, url, agency, audit_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title & Info
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
    story.append(Paragraph(f"Local SEO Audit Report for {biz_name}", title_style))
    story.append(Paragraph(f"<b>Prepared by:</b> {agency}", styles['Normal']))
    story.append(Paragraph(f"<b>Website Analyzed:</b> {url}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Audit Summary
    story.append(Paragraph("<b>Real-Time SEO Performance:</b>", styles['Heading2']))
    story.append(Paragraph(f"• Overall On-Page Health Score: <b>{audit_data['score']}%</b>", styles['Normal']))
    story.append(Paragraph(f"• Page Title Found: {'Yes' if audit_data['has_title'] else 'No'}", styles['Normal']))
    story.append(Paragraph(f"• Meta Description Found: {'Yes' if audit_data['has_meta_desc'] else 'No'}", styles['Normal']))
    story.append(Paragraph(f"• H1 Heading Tag Count: {audit_data['h1_count']}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Recommendations
    story.append(Paragraph("<b>Actionable Next Steps:</b>", styles['Heading2']))
    if not audit_data['has_title']:
        story.append(Paragraph("1. High Priority: Add a SEO-optimized Title tag.", styles['Normal']))
    if not audit_data['has_meta_desc']:
        story.append(Paragraph("2. High Priority: Add a compelling Meta Description for higher CTR.", styles['Normal']))
    if not audit_data['has_h1']:
        story.append(Paragraph("3. Medium Priority: Add a main H1 tag on the homepage.", styles['Normal']))
    if audit_data['score'] == 100:
        story.append(Paragraph("1. Essential On-page tags are well structured!", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("Run SEO Audit"):
    if website_url:
        with st.spinner("Scanning website in real-time..."):
            audit_res = audit_website(website_url)
            
        if audit_res["status"] == "Success":
            st.success("Website successfully scanned!")
            
            # Metrics Display
            col1, col2, col3 = st.columns(3)
            col1.metric("On-Page Score", f"{audit_res['score']}%")
            col2.metric("Meta Description", "Found" if audit_res['has_meta_desc'] else "Missing")
            col3.metric("H1 Headings", f"{audit_res['h1_count']} Found")
            
            st.write("### 📌 Real-Time Audit Insights")
            if audit_res["has_title"]:
                st.info(f"*Page Title:* {audit_res['title_text']}")
            else:
                st.error("❌ *Page Title:* Missing")
                
            if not audit_res["has_meta_desc"]:
                st.warning("⚠️ *Meta Description:* Missing! Add meta description to improve Google click-through rates.")
            else:
                st.success("✅ *Meta Description:* Present")
                
            if not audit_res["has_h1"]:
                st.warning("⚠️ *H1 Tag:* No H1 heading found on page.")
            else:
                st.success(f"✅ *H1 Tag:* {audit_res['h1_count']} H1 tag(s) detected.")
                
            # PDF Download
            pdf_data = generate_pdf(business_name if business_name else "Client", website_url, agency_name, audit_res)
            
            st.write("---")
            st.download_button(
                label="📄 Download Updated PDF Report",
                data=pdf_data,
                file_name=f"SEO_Audit_{business_name if business_name else 'Report'}.pdf",
                mime="application/pdf"
            )
        else:
            st.error(f"Could not scan URL. Reason: {audit_res['status']}")
    else:
        st.error("Please enter a valid URL.")