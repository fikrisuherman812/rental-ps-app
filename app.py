import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Rental PS Dashboard", page_icon="🎮", layout="wide")

# Zonawaktu WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

def get_now_wib():
    return datetime.now(WIB).replace(tzinfo=None)

# Custom CSS Tampilan Modern
st.markdown("""
<style>
    .header-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .tv-card {
        padding: 16px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .tv-kosong { background: linear-gradient(135deg, #059669 0%, #10b981 100%); }
    .tv-terpakai { background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); }
    .tv-warning { background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); }
    
    .tv-title { font-size: 20px; font-weight: bold; }
    .tv-status { font-size: 14px; margin-top: 4px; text-transform: uppercase; }
    .tv-detail { font-size: 12px; margin-top: 8px; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# File Data
FILE_PEMASUKAN = "data_pemasukan.xlsx"
TARIF_PS = {"PS3": 5000, "PS4": 7500, "PS5": 12000}
TV_MAP = {1: "PS3", 2: "PS4", 3: "PS3", 4: "PS5", 5: "PS4", 6: "PS5"}

# --- SYSTEM LOGIN ---
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if st.session_state["user_role"] is None:
    st.markdown("<h2 style='text-align: center;'>🔐 LOGIN RENTAL PLAYSTATION</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pin = st.text_input("Masukkan PIN Akses:", type="password")
        if st.button("Login", use_container_width=True):
            if pin == "1234":  # PIN Karyawan
                st.session_state["user_role"] = "Karyawan"
                st.rerun()
            elif pin == "9999":  # PIN Owner
                st.session_state["user_role"] = "Owner"
                st.rerun()
            else:
                st.error("PIN Salah! (Default Karyawan: 1234, Owner: 9999)")
    st.stop()

# Logout di Sidebar
st.sidebar.write(f"👤 Login sebagai: **{st.session_state['user_role']}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state["user_role"] = None
    st.rerun()

# --- LOAD DATA ---
def load_pemasukan():
    if os.path.exists(FILE_PEMASUKAN):
        df = pd.read_excel(FILE_PEMASUKAN)
        return df
    else:
        cols = ["No", "Hari", "Tanggal", "Nama Pelanggan", "No TV", "Type", "Jam Mulai", "Durasi (Jam)", "Jam Selesai", "Status", "Total (Rp)"]
        df_empty = pd.DataFrame(columns=cols)
        df_empty.to_excel(FILE_PEMASUKAN, index=False)
        return df_empty

df_in = load_pemasukan()

st.markdown("""
<div class="header-banner">
    <h2 style='margin:0;'>🎮 MONITORING & BILLING RENTAL PS</h2>
</div>
""", unsafe_allow_html=True)

# NAVIGASI BERDASARKAN ROLE
if st.session_state["user_role"] == "Owner":
    menu_options = ["⏱️ Live Dashboard TV", "📥 Input Transaksi", "➕ Tambah Durasi", "📊 Laporan Keuangan (Owner)", "✏️ Edit / Hapus Data"]
else:
    menu_options = ["⏱️ Live Dashboard TV", "📥 Input Transaksi", "➕ Tambah Durasi"]

menu = st.sidebar.radio("Menu Utama:", menu_options)

# 1. LIVE DASHBOARD TV & TIMER (PERBAIKAN SELISIH UTC/WIB)
if menu == "⏱️ Live Dashboard TV":
    st.subheader("📺 Live Monitoring TV")
    now_wib = get_now_wib()
    
    cols = st.columns(3)
    
    for no_tv in range(1, 7):
        col_idx = (no_tv - 1) % 3
        type_ps = TV_MAP.get(no_tv, "PS3")
        
        # Cek transaksi aktif
        tv_active = df_in[(df_in["No TV"] == no_tv) & (df_in["Status"] == "AKTIF")] if not df_in.empty else pd.DataFrame()
        
        with cols[col_idx]:
            if not tv_active.empty:
                row = tv_active.iloc[-1]
                idx = tv_active.index[-1]
                
                jam_selesai_str = str(row["Jam Selesai"])
                jam_mulai_str = str(row["Jam Mulai"])
                tgl_str = str(row["Tanggal"]) # DD/MM/YYYY
                
                # Format objek Datetime berdasarkan Tanggal + Jam Selesai
                target_selesai_dt = datetime.strptime(f"{tgl_str} {jam_selesai_str}", "%d/%m/%Y %H:%M")
                
                # Hitung Selisih Waktu
                sisa_detik = int((target_selesai_dt - now_wib).total_seconds())
                sisa_menit = sisa_detik // 60
                
                if sisa_detik > 0:
                    card_class = "tv-warning" if sisa_menit < 10 else "tv-terpakai"
                    st.markdown(f"""
                    <div class="tv-card {card_class}">
                        <div class="tv-title">TV {no_tv} ({type_ps})</div>
                        <div class="tv-status">🔴 SEDANG MAIN</div>
                        <div class="tv-detail">
                            <b>Pelanggan:</b> {row['Nama Pelanggan']}<br>
                            <b>Mulai:</b> {jam_mulai_str} | <b>Selesai:</b> {jam_selesai_str}<br>
                            <b>Sisa Waktu:</b> {sisa_menit} Menit
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Update otomatis ke SELESAI jika waktu habis
                    df_in.at[idx, "Status"] = "SELESAI"
                    df_in.to_excel(FILE_PEMASUKAN, index=False)
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="tv-card tv-kosong">
                    <div class="tv-title">TV {no_tv} ({type_ps})</div>
                    <div class="tv-status">🟢 KOSONG</div>
                    <div class="tv-detail">Siap Disewa</div>
                </div>
                """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Timer"):
        st.rerun()

# 2. INPUT TRANSAKSI BARU
elif menu == "📥 Input Transaksi":
    st.sidebar.subheader("Form Transaksi")
    now_wib = get_now_wib()
    
    tanggal = st.sidebar.date_input("Tanggal", now_wib.date())
    nama = st.sidebar.text_input("Nama Pelanggan")
    no_tv = st.sidebar.number_input("No TV", min_value=1, max_value=6, value=1)
    durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, value=1)
    jam_mulai = st.sidebar.time_input("Jam Mulai Manual:", value=now_wib.time(), key="input_jam_mulai")

    type_ps = TV_MAP.get(no_tv, "PS3")
    tarif = TARIF_PS.get(type_ps, 5000)
    total = durasi * tarif

    waktu_mulai = datetime.combine(tanggal, jam_mulai)
    waktu_selesai = waktu_mulai + timedelta(hours=durasi)

    st.sidebar.info(f"🎮 Type: **{type_ps}** | Total: **Rp{total:,}**\n\n⏰ Jam Selesai: **{waktu_selesai.time().strftime('%H:%M')}**")

    if st.sidebar.button("💾 Simpan & Mulai Main"):
        if not nama:
            st.sidebar.error("Mohon isi nama!")
        else:
            no_baru = len(df_in) + 1
            new_row = pd.DataFrame([{
                "No": no_baru,
                "Hari": tanggal.strftime("%A"),
                "Tanggal": tanggal.strftime("%d/%m/%Y"),
                "Nama Pelanggan": nama,
                "No TV": no_tv,
                "Type": type_ps,
                "Jam Mulai": jam_mulai.strftime("%H:%M"),
                "Durasi (Jam)": durasi,
                "Jam Selesai": waktu_selesai.time().strftime("%H:%M"),
                "Status": "AKTIF",
                "Total (Rp)": total
            }])
            df_in = pd.concat([df_in, new_row], ignore_index=True)
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.sidebar.success("✅ Transaksi Berhasil Disimpan!")
            st.rerun()

# 3. FITUR TAMBAH DURASI
elif menu == "➕ Tambah Durasi":
    st.subheader("➕ Tambah Waktu Main (Extend)")
    aktif_df = df_in[df_in["Status"] == "AKTIF"]
    
    if aktif_df.empty:
        st.info("Saat ini tidak ada TV yang sedang dipakai.")
    else:
        list_aktif = [f"No {row['No']} - TV {row['No TV']} ({row['Nama Pelanggan']})" for idx, row in aktif_df.iterrows()]
        pilihan = st.selectbox("Pilih Transaksi TV yang Ingin Ditambah Waktu:", list_aktif)
        
        no_transaksi = int(pilihan.split(" - ")[0].replace("No ", ""))
        row_selected = df_in[df_in["No"] == no_transaksi].iloc[0]
        
        tambah_jam = st.number_input("Tambah Durasi (Jam):", min_value=1, value=1)
        tarif_jam = TARIF_PS.get(row_selected["Type"], 5000)
        biaya_tambah = tambah_jam * tarif_jam
        
        st.write(f"💵 Biaya Tambahan: **Rp {biaya_tambah:,}**")
        
        if st.button("💾 Perbarui Durasi"):
            idx = df_in[df_in["No"] == no_transaksi].index[0]
            
            jam_selesai_lama = datetime.strptime(f"{row_selected['Tanggal']} {row_selected['Jam Selesai']}", "%d/%m/%Y %H:%M")
            jam_selesai_baru = jam_selesai_lama + timedelta(hours=tambah_jam)
            
            df_in.at[idx, "Durasi (Jam)"] += tambah_jam
            df_in.at[idx, "Jam Selesai"] = jam_selesai_baru.time().strftime("%H:%M")
            df_in.at[idx, "Total (Rp)"] += biaya_tambah
            
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.success("✅ Waktu Berhasil Ditambahkan!")
            st.rerun()

# 4. LAPORAN KEUANGAN (KHUSUS OWNER)
elif menu == "📊 Laporan Keuangan (Owner)":
    st.subheader("📊 Laporan Pendapatan (Khusus Owner)")
    tot_pemasukan = df_in["Total (Rp)"].sum() if not df_in.empty else 0
    st.metric("Total Pemasukan All-Time", f"Rp {tot_pemasukan:,}")
    st.dataframe(df_in, use_container_width=True)

# 5. EDIT & HAPUS DATA (KHUSUS OWNER)
elif menu == "✏️ Edit / Hapus Data":
    st.subheader("🛠️ Kelola Data Transaksi")
    if not df_in.empty:
        no_hapus = st.selectbox("Pilih No Transaksi yang Akan Dihapus:", df_in["No"].tolist())
        if st.button("❌ Hapus Transaksi"):
            df_in = df_in[df_in["No"] != no_hapus]
            df_in["No"] = range(1, len(df_in) + 1)
            df_in.to_excel(FILE_PEMASUKAN, index=False)
            st.success("✅ Data berhasil dihapus!")
            st.rerun()
