import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Rental PS", layout="wide")
st.title("🎮 DATABASE RENTAL PLAYSTATION")

# Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Membaca data mulai dari baris header sebenarnya (header=1)
df = conn.read(ttl=0, header=1)

# Pilihan TV dan Type PS otomatis
tv_type_map = {
    1: "PS3",
    2: "PS4",
    3: "PS3",
    4: "PS5"  # Sesuaikan tipe PS dengan nomor TV Anda jika ada
}

# Sidebar Input Transaksi
st.sidebar.header("Form Input Transaksi")
tanggal = st.sidebar.date_input("Tanggal")
nama = st.sidebar.text_input("Nama Pelanggan")
no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)

type_ps = tv_type_map.get(no_tv, "PS3")

if st.sidebar.button("Simpan Transaksi"):
    # Hitung nomor urut transaksi berikutnya
    no_berikutnya = len(df) + 1
    
    # Format hari dan tanggal
    hari_str = tanggal.strftime("%A")  # Atau isi manual
    tgl_str = tanggal.strftime("%d/%m/%y")
    
    # Baris data baru sesuai struktur kolom di Sheets Anda
    new_data = pd.DataFrame([{
        "Kupon": "None",
        "No": no_berikutnya,
        "Hari": hari_str,
        "Tanggal": tgl_str,
        "No TV": no_tv,
        "Type": type_ps,
        "Durasi": durasi
    }])
    
    # Gabungkan dan update ke Google Sheets
    updated_df = pd.concat([df, new_data], ignore_index=True)
    conn.update(data=updated_df)
    
    st.sidebar.success("✅ Transaksi Berhasil Disimpan!")
    st.rerun()

# Tampilkan Tabel
st.subheader("Data Transaksi Terkini")
st.dataframe(df, use_container_width=True)
