import streamlit as st
import openai

# ตั้งค่า Sidebar สำหรับใส่ API Key
st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    # ตั้งค่า API Key
    openai.api_key = api_key
    
    st.title("Test OpenAI API Key 🔑")
    
    # กล่องข้อความสำหรับใส่ prompt
    user_prompt = st.text_input("Enter a prompt to test OpenAI API:", "Hello, how are you?")
    
    if st.button("Send to OpenAI"):
        try:
            # ทดสอบเรียกใช้งาน OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # แสดงผลลัพธ์ที่ได้
            st.subheader("Response from OpenAI:")
            st.write(response['choices'][0]['message']['content'].strip())
        except openai.error.AuthenticationError:
            st.error("Invalid API Key! Please check and try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")
