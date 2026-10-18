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
agency_name = st.sidebar.text_input(
    "Agency Name (White-Label)", value="Digital Growth Agency"
)

st.write("---")
website_url = st.text_input(
    "Enter Client Website URL:", placeholder="https://example.com"
)
business_name = st.text_input(
    "Business Name:", placeholder="e.g. Acme Dental Care"
)
