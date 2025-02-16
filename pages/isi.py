import streamlit as st
import time
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
import streamlit as st
import numpy as np
import librosa
import tensorflow as tf
import os
import noisereduce as nr
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import database_handler as db
import joblib

st.set_page_config(
    page_title="Mandarin Tone Practice",
    page_icon="✨",
)

scaler = joblib.load("scaler.pkl")

# Load model
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("lstm.keras")
    return model
model = load_model()


def pre_emphasis(signal, alpha=0.97):
    return np.append(signal[0], signal[1:] - alpha * signal[:-1])

def preprocess_audio(file_path, output_file_path):
    SAMPLE_RATE = 22050
    N_MFCC = 60
    MAX_PAD_LEN = 47

    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    
    # Noise reduction
    y = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.5)
    
    # Trim silence
    y, _ = librosa.effects.trim(y, top_db=20)
    
    # Check if the audio is still empty after trimming silence
    if y.size == 0:
        st.error("Maaf, suara tidak terdeteksi setelah diproses. Pastikan Anda berbicara dengan jelas.")
        return None  # Indikasikan bahwa tidak ada data untuk diproses
    
    # Check the duration of the audio
    duration = len(y) / sr
    if duration < 0.01:
        st.error("Maaf, durasi suara terlalu singkat. Tidak ada data yang diperoleh.")
        return None

    # Normalize volume
    y = librosa.util.normalize(y)
    
    # Save the processed audio as mp3
    sf.write(output_file_path, y, sr, format='MP3')

    # Ekstraksi MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)

    # Standarisasi MFCC agar sesuai dengan training
    mfcc_standardized = scaler.transform(mfcc.T).T

    # Padding/truncating agar bentuk MFCC selalu (60, 47)
    if mfcc_standardized.shape[1] < MAX_PAD_LEN:
        pad_width = MAX_PAD_LEN - mfcc_standardized.shape[1]
        mfcc_standardized = np.pad(mfcc_standardized, pad_width=((0, 0), (0, pad_width)), mode='constant')
    elif mfcc_standardized.shape[1] > MAX_PAD_LEN:
        mfcc_standardized = mfcc_standardized[:, :MAX_PAD_LEN]

    # Transpose menjadi (47, 60) untuk model
    mfcc_standardized = mfcc_standardized.T

    # Tambahkan dimensi batch agar bentuk menjadi (1, 47, 60)
    mfcc_standardized = np.expand_dims(mfcc_standardized, axis=0)

    return mfcc_standardized, mfcc, y, sr



# Function to plot MFCC
def plot_mfcc2(audio, sample_rate, title, n_mfcc=60):
    mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    plt.figure(figsize=(6, 4))
    librosa.display.specshow(
        mfcc, x_axis='time', sr=sample_rate, cmap='viridis'
    )
    plt.gca().invert_yaxis()  # Maintain correct orientation
    plt.yticks(range(0, n_mfcc, 5))  # Set y-axis ticks to MFCC indices
    plt.ylabel("MFCC Coefficients")
    plt.title(f"MFCC - {title}")
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    st.pyplot(plt)
    st.write("MFCC shape:", mfcc.shape)

# Fungsi untuk merekam audio dan menyimpan sebagai MP3
def record_audio(duration=3, fs = 22500, wav_filename="recorded.wav", mp3_filename="recorded.mp3"):
    st.toast('Rekaman dimulai silahkan berbicara...', icon='🔴')
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Tunggu hingga rekaman selesai
    write(wav_filename, fs, recording)  # Simpan sebagai file WAV
    st.toast('Rekaman selesai !', icon='🟢')

    # Konversi WAV ke MP3
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")
    st.toast('Rekaman berhasil dikonversi !', icon='🎉')
    os.remove(wav_filename)
    return mp3_filename


with open("style.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

query_params = st.query_params['selected_tone']
st.title(f"Mari Latihan *Nada {query_params}*")
st.write("Kamu dapat geser kiri/kanan untuk melihat variasi kata yang dapat dilatih")

# Karakter Nada
characters = [
    # Nada 1 (ā)
    {"character": "一", "tone": "yī", "mean": "(kb) satu", "tone_number": 1},
    {"character": "妈", "tone": "mā", "mean": "(kb) ibu", "tone_number": 1},
    {"character": "花", "tone": "huā", "mean": "(kb) bunga", "tone_number": 1},
    {"character": "他", "tone": "tā", "mean": "(kb) dia (laki-laki)", "tone_number": 1},
    {"character": "天", "tone": "tiān", "mean": "(kb) langit", "tone_number": 1},
    
    # Nada 2 (á)
    {"character": "麻", "tone": "má", "mean": "(kb) tanaman rami", "tone_number": 2},
    {"character": "没", "tone": "méi", "mean": "(ket) belum", "tone_number": 2},
    {"character": "忙", "tone": "máng", "mean": "(ks) sibuk", "tone_number": 2},
    {"character": "门", "tone": "mén", "mean": "(kb) pintu", "tone_number": 2},
    {"character": "明", "tone": "míng", "mean": "(ks) terang", "tone_number": 2},
    
    # Nada 3 (ǎ)
    {"character": "我", "tone": "wǒ", "mean": "(kb) aku", "tone_number": 3},
    {"character": "手", "tone": "shǒu", "mean": "(kb) tangan", "tone_number": 3},
    {"character": "马", "tone": "mǎ", "mean": "(kb) kuda", "tone_number": 3},
    {"character": "米", "tone": "mǐ", "mean": "(kb) beras", "tone_number": 3},
    {"character": "狗", "tone": "gǒu", "mean": "(kb) anjing", "tone_number": 3},
    
    # Nada 4 (à)
    {"character": "是", "tone": "shì", "mean": "(ket) adalah", "tone_number": 4},
    {"character": "快", "tone": "kuài", "mean": "(ks) cepat", "tone_number": 4},
    {"character": "骂", "tone": "mà", "mean": "(kk) memarahi", "tone_number": 4},
    {"character": "大", "tone": "dà", "mean": "(ks) besar", "tone_number": 4},
    {"character": "看", "tone": "kàn", "mean": "(kk) melihat", "tone_number": 4}
]


# Filter karakter berdasarkan nada yang dipilih
selected_tone = int(query_params)  # Konversi query_params ke integer
filtered_characters = [char for char in characters if char["tone_number"] == selected_tone]

if not filtered_characters:
    st.error("Tidak ada karakter untuk nada ini.")
else:
    # Variabel sesi untuk menyimpan status rekaman atau unggahan
    def get_session_state():
        if 'audio_uploaded' not in st.session_state:
            st.session_state.audio_uploaded = None
        if 'processed_audio' not in st.session_state:
            st.session_state.processed_audio = None
        if 'file_path' not in st.session_state:
            st.session_state.file_path = None
        if "vote" not in st.session_state:
            st.session_state.vote = None
        if "character_index" not in st.session_state:
            st.session_state.character_index = 0
        return st.session_state

    session_state = get_session_state()

    # Batas index agar sesuai dengan jumlah karakter yang difilter
    st.session_state.character_index %= len(filtered_characters)

    # Menampilkan karakter berdasarkan indeks
    selected_character = filtered_characters[st.session_state.character_index]

    st.markdown(
        f"<div style='text-align:center;'><br>"
        f"<p style='font-size:5rem; font-weight:bold;'>{selected_character['character']}</p>"
        f"<p style='font-size:1.5rem;'>{selected_character['tone']}</p>"
        f"<p style='font-size:1rem; color:#666;'>{selected_character['mean']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Tombol navigasi di bawah karakter
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️"):  
            st.session_state.character_index = (st.session_state.character_index - 1) % len(filtered_characters)
    with col3:
        if st.button("➡️"):  # Gunakan encoding HTML untuk tanda >
            st.session_state.character_index = (st.session_state.character_index + 1) % len(filtered_characters)


@st.dialog("Hasil Latihanmu")
def vote(item, image_url=None):
    # Tampilkan gambar di tengah
    if image_url:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{image_url}" width=100px alt="Gambar" style="height: auto;">
            </div><br>
            """,
            unsafe_allow_html=True,
        )

    st.write(item)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Keluar"):
            del st.session_state['vote']  # Hapus vote state
            st.toast("Keluar dari latihan...", icon="✅")  # Notifikasi
            st.write('<meta http-equiv="refresh" content="0; url=/main" />', unsafe_allow_html=True)
    with col2:
        if st.button("Ulangi"): 
            st.session_state['audio_uploaded'] = None  # Reset audio state
            st.session_state['processed_audio'] = None
            st.session_state['file_path'] = None 
            del st.session_state['vote']  # Hapus vote state
            st.rerun()


# Pilihan metode rekaman
tab1, tab2 = st.tabs(["Rekam Langsung", "Pilih Audio"])

with tab1:
    st.write("Jika sudah siap untuk berlatih, klik tombol “Rekam”")
    if st.button("🔴 Rekam") :
        # Rekam audio selama 3 detik
        output_file = None
        output_file = record_audio()
        
        # Tampilkan audio setelah selesai merekam
        if os.path.exists(output_file):
            session_state.audio_uploaded = output_file
            session_state.file_path = output_file
            st.write("Kamu bisa dengarkan ulang suara orisinil kamu")
            st.audio(output_file)
            st.toast('Audio berhasil direkam dan sedang diproses...', icon='🎉')
            
                
with tab2:
    uploaded_file = None
    session_state.processed_audio = None
    uploaded_file = st.file_uploader("Unggah file audio:", type=["mp3"])
    if uploaded_file:
        session_state.audio_uploaded = uploaded_file
        session_state.file_path = uploaded_file
        st.write("Kamu bisa dengarkan ulang suara orisinil kamu")
        st.audio(uploaded_file, format="audio")
        st.toast('Audio berhasil diunggah dan sedang diproses...', icon='🎉')

if session_state.audio_uploaded:
    try:
        if session_state.processed_audio is None:
            # Preprocessing audio
            output_file_path = 'recorded_clean.mp3'
            preprocess_result = preprocess_audio(session_state.file_path, output_file_path)

            if preprocess_result is None or len(preprocess_result) != 4:
                st.error("Gagal memproses audio. Silakan periksa file Anda dan coba lagi.")
                st.stop()
            
            mfcc_features, mfcc, y, sr = preprocess_result

            # Tampilkan audio yang telah diperjelas
            st.text("")
            st.text("")
            st.write("Kamu bisa dengarkan suara kamu setelah diperjelas:")
            st.audio(output_file_path)

            # Simpan hasil preprocessing ke session state
            session_state.processed_audio = (mfcc_features, mfcc, y, sr)
            predictions = model.predict(mfcc_features)

            # Hitung confidence score
            target_label = int(query_params) - 1
            target_confidence = predictions[0][target_label]

            # Label nada
            tone_labels = {0: "Tone 1", 1: "Tone 2", 2: "Tone 3", 3: "Tone 4"}
            predicted_label = np.argmax(predictions, axis=1)[0]
            predicted_tone = tone_labels.get(predicted_label, "Unknown Tone")

            # Evaluasi apakah nada benar
            user_id = "user_123"

            # Tentukan pesan berdasarkan confidence score
            if target_confidence >= 0.6:
                st.balloons()
                correct = True
                st.success(f"Pengucapanmu benar!", icon="✅")
                vote(
                    item=f"**Hebat, pengucapanmu benar!** \n\n{tone_labels[target_label]} diucapkan dengan sangat baik.",
                    image_url="https://img.icons8.com/?size=100&id=7kniG694XSWX&format=png&color=000000",
                )
            elif target_confidence >= 0.4:
                correct = True
                st.success(f"Pengucapanmu hampir benar!", icon="✅")
                vote(
                    item=f"**Hampir Benar!** \n\nCukup benar, namun masih bisa ditingkatkan lebih baik.",
                    image_url="https://img.icons8.com/?size=100&id=gCWKzO-Ww9oS&format=png&color=000000",
                )
            else:
                correct = False
                st.error(f"Yah, pengucapan kamu belum sesuai.. Kamu mengucapkan {predicted_tone}", icon="❌")
                vote(
                    item=f"**Yah, pengucapan kamu belum sesuai.**\n\nKamu cenderung ke {predicted_tone}, bukan {tone_labels[target_label]}.",
                    image_url="https://img.icons8.com/?size=100&id=QEwudVFixKnU&format=png&color=000000",
                )

            db.insert_user_progress(user_id, int(query_params), "", correct)
            if st.toggle("_Dev Mode_") :
                # Tampilkan confidence scores
                st.write("Confidence Scores:")
                st.json({f"Tone {i+1}": f"{score:.2f}" for i, score in enumerate(predictions[0])})

                st.write("Plot MFCC")
                plot_mfcc2(y, sr, title=f"MFCC - {query_params}")
       
    except librosa.util.exceptions.ParameterError:
        st.error("File yang diunggah tidak valid atau tidak didukung. Pastikan Anda mengunggah file audio yang benar.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

    # Statistik pengguna
    if "vote" in st.session_state:
        st.divider()
        # Tampilkan statistik pengguna
        user_id = "user_123"  # Ini bisa diganti dengan ID pengguna yang sebenarnya
        progress = db.get_user_progress(user_id)
        # Siapkan data untuk tabel
        data = []
        for entry in progress:
            tone, hanzi, correct, timestamp = entry
            status = "Benar" if correct else "Salah"
            data.append({"Nada": tone, "Hasil": status, "Waktu": timestamp})

        # Tampilkan tabel menggunakan st.dataframe
        st.write("Statistik Pengguna:")
        st.dataframe(data, use_container_width=True)


st.divider()
st.divider()
st.markdown("""\n\n**Note** :\n
**(kb)**: Kata benda (noun)  
**(ks)**: Kata sifat (adjective)  
**(ket)**: Kata keterangan (adverb)  
**(kk)**: Kata kerja (verb)
""")