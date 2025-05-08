import streamlit as st
import tempfile
import os
from openai import OpenAI
from pydub import AudioSegment
import math
from dotenv import load_dotenv  # 追加

# .envを読み込む
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
st.write(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
client = OpenAI(api_key=OPENAI_API_KEY)

st.title("音声・動画ファイル文字起こしアプリ（長時間対応）")

# ファイルアップロード
uploaded_file = st.file_uploader("音声または動画ファイルをアップロードしてください (mp3, wav, m4a, mp4, mov, avi, mkv)",
                                 type=["mp3", "wav", "m4a", "mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    # 動画ファイルの場合は音声抽出
    if file_extension in ["mp4", "mov", "avi", "mkv"]:
        st.write("動画ファイルがアップロードされました。音声を抽出します。")
        audio_path = file_path + ".mp3"
        video = AudioSegment.from_file(file_path)
        video.export(audio_path, format="mp3")
        target_audio_path = audio_path
    else:
        st.write("音声ファイルがアップロードされました。")
        target_audio_path = file_path

    st.write("文字起こしを開始します。少々お待ちください。")

    # 音声読み込み
    audio = AudioSegment.from_file(target_audio_path)

    # 分割設定
    chunk_length_ms = 20 * 60 * 1000  # 20分（制限より少し短くするため）
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
    if file_extension in ["mp4", "mov", "avi", "mkv"]:
        os.remove(audio_path)
