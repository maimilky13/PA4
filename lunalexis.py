import streamlit as st
import openai
import pandas as pd
import jieba
from pypinyin import pinyin, Style
import re


def clean_and_tokenize(text):
    text = re.sub(r"[^\u4e00-\u9fff\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()  
    tokens = jieba.cut(text, cut_all=False)
    return " ".join(tokens)


st.title("LunaLexis 🌖")
st.subheader("Introduction to the App 🥮")
st.text('Welcome to LunaLexis: The NLP Application')
st.write("LunaLexis is an interactive tool designed to assist learners and enthusiasts of the Chinese language in exploring and analyzing text. This application integrates advanced natural language processing techniques with OpenAI's GPT capabilities to deliver a comprehensive suite of features, including:")
st.text(' ')
st.text("1. Pinyin Conversion\n2. Summarization \n3. HSK Vocabulary Extraction")
st.text(' ')
st.write('Additionally, LunaLexis offers the unique ability to filter and select vocabulary based on HSK levels, ranging from Level 1 (beginner) to Level 6 (advanced). This feature allows users to focus on words appropriate to their proficiency, making it a valuable resource for learners at any stage of their language journey.')

st.subheader("OpenAI API key🗝️")
api_key = st.text_input(
    "Enter your OpenAI API key and press enter to apply", type="password")

if api_key:
    st.success("API Key has been entered successfully.")
else:
    st.warning("Please enter your API Key to proceed and press enter to apply.")


if api_key:
    openai.api_key = api_key

    st.subheader("Chinese Text (Manual Input) 🐉")
    user_input = st.text_area("Enter your Chinese text here:", height=200)

    st.subheader("Select HSK Level 🐉")
    hsk_level = st.selectbox("Choose the HSK difficulty level (1-6):",
                             ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"])

    if st.button("Process Manual Input"):
        if user_input.strip():
            try:
                cleaned_text = clean_and_tokenize(user_input)

                pinyin_text = ' '.join(
                    [syllable[0] for syllable in pinyin(user_input, style=Style.TONE)])

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "user", 
                            "content": f"""
Please summarize the following Chinese text into English. Your summary should:
1. Focus on the key points and main ideas of the text.
2. Avoid directly translating the text word for word.
3. Use concise and clear language to convey the essence of the text.
4. Limit the summary to to 50-100 words. Ensure it captures the main points clearly.

Text:
{user_input}
"""
                        }
                    ],
                )
                summary_text = response['choices'][0]['message']['content'].strip(
                )

                keyword_response = openai.ChatCompletion.create(
                    model="gpt-4",
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
                keywords_table = keyword_response['choices'][0]['message']['content'].strip(
                )

                if not keywords_table.strip():
                    st.error(
                        "No response from OpenAI API. Please check the input or API key.")
                    df_keywords = pd.DataFrame(
                        columns=["Chinese Word", "Pinyin", "English Translation"])

                else:
                    keywords_list = []
                    for line in keywords_table.split("\n"):
                        if "|" in line:  
                            parts = [col.strip() for col in line.split("|")]
                            if len(parts) == 3 and parts[0] != "Keyword":
                                keywords_list.append(parts)

                    if keywords_list:
                        df_keywords = pd.DataFrame(keywords_list, columns=[
                                                   "Chinese Word", "Pinyin", "English Translation"])
                        df_keywords.index = range(1, len(df_keywords) + 1)
                    else:
                        st.warning(
                            "No keywords were extracted. Please check the input or API response format.")
                        df_keywords = pd.DataFrame(
                            columns=["Chinese Word", "Pinyin", "English Translation"])

                clean_pinyin = re.sub(r"<[^>]*>", "", pinyin_text).strip()
                clean_pinyin = re.sub(r"\s+", " ", clean_pinyin).strip()

                st.markdown(
                    f"""
                    <div style="
                        background-color: #2A3F5E;
                        border-radius: 20px;
                        padding: 15px;
                        margin: 20px 0;  
                        border: 1px solid #000000;">
                        <h4 style="color: #D8C8B8; margin-bottom: 10px;">Pinyin 🧧</h4>
                        <p style="font-size: 16px; line-height: 1.6; color: white ; font-family: Arial, sans-serif;">
                        {clean_pinyin}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                clean_summary = re.sub(r"<[^>]*>", "", summary_text).strip()
                clean_summary = re.sub(r"\s+", " ", clean_summary).strip()

                st.markdown(
                    f"""
                    <div style="
                        background-color: #042D29;
                        border-radius: 20px;
                        padding: 15px;
                        margin: 20px 0; 
                        border: 1px solid #000000;">
                        <h4 style="color: #D8C8B8; margin-bottom: 10px;">Summary (English) 🥢</h4>
                        <p style="font-size: 16px; line-height: 1.6; color: white; font-family: Arial, sans-serif;">
                        {clean_summary}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <div style="
                        background-color: #451011; 
                        border-radius: 20px;  
                        padding: 10px;  
                        margin: 20px 0;  
                        border: 1px solid #000000;">
                        <h4 style="color: #D8C8B8; margin-bottom: 5px;">Interesting Keywords Table 🀄️</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.dataframe(df_keywords)

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter some text!")
