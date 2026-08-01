import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Rental PS", layout="wide")
st.title("🎮 DATABASE RENTAL PLAYSTATION")

# Nama file penyimpanan
FILE_DATA = "data_transaksi.xlsx"

# Tarif per Jam & Tipe PS berdasarkan No TV
TARIF_PS = {
    "PS3": 5000,
    "PS4": 7500,
    "PS5": 12000
}

TV_MAP = {
    1: "PS3",
    2: "PS4",
    3: "PS3",
    4: "PS5"
}

# Fungsi Membaca Data
def load_data():
    if os.path.exists(FILE_DATA):
        return pd.read_excel(FILE_DATA)
    else:
        columns = [
            "No", "Hari", "Tanggal", "Nama Pelanggan", "No TV", "Type", 
            "Jam Mulai", "Durasi (Jam)", "Jam Selesai", "Total (Rp)"
        ]
        df_empty = pd.DataFrame(columns=columns)
        df_empty.to_excel(FILE_DATA, index=False)
        return df_empty

df = load_data()

# Form Input Transaksi di Sidebar
st.sidebar.header("Form Input Transaksi")
tanggal = st.sidebar.date_input("Tanggal", datetime.now())
nama = st.sidebar.text_input("Nama Pelanggan")
no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)
jam_mulai = st.sidebar.time_input("Jam Mulai", value=datetime.now().time())

# Tipe PS dan Tarif Otomatis
type_ps = TV_MAP.get(no_tv, "PS3")
tarif_per_jam = TARIF_PS.get(type_ps, 5000)
total_nominal = durasi * tarif_per_jam

# Hitung Jam Selesai
waktu_mulai_dt = datetime.combine(tanggal, jam_mulai)
waktu_selesai_dt = waktu_mulai_dt + timedelta(hours=durasi)
jam_selesai = waktu_selesai_dt.time()

# Tampilkan Informasi Tarif di Sidebar
st.sidebar.info(f"Type: **{type_ps}** | Tarif/Jam: **Rp{tarif_per_jam:,}**\n\nTotal: **Rp{total_nominal:,}**")

if st.sidebar.button("Simpan Transaksi"):
    if not nama:
        st.sidebar.error("Mohon isi nama pelanggan!")
    else:
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
            "Jam Mulai": jam_mulai.strftime("%H:%M"),
            "Durasi (Jam)": durasi,
            "Jam Selesai": jam_selesai.strftime("%H:%M"),
            "Total (Rp)": total_nominal
        }])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df.to_excel(FILE_DATA, index=False)
        
        st.sidebar.success("✅ Transaksi Berhasil Disimpan!")
        st.rerun()

# Tampilkan Tabel
st.subheader("Data Transaksi Terkini")
st.dataframe(df, use_container_width=True)

# Tombol Download Rekap
if not df.empty:
    st.markdown("---")
    with pd.ExcelWriter("rekap_rental.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    
    with open("rekap_rental.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download File Rekap Excel Terkini",
            data=file,
            file_name=f"Rekap_Rental_PS_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
