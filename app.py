import streamlit as st
from google import genai
from google.genai import types
import os
import tempfile
import dotenv

dotenv.load_dotenv()

st.subheader("System Message")
system_msg = st.text_area("  ", height=150, 
                          placeholder="Write System message...")

st.subheader("Prompt")

col1, col2 = st.columns([3.5,1.5])

with col1:
    prompt = st.text_area("  ", height=120,
                     placeholder="Ask anything..")
with col2:
    pdf = st.file_uploader("  ", type=["pdf"])

def generate():
    
    api_key = os.getenv('API_KEY')
    
    client = genai.Client(
        api_key=api_key,
    )
    
    if pdf is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf.getvalue())
            temp_file_path = temp_file.name
        
        print(f"Temporary file saved at: {temp_file_path}")
        
        try:
            files = [
                client.files.upload(file=temp_file_path)
            ]
            
            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=files[0].uri,
                            mime_type=files[0].mime_type,
                        ),
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=system_msg),
                ],
            )
            
            st.subheader("AI Response")
            response_container = st.empty()
            full_response = ""
            
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
    else:
        st.error("Please upload a PDF file first.")

if st.button("Analyze PDF"):
    if pdf is not None:
            generate()

