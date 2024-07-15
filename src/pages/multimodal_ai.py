from configs import const
import base64
import requests
import os
import re
import pandas as pd
import streamlit as st
from PIL import Image as PILImage
import io
import json
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate, LLMChain

def encode_image(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def mask_api_key(api_key):
    return api_key[:4] + "****" + api_key[-4:]

def show():
    st.title("画像解析アプリ")

    uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = PILImage.open(io.BytesIO(uploaded_file.read()))
        st.image(image, caption="アップロードされた画像", use_column_width=True)

        # 画像をBase64エンコード
        base64_image = encode_image(image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {const.OPENAI_API_KEY}"
        }

        prompt = "この画像について教えてください。"

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        if st.button("解析"):
            # 画像解析の実行
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                st.success("### 解析結果:")
                st.write(result)

                # LLMを使用して料理名を推測
                llm = ChatOpenAI(api_key=os.environ['OPENAI_API_KEY'], model_name="gpt-4o", max_tokens=1500)

                prompt_template = PromptTemplate(
                    input_variables=["description"],
                    template="""
                    材料情報を参考にどんな料理ができるか推測してください。
                    その後回答形式に従って回答を出力してください。

                    # 材料情報
                    {description}

                    # 回答形式
                    料理名：[ここに料理名]
                    """
                )

                llm_chain = LLMChain(prompt=prompt_template, llm=llm)
                description = result
                dish_result = llm_chain.run(description=description)
                st.write("### こんな料理を作ることができます")
                dish_name_match = re.search(r'料理名：(.+)', dish_result)
                if dish_name_match:
                    dish_name = dish_name_match.group(1)
                    st.markdown(f"料理名: {dish_name}")

                    # リクエストのJSON
                    params = {
                        'key': const.GOOGLE_API_KEY,
                        'query': dish_name,  # 検索キーワード
                        'language': 'ja'  # 日本語での結果を取得
                    }

                    masked_params = params.copy()
                    masked_params['key'] = mask_api_key(params['key'])

                    st.write("### リクエストのJSON")
                    st.json(masked_params)

                    # 店舗情報の取得と表示
                    response = requests.get(const.PLACES_API_ENDPOINT, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        if data['status'] == 'OK':
                            results = []
                            for place in data['results']:
                                name = place['name']
                                address = place.get('formatted_address', '住所情報なし')
                                rating = place.get('rating', '評価なし')
                                user_ratings_total = place.get('user_ratings_total', '評価数なし')
                                geometry = place.get('geometry', {}).get('location', '位置情報なし')
                                results.append({
                                    '店名': name,
                                    '住所': address,
                                    '評価': rating,
                                    '評価合計': user_ratings_total,
                                    '位置情報': geometry
                                })

                            df = pd.DataFrame(results)
                            df = df.sort_values(by='評価', ascending=False)
                            st.write("### 店舗情報")
                            st.dataframe(df)
                        else:
                            st.error(f"APIリクエストが失敗しました。ステータス: {data['status']}, エラーメッセージ: {data.get('error_message', 'なし')}")
                    else:
                        st.error(f"HTTPリクエストが失敗しました。ステータスコード: {response.status_code}")

                else:
                    st.write("料理名を推測できませんでした。")

            else:
                st.error("解析に失敗しました。")
                st.write(response.json())

if __name__ == "__main__":
    show()
