import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Rental PS", layout="wide")
st.title("🎮 DATABASE & KEUANGAN RENTAL PLAYSTATION")

# File Penyimpanan Data
FILE_PEMASUKAN = "data_pemasukan.xlsx"
FILE_PENGELUARAN = "data_pengeluaran.xlsx"

TARIF_PS = {"PS3": 5000, "PS4": 7500, "PS5": 12000}
TV_MAP = {1: "PS3", 2: "PS4", 3: "PS3", 4: "PS5"}

# --- FUNGSI LOAD DATA ---
def load_pemasukan():
    if os.path.exists(FILE_PEMASUKAN):
        df = pd.read_excel(FILE_PEMASUKAN)
        df["Tanggal_DT"] = pd.to_datetime(df["Tanggal_DT"])
        return df
    else:
        cols = ["No", "Hari", "Tanggal", "Tanggal_DT", "Nama Pelanggan", "No TV", "Type", "Jam Mulai", "Durasi (Jam)", "Jam Selesai", "Total (Rp)"]
        df_empty = pd.DataFrame(columns=cols)
        df_empty.to_excel(FILE_PEMASUKAN, index=False)
        return df_empty

def load_pengeluaran():
    if os.path.exists(FILE_PENGELUARAN):
        df = pd.read_excel(FILE_PENGELUARAN)
        df["Tanggal_DT"] = pd.to_datetime(df["Tanggal_DT"])
        return df
    else:
        cols = ["No", "Hari", "Tanggal", "Tanggal_DT", "Keterangan", "Nominal (Rp)"]
        df_empty = pd.DataFrame(columns=cols)
        df_empty.to_excel(FILE_PENGELUARAN, index=False)
        return df_empty

df_in = load_pemasukan()
df_out = load_pengeluaran()

# --- MENU NAVIGATION ---
st.sidebar.header("⚙️ Menu Utama")
menu = st.sidebar.radio("Pilih Menu:", [
    "📥 Input Transaksi (Pemasukan)", 
    "📤 Input Pengeluaran", 
    "📊 Ringkasan Keuangan", 
    "✏️ Edit / Hapus Data"
])

# 1. INPUT PEMASUKAN
if menu == "📥 Input Transaksi (Pemasukan)":
    st.sidebar.subheader("Form Pemasukan Rental")
    tanggal = st.sidebar.date_input("Tanggal", datetime.now())
    nama = st.sidebar.text_input("Nama Pelanggan")
    no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=10, value=1)
    durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)
    jam_mulai = st.sidebar.time_input("Jam Mulai", value=datetime.now().time())

    type_ps = TV_MAP.get(no_tv, "PS3")
    tarif = TARIF_PS.get(type_ps, 5000)
    total = durasi * tarif

    waktu_mulai = datetime.combine(tanggal, jam_mulai)
    waktu_selesai = waktu_mulai + timedelta(hours=durasi)

    st.sidebar.info(f"Type: **{type_ps}** | Total: **Rp{total:,}**")

    if st.sidebar.button("💾 Simpan Pemasukan"):
        if not nama:
            st.sidebar.error("Isi nama pelanggan!")
        else:
            no_baru = len(df_in) + 1
            new_row = pd.DataFrame([{
                "No": no_baru,
                "Hari": tanggal.strftime("%A"),
                "Tanggal": tanggal.strftime("%d/%m/%Y"),
                "Tanggal_DT": pd.to_datetime(tanggal),
                "Nama Pelanggan": nama,
                "No TV": no_tv,
                "Type": type_ps,
                "Jam Mulai": jam_mulai.strftime("%H:%M"),
                "Durasi (Jam)": durasi,
                "Jam Selesai": waktu_selesai.time().strftime("%H:%M"),
                "Total (Rp)": total
            }])
            df_in = pd.concat([df_in, new_row], ignore_index=True)
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.sidebar.success("✅ Pemasukan Disimpan!")
            st.rerun()

    st.subheader("📋 Riwayat Pemasukan Terkini")
    st.dataframe(df_in.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 2. INPUT PENGELUARAN
elif menu == "📤 Input Pengeluaran":
    st.sidebar.subheader("Form Pengeluaran")
    tgl_out = st.sidebar.date_input("Tanggal", datetime.now())
    ket_out = st.sidebar.text_input("Keterangan Pengeluaran (Contoh: Beli Token, Service Stik)")
    nom_out = st.sidebar.number_input("Nominal (Rp)", min_value=1000, step=1000, value=10000)

    if st.sidebar.button("💾 Simpan Pengeluaran"):
        if not ket_out:
            st.sidebar.error("Isi keterangan pengeluaran!")
        else:
            no_baru = len(df_out) + 1
            new_row = pd.DataFrame([{
                "No": no_baru,
                "Hari": tgl_out.strftime("%A"),
                "Tanggal": tgl_out.strftime("%d/%m/%Y"),
                "Tanggal_DT": pd.to_datetime(tgl_out),
                "Keterangan": ket_out,
                "Nominal (Rp)": nom_out
            }])
            df_out = pd.concat([df_out, new_row], ignore_index=True)
            df_out.to_excel(FILE_PENGELUARAN, index=False)
            st.sidebar.success("✅ Pengeluaran Disimpan!")
            st.rerun()

    st.subheader("💸 Riwayat Pengeluaran Operasional")
    st.dataframe(df_out.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 3. RINGKASAN KEUANGAN
elif menu == "📊 Ringkasan Keuangan":
    st.subheader("📊 Laporan & Rekapitulasi Keuangan")
    
    periode = st.selectbox("Pilih Periode Laporan:", ["Harian", "Bulanan", "Tahunan"])
    
    df_in_filtered = df_in.copy()
    df_out_filtered = df_out.copy()

    if periode == "Harian":
        pilih_tgl = st.date_input("Pilih Tanggal:", datetime.now())
        df_in_filtered = df_in[df_in["Tanggal_DT"].dt.date == pilih_tgl] if not df_in.empty else df_in
        df_out_filtered = df_out[df_out["Tanggal_DT"].dt.date == pilih_tgl] if not df_out.empty else df_out

    elif periode == "Bulanan":
        col_m, col_y = st.columns(2)
        bulan = col_m.selectbox("Pilih Bulan:", list(range(1, 13)), index=datetime.now().month - 1)
        tahun = col_y.number_input("Pilih Tahun:", value=datetime.now().year)
        
        if not df_in.empty:
            df_in_filtered = df_in[(df_in["Tanggal_DT"].dt.month == bulan) & (df_in["Tanggal_DT"].dt.year == tahun)]
        if not df_out.empty:
            df_out_filtered = df_out[(df_out["Tanggal_DT"].dt.month == bulan) & (df_out["Tanggal_DT"].dt.year == tahun)]

    elif periode == "Tahunan":
        tahun = st.number_input("Pilih Tahun:", value=datetime.now().year)
        if not df_in.empty:
            df_in_filtered = df_in[df_in["Tanggal_DT"].dt.year == tahun]
        if not df_out.empty:
            df_out_filtered = df_out[df_out["Tanggal_DT"].dt.year == tahun]

    # Hitung Total
    tot_pemasukan = df_in_filtered["Total (Rp)"].sum() if not df_in_filtered.empty else 0
    tot_pengeluaran = df_out_filtered["Nominal (Rp)"].sum() if not df_out_filtered.empty else 0
    keuntungan_bersih = tot_pemasukan - tot_pengeluaran

    # Dashboard Metric
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Total Pemasukan", f"Rp{tot_pemasukan:,}")
    col2.metric("🔴 Total Pengeluaran", f"Rp{tot_pengeluaran:,}")
    col3.metric("💰 Keuntungan Bersih", f"Rp{keuntungan_bersih:,}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.write("### Detail Pemasukan")
        st.dataframe(df_in_filtered.drop(columns=["Tanggal_DT"]), use_container_width=True)
    with c2:
        st.write("### Detail Pengeluaran")
        st.dataframe(df_out_filtered.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 4. EDIT / HAPUS DATA
elif menu == "✏️ Edit / Hapus Data":
    st.subheader("🛠️ Kelola / Hapus Data Pemasukan")
    if not df_in.empty:
        no_hapus = st.selectbox("Pilih No Pemasukan yang Akan Dihapus:", df_in["No"].tolist())
        if st.button("❌ Hapus Pemasukan"):
            df_in = df_in[df_in["No"] != no_hapus]
            df_in["No"] = range(1, len(df_in) + 1)
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.success("✅ Data pemasukan terhapus!")
            st.rerun()
