import streamlit as st
import openai
import pandas as pd
import jieba
from pypinyin import pinyin, Style
import re
import openai.error

# ฟังก์ชันสำหรับการตัดคำและคลีนคำ
def clean_and_tokenize(text):
    text = re.sub(r"[^\u4e00-\u9fff0-9\s]", "", text)  # เก็บเฉพาะตัวอักษรภาษาจีน ตัวเลข และช่องว่าง
    text = re.sub(r"\s+", " ", text).strip()  # ลบช่องว่างเกินจำเป็น
    tokens = jieba.cut(text, cut_all=False)
    return " ".join(tokens)

# ตั้งค่า Sidebar สำหรับกรอก API Key
st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    openai.api_key = api_key

    st.title("LunaLexis 🌖")
    st.subheader("Introduction to the App 🥮")
    st.text("Welcome to the NLP Application with Preprocessing for Chinese Texts.")
    st.text("This app provides summarization, pinyin conversion, and keyword extraction.")

    # ส่วนสำหรับกรอกข้อความ
    st.header("Manual Input 🐉")
    user_input = st.text_area("Enter your Chinese text here:", height=150)

    # ตัวเลือก HSK Level
    st.subheader("Select HSK Level 🐉")
    hsk_level = st.selectbox("Choose the HSK difficulty level (1-6):", ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"])

    if st.button("Process Manual Input"):
        if user_input.strip():
            try:
                with st.spinner("Processing your input..."):
                    # 1. ตัดคำและคลีนข้อความ
                    cleaned_text = clean_and_tokenize(user_input)

                    # 2. แปลงข้อความเป็นพินอิน
                    pinyin_text = ' '.join([syllable[0] for syllable in pinyin(user_input, style=Style.TONE)])

                    # 3. สรุปเนื้อหา
                    try:
                        summary_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": f"Summarize this text into English: {user_input}"}],
                            timeout=20
                        )
                        summary_text = summary_response['choices'][0]['message']['content'].strip()
                    except openai.error.OpenAIError as e:
                        summary_text = f"Error summarizing: {e}"

                    # 4. ดึงคำศัพท์ที่น่าสนใจ
                    try:
                        keyword_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{
                                "role": "user",
                                "content": f"""
Extract 10 keywords from this text at {hsk_level} level. Format as:
Chinese Word | Pinyin | English Translation

Text: {cleaned_text}
"""
                            }],
                            max_tokens=300,
                            timeout=20
                        )
                        keywords_table = keyword_response['choices'][0]['message']['content'].strip()

                        keywords_list = []
                        for line in keywords_table.split("\n"):
                            if "|" in line:
                                parts = [col.strip() for col in line.split("|")]
                                if len(parts) == 3:
                                    keywords_list.append(parts)

                        if keywords_list:
                            df_keywords = pd.DataFrame(keywords_list, columns=["Chinese Word", "Pinyin", "English Translation"])
                        else:
                            df_keywords = pd.DataFrame(columns=["Chinese Word", "Pinyin", "English Translation"])

                    except openai.error.OpenAIError as e:
                        df_keywords = pd.DataFrame(columns=["Chinese Word", "Pinyin", "English Translation"])
                        st.error(f"Error extracting keywords: {e}")

                    # แสดงผลลัพธ์
                    st.subheader("Pinyin 🧧")
                    st.write(f"{pinyin_text}")

                    st.subheader("Summary (English) 🥢")
                    st.write(f"{summary_text}")

                    st.subheader("Interesting Keywords Table 🀄️")
                    st.dataframe(df_keywords)

            except Exception as e:
                st.error(f"Unexpected error: {e}")
        else:
            st.error("Please enter some text!")
else:
    st.error("Please provide a valid OpenAI API key.")
