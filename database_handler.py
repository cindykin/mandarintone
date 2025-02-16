import sqlite3
import os
import pandas as pd

DB_PATH = "mandarin_tones.db"

import os
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Membuat tabel di dalam database
def create_database():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Membuat tabel untuk nada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tones (
                id INTEGER PRIMARY KEY,
                hanzi TEXT,
                nada INTEGER,
                pinyin TEXT,
                arti TEXT,
                audio TEXT
            )
        ''')

        # Membuat tabel untuk progres pengguna
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                nada INTEGER,
                hanzi TEXT,
                correct BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

# Fungsi untuk memasukkan data nada dari CSV
def insert_tones_from_csv(csv_file_path):
    df = pd.read_csv(csv_file_path, sep=";")  # Tambahkan sep=";" untuk delimiter titik koma

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO tones (hanzi, nada, pinyin, arti, audio)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['hanzi'], row['nada'], row['pinyin'], row['arti'], row['audio']))

    conn.commit()
    conn.close()

# Fungsi untuk memasukkan progres pengguna
def insert_user_progress(user_id, nada, hanzi, correct):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_progress (user_id, nada, hanzi, correct)
        VALUES (?, ?, ?, ?)
    ''', (user_id, nada, hanzi, correct))
    conn.commit()
    conn.close()

# Fungsi untuk mendapatkan data nada berdasarkan nada
def get_tones_by_tone_number(nada):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT hanzi, nada, pinyin, arti, audio FROM tones WHERE nada = ?
    ''', (nada,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fungsi untuk mendapatkan progres pengguna
def get_user_progress(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nada, hanzi, correct, timestamp FROM user_progress WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Membuat database dan tabel jika belum ada
create_database()
