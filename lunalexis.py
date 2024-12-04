import streamlit as st
import openai
import pandas as pd
import jieba  
from pypinyin import pinyin, Style  
import re

# ฟังก์ชันสำหรับการตัดคำและคลีนคำ
def clean_and_tokenize(text):
    # ลบสัญลักษณ์พิเศษและช่องว่างที่ไม่จำเป็น
    text = re.sub(r"[^\u4e00-\u9fff\s]", "", text)  # เก็บเฉพาะตัวอักษรภาษาจีนและช่องว่าง
    text = re.sub(r"\s+", " ", text).strip()  # ลบช่องว่างเกินจำเป็น
    # ตัดคำด้วย jieba
    tokens = jieba.cut(text, cut_all=False)
    return " ".join(tokens)

# ตั้งค่าให้กรอก API Key ในส่วนหลักของหน้า
st.title("LunaLexis 🌖")
st.subheader("Introduction to the App 🥮")
st.text("Welcome to the NLP Application with Preprocessing, an interactive tool designed\nto assist learners and enthusiasts of the Chinese language in exploring and\nanalyzing text. This application integrates advanced natural language processing\ntechniques with OpenAI's GPT capabilities to deliver a comprehensive\nsuite of features, including:")
st.text(' ')
st.text("1. Pinyin Conversion\n2. Summarization\n3. HSK Vocabulary Extraction")
st.text(' ')
st.text('This app is perfect for language learners, educators, and anyone looking to gain\ndeeper insights into Chinese text, whether for study or personal interest.')

st.subheader("OpenAI API key🗝️")
api_key = st.text_input("Enter your OpenAI API key and press enter to apply", type="password")

# ตรวจสอบการกรอก API Key
if api_key:
    st.success("API Key has been entered successfully.")
else:
    st.warning("Please enter your API Key to proceed and press enter to apply.")


if api_key:
    openai.api_key = api_key

    # ส่วนสำหรับกรอกข้อความด้วยมือ
    st.header("Manual Input 🐉")
    user_input = st.text_area("Enter your Chinese text here:", height=150)
    # เพิ่มตัวเลือกระดับความยาก HSK
    st.subheader("Select HSK Level 🐉")
    hsk_level = st.selectbox("Choose the HSK difficulty level (1-6):", ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"])

    if st.button("Process Manual Input"):
        if user_input.strip():
            try:
                # 1. ตัดคำและคลีนข้อความ
                cleaned_text = clean_and_tokenize(user_input)

                # 2. แปลงข้อความเป็นพินอิน
                pinyin_text = ' '.join([syllable[0] for syllable in pinyin(user_input, style=Style.TONE)])

                # 3. สรุปเนื้อหาและแปลเป็นภาษาอังกฤษ
                response = openai.ChatCompletion.create(
    model="gpt-4", 
    messages=[{"role": "user", "content": f"Please summarize the following Chinese article into English, focusing on the main ideas and key information: {user_input}"}],
)
                summary_text = response['choices'][0]['message']['content'].strip()

                # 4. เลือกคำศัพท์ที่น่าสนใจและแปลเป็นภาษาไทย
                keyword_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
Extract 10 interesting keywords from the following Chinese text. 
Each keyword must strictly match the {hsk_level} level as defined by the official HSK vocabulary standard. 
Avoid words outside this level. 
Format the response as a table with '|' separating columns.

Here is an example for HSK 1 level:
你好          | nǐ hǎo  | hello  
谢谢          | xiè xiè | thank you  

The keywords extracted should match the following criteria:
1. The word must belong to the {hsk_level} vocabulary and be relevant to the context.
2. If {hsk_level} is HSK 1, use only HSK 1 vocabulary and skip comparisons with previous levels.
3. For levels HSK 2-6, the word must belong to the {hsk_level} vocabulary and not exist in any previous HSK levels.
4. Select common and relevant words from the text that fit the context.
5. Avoid advanced words or phrases if they exceed the selected level.

Text:
{cleaned_text}
"""
                        }
                    ],
                    max_tokens=300
                )
                keywords_table = keyword_response['choices'][0]['message']['content'].strip()


                # ตรวจสอบว่าผลลัพธ์มีข้อมูลหรือไม่
                if not keywords_table.strip():
                    st.error("No response from OpenAI API. Please check the input or API key.")
                    df_keywords = pd.DataFrame(columns=["Chinese Word", "Pinyin", "English Translation"])  # DataFrame ว่าง

                else:
                    # แปลงตารางผลลัพธ์เป็น DataFrame
                    keywords_list = []
                    for line in keywords_table.split("\n"):
                        if "|" in line:  # ใช้ '|' เป็นตัวแบ่งคอลัมน์
                            parts = [col.strip() for col in line.split("|")]
                            if len(parts) == 3 and parts[0] != "Keyword":  # ตรวจสอบว่ามี 3 คอลัมน์
                                keywords_list.append(parts)

                    # ตรวจสอบว่ามีคำศัพท์ในตารางหรือไม่
                    if keywords_list:
                        df_keywords = pd.DataFrame(keywords_list, columns=["Chinese Word", "Pinyin", "English Translation"])
            
                    else:
                        st.warning("No keywords were extracted. Please check the input or API response format.")
                        df_keywords = pd.DataFrame(columns=["Chinese Word", "Pinyin", "English Translation"])  # DataFrame ว่าง
                        
                # แสดงผล Pinyin (สีแดงอ่อน)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFC1C1;
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 15px;
                        border: 1px solid #FF9999;">
                        <h4 style="color: #D9534F; margin-bottom: 10px;">Pinyin 🧧</h4>
                        <p style="font-size: 16px; line-height: 1.6; color: #333;">{pinyin_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # แสดงผล Summary (สีทองอ่อน)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFD700;
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 15px;
                        border: 1px solid #FFC107;">
                        <h4 style="color: #FF8C00; margin-bottom: 10px;">Summary (English) 🥢</h4>
                        <p style="font-size: 16px; line-height: 1.6; color: #333;">{summary_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # แสดง DataFrame (สีฟ้าอ่อน)
                st.markdown(
                    """
                    <div style="
                        background-color: #E6F7FF;
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 15px;
                        border: 1px solid #91D5FF;">
                        <h4 style="color: #1890FF; margin-bottom: 10px;">Interesting Keywords Table 🀄️</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.dataframe(df_keywords)



            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter some text!")