import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🎮 DATABASE RENTAL PLAYSTATION")

# Membuat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Membaca data dari Google Sheets (misal Sheet1 atau Data Transaksi)
df = conn.read(ttl=0) # ttl=0 agar data selalu paling baru (live)

st.write("### Data Transaksi Terkini")
st.dataframe(df)

# Form Input Transaksi Baru
st.sidebar.header("Form Input Transaksi")
tanggal = st.sidebar.date_input("Tanggal")
nama = st.sidebar.text_input("Nama Pelanggan")
no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)

if st.sidebar.button("Simpan Transaksi"):
    # Buat data baru
    new_data = pd.DataFrame([{
        "Tanggal": str(tanggal),
        "Nama Pelanggan": nama,
        "No TV": no_tv,
        "Durasi": durasi
    }])
    
    # Gabungkan dengan data lama dan simpan ke Google Sheets
    updated_df = pd.concat([df, new_data], ignore_index=True)
    conn.update(data=updated_df)
    
    st.sidebar.success("Transaksi Berhasil Disimpan ke Google Sheets!")
    st.rerun()
