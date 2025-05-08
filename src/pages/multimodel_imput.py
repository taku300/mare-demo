import streamlit as st
import tempfile
import os
from openai import OpenAI
from pydub import AudioSegment
import math
from dotenv import load_dotenv

# .envを読み込む
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

st.title("音声ファイル文字起こしアプリ（長時間対応）")

# 音声ファイルアップロード
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください (mp3, wav, m4a)",
                                 type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.write("文字起こしを開始します。少々お待ちください。")

    # 音声読み込み
    audio = AudioSegment.from_file(file_path)

    # 分割設定（20分単位）
    chunk_length_ms = 20 * 60 * 1000
    total_chunks = math.ceil(len(audio) / chunk_length_ms)

    full_transcript = ""

    for i in range(total_chunks):
        start = i * chunk_length_ms
        end = min((i + 1) * chunk_length_ms, len(audio))
        chunk = audio[start:end]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as chunk_file:
            chunk.export(chunk_file.name, format="mp3")

            with open(chunk_file.name, "rb") as audio_file:
                st.write(f"{i+1}/{total_chunks} チャンク目を文字起こし中...")
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    response_format="text",
                    language="ja"
                )
                full_transcript += transcript + "\n"

            os.remove(chunk_file.name)

    st.subheader("文字起こし結果")
    st.text_area("文字起こしテキスト", full_transcript, height=300)

    # ダウンロードボタン
    st.download_button(
        label="文字起こし結果をダウンロード",
        data=full_transcript,
        file_name="transcription_result.txt",
        mime="text/plain"
    )

    # 後片付け
    os.remove(file_path)
