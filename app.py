# --- FUNGSI SOUND NOTIFIKASI MEMAKAI AUDIO NATIVE STREAMLIT ---
def play_sound_alarm():
    sound_url = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
    # Menggunakan st.audio autoplay
    st.audio(sound_url, format="audio/mp3", autoplay=True)

# 1. LIVE DASHBOARD TV & TIMER
if menu == "⏱️ Live Dashboard TV":
    st.subheader("📺 Live Monitoring TV (Auto-Update)")
    now_wib = datetime.now(WIB).replace(tzinfo=None)
    
    # Tombol Manual Tes Suara
    with st.expander("🔊 Tes Suara Alarm (Klik di sini jika suara belum aktif)"):
        st.caption("Klik tombol di bawah untuk memancing izin suara dari browser:")
        if st.button("🔔 Coba Bunyikan Alarm"):
            play_sound_alarm()
    
    cols = st.columns(3)
    tv_habis_info = []
    
    for no_tv in range(1, 7):
        col_idx = (no_tv - 1) % 3
        type_ps = TV_MAP.get(no_tv, "PS3")
        
        tv_active = df_in[(df_in["No TV"] == no_tv) & (df_in["Status"] == "AKTIF")] if not df_in.empty else pd.DataFrame()
        
        with cols[col_idx]:
            if not tv_active.empty:
                row = tv_active.iloc[-1]
                idx = tv_active.index[-1]
                
                jam_selesai_str = str(row["Jam Selesai"]).strip()
                jam_mulai_str = str(row["Jam Mulai"]).strip()
                tgl_dt = pd.to_datetime(row["Tanggal_DT"]).date()
                
                jam_selesai_time = datetime.strptime(jam_selesai_str, "%H:%M").time()
                target_selesai_dt = datetime.combine(tgl_dt, jam_selesai_time)
                
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
                    tv_habis_info.append(f"TV {no_tv} ({row['Nama Pelanggan']})")
                    df_in.at[idx, "Status"] = "SELESAI"
                    df_in.to_excel(FILE_PEMASUKAN, index=False)
            else:
                st.markdown(f"""
                <div class="tv-card tv-kosong">
                    <div class="tv-title">TV {no_tv} ({type_ps})</div>
                    <div class="tv-status">🟢 KOSONG</div>
                    <div class="tv-detail">Siap Disewa</div>
                </div>
                """, unsafe_allow_html=True)

    # Bunyikan alarm jika ada TV habis
    if tv_habis_info:
        st.error(f"🔔 WAKTU HABIS! {', '.join(tv_habis_info)}")
        play_sound_alarm()
