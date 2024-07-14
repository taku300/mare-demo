import streamlit as st
from pages import insight_ai

def show():
    # README.mdファイルの内容を読み込む
    with open("README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()
    
    # README.mdの内容を表示する
    st.markdown(readme_content)

if __name__ == "__main__":
    show()
