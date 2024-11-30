import streamlit as st
import openai

# ตั้งค่า API Key
st.sidebar.title("API Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if api_key:
    openai.api_key = api_key
    st.title("Test OpenAI API Key 🔑")

    # Prompt Input
    user_prompt = st.text_input("Enter a prompt to test OpenAI API:", "Hello, how are you?")
    
    if st.button("Send to OpenAI"):
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=user_prompt,
                max_tokens=50
            )
            st.subheader("Response from OpenAI:")
            st.write(response.choices[0].text.strip())
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")
