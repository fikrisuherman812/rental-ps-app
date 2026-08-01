import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, time

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

# Mode Aplikasi di Sidebar: Input Baru vs Edit Data
st.sidebar.header("⚙️ Menu Aplikasi")
mode = st.sidebar.radio("Pilih Aksi:", ["Input Transaksi Baru", "✏️ Edit / Ubah Transaksi", "🗑️ Hapus Transaksi"])

# --- MODE 1: INPUT TRANSAKSI BARU ---
if mode == "Input Transaksi Baru":
    st.sidebar.subheader("Form Input Transaksi")
    tanggal = st.sidebar.date_input("Tanggal", datetime.now())
    nama = st.sidebar.text_input("Nama Pelanggan")
    no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
    durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)
    jam_mulai = st.sidebar.time_input("Jam Mulai", value=datetime.now().time())

    type_ps = TV_MAP.get(no_tv, "PS3")
    tarif_per_jam = TARIF_PS.get(type_ps, 5000)
    total_nominal = durasi * tarif_per_jam

    waktu_mulai_dt = datetime.combine(tanggal, jam_mulai)
    waktu_selesai_dt = waktu_mulai_dt + timedelta(hours=durasi)
    jam_selesai = waktu_selesai_dt.time()

    st.sidebar.info(f"Type: **{type_ps}** | Tarif/Jam: **Rp{tarif_per_jam:,}**\n\nTotal: **Rp{total_nominal:,}**")

    if st.sidebar.button("💾 Simpan Transaksi"):
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

# --- MODE 2: EDIT / UBAH TRANSAKSI ---
elif mode == "✏️ Edit / Ubah Transaksi":
    st.sidebar.subheader("Form Edit Transaksi")
    if df.empty:
        st.sidebar.warning("Belum ada data transaksi yang bisa diubah.")
    else:
        list_no = df["No"].tolist()
        no_edit = st.sidebar.selectbox("Pilih No Transaksi yang Akan Diubah:", list_no)
        
        # Ambil data lama transaksi tersebut
        data_lama = df[df["No"] == no_edit].iloc[0]
        
        # Tampilkan form edit yang terisi data lama
        nama_edit = st.sidebar.text_input("Nama Pelanggan", value=str(data_lama["Nama Pelanggan"]))
        no_tv_edit = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=int(data_lama["No TV"]))
        durasi_edit = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=int(data_lama["Durasi (Jam)"]))
        
        # Parse jam mulai lama
        try:
            jam_mulai_obj = datetime.strptime(str(data_lama["Jam Mulai"]), "%H:%M").time()
        except:
            jam_mulai_obj = datetime.now().time()
            
        jam_mulai_edit = st.sidebar.time_input("Jam Mulai", value=jam_mulai_obj)

        type_ps_edit = TV_MAP.get(no_tv_edit, "PS3")
        tarif_edit = TARIF_PS.get(type_ps_edit, 5000)
        total_edit = durasi_edit * tarif_edit

        # Hitung jam selesai baru
        tgl_lama = datetime.now().date()
        waktu_mulai_dt = datetime.combine(tgl_lama, jam_mulai_edit)
        waktu_selesai_dt = waktu_mulai_dt + timedelta(hours=durasi_edit)
        jam_selesai_edit = waktu_selesai_dt.time().strftime("%H:%M")

        st.sidebar.info(f"Type Baru: **{type_ps_edit}** | Total Baru: **Rp{total_edit:,}**")

        if st.sidebar.button("Update Transaksi"):
            # Update data pada baris yang dipilih
            idx = df[df["No"] == no_edit].index[0]
            df.at[idx, "Nama Pelanggan"] = nama_edit
            df.at[idx, "No TV"] = no_tv_edit
            df.at[idx, "Type"] = type_ps_edit
            df.at[idx, "Jam Mulai"] = jam_mulai_edit.strftime("%H:%M")
            df.at[idx, "Durasi (Jam)"] = durasi_edit
            df.at[idx, "Jam Selesai"] = jam_selesai_edit
            df.at[idx, "Total (Rp)"] = total_edit

            df.to_excel(FILE_DATA, index=False)
            st.sidebar.success(f"✅ Transaksi No {no_edit} Berhasil Diperbarui!")
            st.rerun()

# --- MODE 3: HAPUS TRANSAKSI ---
elif mode == "🗑️ Hapus Transaksi":
    st.sidebar.subheader("Hapus Transaksi")
    if df.empty:
        st.sidebar.warning("Belum ada data transaksi yang bisa dihapus.")
    else:
        list_no = df["No"].tolist()
        no_hapus = st.sidebar.selectbox("Pilih No Transaksi yang Akan Dihapus:", list_no)
        
        if st.sidebar.button("❌ Hapus Transaksi Ini"):
            df = df[df["No"] != no_hapus]
            df["No"] = range(1, len(df) + 1)
            df.to_excel(FILE_DATA, index=False)
            st.sidebar.success(f"✅ Transaksi No {no_hapus} Berhasil Dihapus!")
            st.rerun()

# Tampilkan Tabel Utama
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
