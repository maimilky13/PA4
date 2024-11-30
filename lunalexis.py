import streamlit as st
import openai

# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    openai.api_key = api_key
    st.title("Test OpenAI API Key 🔑")
    
    # กล่องข้อความสำหรับใส่ prompt
    user_prompt = st.text_input("Enter a prompt to test OpenAI API:", "Hello, how are you?")
    
    if st.button("Send to OpenAI"):
        try:
            # ใช้ OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt}
                ]
            )
            # แสดงผลลัพธ์
            st.subheader("Response from OpenAI:")
            st.write(response.choices[0].message["content"].strip())
        except Exception as e:
            if "authentication" in str(e).lower():
                st.error("Invalid API Key! Please check and try again.")
            else:
                st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")
