import streamlit as st
import time
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
import streamlit as st
import os

st.set_page_config(page_title="Latihan Nada Mandarin", layout="centered")

# Fungsi untuk merekam audio dan menyimpan sebagai MP3
def record_audio(duration=3, wav_filename="recorded.wav", mp3_filename="recorded.mp3"):
    fs = 22500  # Sampling rate
    st.write("Rekaman dimulai... Silakan berbicara!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Tunggu hingga rekaman selesai
    write(wav_filename, fs, recording)  # Simpan sebagai file WAV
    st.write("Rekaman selesai!")

    # Konversi WAV ke MP3
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")
    st.write(f"Rekaman disimpan sebagai {mp3_filename}")

    return mp3_filename


with open("style.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

query_params = st.query_params['selected_tone']
st.title(f"Mari Latihan *Nada {query_params}*")
st.write("Kamu dapat geser kiri/kanan untuk melihat variasi kata yang dapat dilatih")

# Karakter Nada
characters = [
    {"character": "阿", "tone": "ā"},
    {"character": "妈", "tone": "mā"},
    {"character": "他", "tone": "tā"}
]

# State untuk karakter yang dipilih
if "character_index" not in st.session_state:
    st.session_state.character_index = 0

# Menampilkan karakter
selected_character = characters[st.session_state.character_index]

st.markdown(
    f"<div style='text-align:center;'>"
    f"<p style='font-size:3rem; font-weight:bold;'>{selected_character['character']}</p>"
    f"<p style='font-size:1.5rem; color:#666;'>{selected_character['tone']}</p>"
    f"</div>",
    unsafe_allow_html=True
)

# Tombol navigasi di bawah karakter
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("<"):
        st.session_state.character_index = (st.session_state.character_index - 1) % len(characters)
with col3:
    if st.button(">"):
        st.session_state.character_index = (st.session_state.character_index + 1) % len(characters)

# Pilihan metode rekaman
tab1, tab2 = st.tabs(["Rekam Langsung", "Pilih Audio"])


with tab1:
    if st.button("Mulai Rekam"):
        # Rekam audio selama 3 detik
        output_file = record_audio()
        
        # Tampilkan audio setelah selesai merekam
        if os.path.exists(output_file):
            st.audio(output_file)
            st.success("✅ Rekaman selesai dan audio siap diputar!")
with tab2:
    audio_file = st.file_uploader("Unggah file audio:", type=["mp3"])
    if audio_file:
        st.audio(audio_file, format="audio/wav")
        st.success("✅ Audio berhasil diunggah dan siap diproses.")