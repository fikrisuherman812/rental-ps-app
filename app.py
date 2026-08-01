import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Rental PS", layout="wide")
st.title("🎮 DATABASE RENTAL PLAYSTATION")

# Nama file penyimpanan lokal
FILE_DATA = "data_transaksi.xlsx"

# Peta Nomor TV ke Tipe PS
tv_type_map = {
    1: "PS3",
    2: "PS4",
    3: "PS3",
    4: "PS5"
}

# Fungsi Membaca Data (Otomatis Buat File Jika Belum Ada)
def load_data():
    if os.path.exists(FILE_DATA):
        return pd.read_excel(FILE_DATA)
    else:
        # Buat tabel awal jika file belum ada
        df_empty = pd.DataFrame(columns=["No", "Hari", "Tanggal", "Nama Pelanggan", "No TV", "Type", "Durasi (Jam)"])
        df_empty.to_excel(FILE_DATA, index=False)
        return df_empty

df = load_data()

# Form Input Transaksi di Sidebar
st.sidebar.header("Form Input Transaksi")
tanggal = st.sidebar.date_input("Tanggal", datetime.now())
nama = st.sidebar.text_input("Nama Pelanggan")
no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)

type_ps = tv_type_map.get(no_tv, "PS3")

if st.sidebar.button("Simpan Transaksi"):
    if not nama:
        st.sidebar.error("Mohon isi nama pelanggan!")
    else:
        # Buat baris baru
        no_baru = len(df) + 1
        hari_str = tanggal.strftime("%A")
        tgl_str = tanggal.strftime("%d/%m/%Y")
        
        new_row = pd.DataFrame([{
            "No": no_baru,
            "Hari": hari_str,
            "Tanggal": tgl_str,
            "Nama Pelanggan": nama,
            "No TV": no_tv,
            "Type": type_ps,
            "Durasi (Jam)": durasi
        }])
        
        # Gabung dan simpan ke file Excel
        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_excel(FILE_DATA, index=False)
        
        st.sidebar.success("✅ Transaksi Berhasil Disimpan!")
        st.rerun()

# Tampilkan Rekap & Data Transaksi
st.subheader("Data Transaksi Terkini")
st.dataframe(df, use_container_width=True)

# Tombol Unduh File Excel Rekapan
if not df.empty:
    st.markdown("---")
    # Konversi dataframe ke excel untuk diunduh
    with pd.ExcelWriter("rekap_rental.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    
    with open("rekap_rental.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download File Rekap Excel Terkini",
            data=file,
            file_name=f"Rekap_Rental_PS_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
