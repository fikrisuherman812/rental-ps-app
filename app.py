import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Rental PS Dashboard", page_icon="🎮", layout="wide")

# CSS Kustom untuk Mempercantik Tampilan UI
st.markdown("""
<style>
    /* Styling Header */
    .header-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .header-title {
        font-size: 28px;
        font-weight: bold;
        margin: 0;
    }
    .header-subtitle {
        font-size: 14px;
        color: #a5b4fc;
        margin-top: 4px;
    }
    /* Styling Cards Ringkasan Keuangan */
    .metric-card {
        padding: 18px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .card-income { background: linear-gradient(135deg, #059669 0%, #10b981 100%); }
    .card-expense { background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); }
    .card-profit { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); }
    
    .card-label { font-size: 13px; text-transform: uppercase; opacity: 0.9; }
    .card-value { font-size: 24px; margin-top: 6px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

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

# Banner Header Keren
st.markdown("""
<div class="header-banner">
    <div class="header-title">🎮 SISTEM MANAGEMENT RENTAL PLAYSTATION</div>
    <div class="header-subtitle">Pencatatan Transaksi Pemasukan, Pengeluaran & Laporan Keuangan Real-Time</div>
</div>
""", unsafe_allow_html=True)

# --- MENU SIDEBAR ---
st.sidebar.header("⚙️ Navigasi Utama")
menu = st.sidebar.radio("Pilih Halaman:", [
    "📥 Input Transaksi (Pemasukan)", 
    "📤 Input Pengeluaran", 
    "📊 Ringkasan Keuangan", 
    "✏️ Kelola & Edit Data"
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

    st.sidebar.info(f"🎮 Type: **{type_ps}** | Tarif: **Rp{tarif:,}/jam**\n\n💵 Total Bayar: **Rp{total:,}**")

    if st.sidebar.button("💾 Simpan Transaksi", use_container_width=True):
        if not nama:
            st.sidebar.error("Mohon isi nama pelanggan!")
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
            st.sidebar.success("✅ Transaksi Berhasil Disimpan!")
            st.rerun()

    st.subheader("📋 Riwayat Transaksi Pemasukan")
    st.dataframe(df_in.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 2. INPUT PENGELUARAN
elif menu == "📤 Input Pengeluaran":
    st.sidebar.subheader("Form Pengeluaran Operasional")
    tgl_out = st.sidebar.date_input("Tanggal", datetime.now())
    ket_out = st.sidebar.text_input("Keterangan Pengeluaran")
    nom_out = st.sidebar.number_input("Nominal (Rp)", min_value=1000, step=1000, value=10000)

    if st.sidebar.button("💾 Simpan Pengeluaran", use_container_width=True):
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
            st.sidebar.success("✅ Pengeluaran Berhasil Disimpan!")
            st.rerun()

    st.subheader("💸 Riwayat Pengeluaran Operasional")
    st.dataframe(df_out.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 3. RINGKASAN KEUANGAN MODERN
elif menu == "📊 Ringkasan Keuangan":
    st.subheader("📊 Laporan & Analisis Keuangan")
    
    col_p, _ = st.columns([1, 2])
    with col_p:
        periode = st.selectbox("Filter Periode Laporan:", ["Harian", "Bulanan", "Tahunan"])
    
    df_in_filtered = df_in.copy()
    df_out_filtered = df_out.copy()

    if periode == "Harian":
        pilih_tgl = st.date_input("Pilih Tanggal:", datetime.now())
        if not df_in.empty: df_in_filtered = df_in[df_in["Tanggal_DT"].dt.date == pilih_tgl]
        if not df_out.empty: df_out_filtered = df_out[df_out["Tanggal_DT"].dt.date == pilih_tgl]

    elif periode == "Bulanan":
        col_m, col_y = st.columns(2)
        bulan = col_m.selectbox("Pilih Bulan:", list(range(1, 13)), index=datetime.now().month - 1)
        tahun = col_y.number_input("Pilih Tahun:", value=datetime.now().year)
        
        if not df_in.empty: df_in_filtered = df_in[(df_in["Tanggal_DT"].dt.month == bulan) & (df_in["Tanggal_DT"].dt.year == tahun)]
        if not df_out.empty: df_out_filtered = df_out[(df_out["Tanggal_DT"].dt.month == bulan) & (df_out["Tanggal_DT"].dt.year == tahun)]

    elif periode == "Tahunan":
        tahun = st.number_input("Pilih Tahun:", value=datetime.now().year)
        if not df_in.empty: df_in_filtered = df_in[df_in["Tanggal_DT"].dt.year == tahun]
        if not df_out.empty: df_out_filtered = df_out[df_out["Tanggal_DT"].dt.year == tahun]

    # Hitung Kalkulasi Ringkasan
    tot_pemasukan = df_in_filtered["Total (Rp)"].sum() if not df_in_filtered.empty else 0
    tot_pengeluaran = df_out_filtered["Nominal (Rp)"].sum() if not df_out_filtered.empty else 0
    keuntungan_bersih = tot_pemasukan - tot_pengeluaran

    # Menampilkan Metric Cards Berwarna
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"""
    <div class="metric-card card-income">
        <div class="card-label">🟢 Total Pemasukan</div>
        <div class="card-value">Rp {tot_pemasukan:,}</div>
    </div>
    """, unsafe_allow_html=True)

    m2.markdown(f"""
    <div class="metric-card card-expense">
        <div class="card-label">🔴 Total Pengeluaran</div>
        <div class="card-value">Rp {tot_pengeluaran:,}</div>
    </div>
    """, unsafe_allow_html=True)

    m3.markdown(f"""
    <div class="metric-card card-profit">
        <div class="card-label">💰 Keuntungan Bersih</div>
        <div class="card-value">Rp {keuntungan_bersih:,}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detail Tabel Menggunakan Tab
    tab1, tab2 = st.tabs(["📋 Detail Pemasukan", "💸 Detail Pengeluaran"])
    with tab1:
        st.dataframe(df_in_filtered.drop(columns=["Tanggal_DT"]), use_container_width=True)
    with tab2:
        st.dataframe(df_out_filtered.drop(columns=["Tanggal_DT"]), use_container_width=True)

# 4. EDIT & KELOLA DATA
elif menu == "✏️ Kelola & Edit Data":
    st.subheader("🛠️ Kelola / Hapus Data Transaksi")
    if not df_in.empty:
        no_hapus = st.selectbox("Pilih No Pemasukan yang Akan Dihapus:", df_in["No"].tolist())
        if st.button("❌ Hapus Pemasukan", type="primary"):
            df_in = df_in[df_in["No"] != no_hapus]
            df_in["No"] = range(1, len(df_in) + 1)
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.success("✅ Data pemasukan terhapus!")
            st.rerun()
