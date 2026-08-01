import streamlit as st
import pandas as pd
import gspread

st.set_page_config(page_title="Rental PS", layout="wide")
st.title("🎮 DATABASE RENTAL PLAYSTATION")

# Ambil URL Google Sheets dari Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

@st.cache_resource
def get_gspread_client():
    # Menggunakan koneksi gspread via gspread.public / client
    return gspread.public(sheet_url)

try:
    # Buka Google Sheets
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"]) if "gcp_service_account" in st.secrets else None
    
    if gc:
        sh = gc.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)
    else:
        st.error("Perlu konfigurasi Service Account untuk menulis data.")
        st.stop()
        
except Exception as e:
    st.warning("Menggunakan mode koneksi alternatif...")
