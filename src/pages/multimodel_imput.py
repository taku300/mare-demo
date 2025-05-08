import streamlit as st
import tempfile
import os
from openai import OpenAI
from dotenv import load_dotenv

# .envを読み込む
load_dotenv()

# OpenAI APIキー取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

st.title("音声ファイル文字起こしアプリ")

# 音声ファイルアップロード
uploaded_file = st.file_uploader(
    "音声ファイルをアップロードしてください (mp3, wav, m4a)",
    type=["mp3", "wav", "m4a"]
)

if uploaded_file is not None:
    # 一時ファイルに保存
    file_extension = uploaded_file.name.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.write("文字起こしを開始します。少々お待ちください。")

    # OpenAI API で文字起こし
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            response_format="text",
            language="ja"
        )

    # 結果表示
    st.subheader("文字起こし結果")
    st.text_area("文字起こしテキスト", transcript, height=300)

    # ダウンロードボタン
    st.download_button(
        label="文字起こし結果をダウンロード",
        data=transcript,
        file_name="transcription_result.txt",
        mime="text/plain"
    )

    # 一時ファイル削除
    os.remove(file_path)
