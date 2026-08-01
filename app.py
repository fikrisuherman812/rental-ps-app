import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(
    page_title="Database Rental Playstation",
    page_icon="🎮",
    layout="wide"
)

# Initialize Session State (Database sementara di memori)
if "pemasukan" not in st.session_state:
    st.session_state.pemasukan = pd.DataFrame(columns=[
        "No", "Hari", "Tanggal", "No TV", "Type", "Durasi (Jam)", 
        "Jam Mulai", "Jam Selesai", "Tarif/Jam", "Total", "Nama", "Bulan", "Tahun"
    ])

if "pengeluaran" not in st.session_state:
    st.session_state.pengeluaran = pd.DataFrame(columns=[
        "No", "Tanggal", "No PS", "Keterangan", "Tarif / Total", "Bulan", "Tahun"
    ])

# Header Utama
st.title("🎮 DATABASE RENTAL PLAYSTATION")
st.caption("Sistem Kasir & Dashboard Rekapitulasi Performa Rental Bulanan")

# Sidebar - Form Input Transaksi
st.sidebar.header("📝 Form Input Transaksi")
jenis_input = st.sidebar.radio("Pilih Jenis Transaksi:", ["Transaksi Pemasukan", "Transaksi Pengeluaran"])

if jenis_input == "Transaksi Pemasukan":
    st.sidebar.subheader("➕ Tambah Pemasukan")
    
    tgl = st.sidebar.date_input("Tanggal", value=datetime.now())
    nama = st.sidebar.text_input("Nama Pelanggan", value="").strip()
    no_tv = st.sidebar.selectbox("No TV", [1, 2])
    
    # Otomatisasi Type & Tarif
    if no_tv == 1:
        tipe_ps = "PS3"
        tarif_jam = 5000
    else:
        tipe_ps = "PS4"
        tarif_jam = 7500
        
    st.sidebar.info(f"**Type:** {tipe_ps} | **Tarif/Jam:** Rp{tarif_jam:,}")
    
    durasi = st.sidebar.number_input("Durasi (Jam)", min_value=1, max_value=24, value=1)
    jam_mulai_input = st.sidebar.time_input("Jam Mulai", value=datetime.now().time())
    
    # Hitung Jam Selesai & Total
    dt_mulai = datetime.combine(tgl, jam_mulai_input)
    dt_selesai = dt_mulai + timedelta(hours=int(durasi))
    jam_selesai_str = dt_selesai.strftime("%H:%M")
    total_bayar = durasi * tarif_jam
    
    st.sidebar.write(f"⏱️ **Jam Selesai:** {jam_selesai_str}")
    st.sidebar.write(f"💰 **Total Bayar:** Rp{total_bayar:,}")
    
    if st.sidebar.button("💾 Simpan Pemasukan", use_container_width=True):
        if not nama:
            st.sidebar.error("Silakan isi nama pelanggan terlebih dahulu!")
        else:
            hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            new_id = len(st.session_state.pemasukan) + 1
            new_row = {
                "No": new_id,
                "Hari": hari_list[tgl.weekday()],
                "Tanggal": tgl.strftime("%d/%m/%y"),
                "No TV": no_tv,
                "Type": tipe_ps,
                "Durasi (Jam)": durasi,
                "Jam Mulai": jam_mulai_input.strftime("%H:%M"),
                "Jam Selesai": jam_selesai_str,
                "Tarif/Jam": f"Rp{tarif_jam:,}",
                "Total": total_bayar,
                "Nama": nama.upper(),
                "Bulan": bulan_list[tgl.month - 1],
                "Tahun": tgl.year
            }
            st.session_state.pemasukan = pd.concat([st.session_state.pemasukan, pd.DataFrame([new_row])], ignore_index=True)
            st.sidebar.success("✅ Transaksi Pemasukan Berhasil Disimpan!")

else:
    st.sidebar.subheader("➖ Tambah Pengeluaran")
    tgl_exp = st.sidebar.date_input("Tanggal Pengeluaran", value=datetime.now())
    no_ps_exp = st.sidebar.text_input("No PS (Opsional)", value="")
    ket_exp = st.sidebar.text_input("Keterangan Pengeluaran", value="").strip()
    jumlah_exp = st.sidebar.number_input("Nominal Pengeluaran (Rp)", min_value=0, step=5000, value=0)
    
    if st.sidebar.button("💾 Simpan Pengeluaran", use_container_width=True):
        if not ket_exp or jumlah_exp == 0:
            st.sidebar.error("Keterangan dan nominal pengeluaran harus diisi!")
        else:
            bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            new_id_exp = len(st.session_state.pengeluaran) + 1
            new_row_exp = {
                "No": new_id_exp,
                "Tanggal": tgl_exp.strftime("%d/%m/%y"),
                "No PS": no_ps_exp,
                "Keterangan": ket_exp,
                "Tarif / Total": jumlah_exp,
                "Bulan": bulan_list[tgl_exp.month - 1],
                "Tahun": tgl_exp.year
            }
            st.session_state.pengeluaran = pd.concat([st.session_state.pengeluaran, pd.DataFrame([new_row_exp])], ignore_index=True)
            st.sidebar.success("✅ Transaksi Pengeluaran Berhasil Disimpan!")

# Tab Tampilan Utama
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Utama", "🟢 Transaksi Pemasukan", "🔴 Transaksi Pengeluaran"])

with tab1:
    st.subheader("📌 Rekapitulasi Performa Rental Bulanan")
    tahun_pilihan = st.selectbox("Pilih Tahun Dilihat:", [2025, 2026, 2027], index=1)
    
    bulan_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    rekap_data = []
    tot_masuk_tahun = 0
    tot_keluar_tahun = 0
    
    for b in bulan_names:
        # Hitung Pemasukan per Bulan
        df_in = st.session_state.pemasukan
        in_filter = df_in[(df_in["Bulan"] == b) & (df_in["Tahun"] == tahun_pilihan)]
        sum_in = in_filter["Total"].sum() if not in_filter.empty else 0
        
        # Hitung Pengeluaran per Bulan
        df_out = st.session_state.pengeluaran
        out_filter = df_out[(df_out["Bulan"] == b) & (df_out["Tahun"] == tahun_pilihan)]
        sum_out = out_filter["Tarif / Total"].sum() if not out_filter.empty else 0
        
        keuntungan = sum_in - sum_out
        
        if sum_in == 0 and sum_out == 0:
            status = "Belum Ada Data"
        elif keuntungan >= 0:
            status = "UNTUNG"
        else:
            status = "RUGI"
            
        tot_masuk_tahun += sum_in
        tot_keluar_tahun += sum_out
        
        rekap_data.append({
            "Bulan": b,
            "Tahun": tahun_pilihan,
            "Total Pemasukan (Rp)": f"Rp{sum_in:,.0f}",
            "Total Pengeluaran (Rp)": f"Rp{sum_out:,.0f}",
            "Keuntungan Bersih (Rp)": f"Rp{keuntungan:,.0f}",
            "Status Keuangan": status
        })
    
    df_rekap = pd.DataFrame(rekap_data)
    st.dataframe(df_rekap, use_container_width=True, hide_index=True)
    
    # Summary Ringkasan Tahunan
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pemasukan Tahunan", f"Rp{tot_masuk_tahun:,.0f}")
    m2.metric("Total Pengeluaran Tahunan", f"Rp{tot_keluar_tahun:,.0f}")
    c_untung = tot_masuk_tahun - tot_keluar_tahun
    m3.metric("Keuntungan Bersih Tahunan", f"Rp{c_untung:,.0f}", delta="UNTUNG" if c_untung >= 0 else "RUGI")

with tab2:
    st.subheader("🟢 Data Transaksi Pemasukan")
    if not st.session_state.pemasukan.empty:
        df_show_in = st.session_state.pemasukan.copy()
        df_show_in["Total"] = df_show_in["Total"].apply(lambda x: f"Rp{x:,.0f}")
        st.dataframe(df_show_in, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data transaksi pemasukan.")

with tab3:
    st.subheader("🔴 Data Transaksi Pengeluaran")
    if not st.session_state.pengeluaran.empty:
        df_show_out = st.session_state.pengeluaran.copy()
        df_show_out["Tarif / Total"] = df_show_out["Tarif / Total"].apply(lambda x: f"Rp{x:,.0f}")
        st.dataframe(df_show_out, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data transaksi pengeluaran.")