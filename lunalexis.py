import streamlit as st
import openai

st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    openai.api_key = api_key
    st.title("Test OpenAI API Key 🔑")

    user_prompt = st.text_input("Enter a prompt to test OpenAI API:", "Hello, how are you?")
    
    if st.button("Send to OpenAI"):
        try:
            # ใช้ฟังก์ชันใหม่ของ OpenAI API
            response = openai.ChatCompletion.chat_create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_prompt}]
            )
            st.subheader("Response from OpenAI:")
            st.write(response['choices'][0]['message']['content'].strip())
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")
