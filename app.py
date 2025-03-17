import streamlit as st
from google import genai
from google.genai import types
import os
import tempfile
import dotenv

dotenv.load_dotenv()

st.subheader("System Message")
system_msg = st.text_area("  ", height=150, placeholder="Write System message...")

# Create columns to place chat input and file uploader side by side
col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.chat_input("Ask anything...")

with col2:
    pdf = st.button(st.file_uploader("Upload PDF", type=["pdf"]))

def generate():
    api_key = os.getenv('API_KEY')

    client = genai.Client(api_key=api_key)

    if pdf is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf.getvalue())
            temp_file_path = temp_file.name

        print(f"Temporary file saved at: {temp_file_path}")

        try:
            files = [client.files.upload(file=temp_file_path)]

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
                system_instruction=[types.Part.from_text(text=system_msg)],
            )

            st.subheader("AI Response")
            response_container = st.empty()
            full_response = ""

            for chunk in client.models.generate_content_stream(
                model=model, contents=contents, config=generate_content_config
            ):
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response)

        except Exception as e:
            st.error(f"Error: {str(e)}")

    else:
        st.error("Please upload a PDF file first.")

# Automatically trigger the function when the user inputs text
if prompt:
    generate()

st.subheader("Subject Prompts - Press the button to get the Prompt")

col3, col4, col5, col6, col7 = st.columns([1, 1.2, 1, 1, 1])
selected_subject = None  

with col3:
    if st.button("Physics"):
        selected_subject = "Physics"

with col4:
    if st.button("Chemistry"):
        selected_subject = "Chemistry"

with col5:
    if st.button("Biology"):
        selected_subject = "Biology"

with col6:
    if st.button("Maths"):
        selected_subject = "Maths"

with col7:
    if st.button("Gujarati"):
        selected_subject = "Gujarati"

if selected_subject:
    st.subheader(f"{selected_subject} Prompts")

    prompts = {
        "Physics": """
        - આ પ્રકરણને સૌથી સરળ રીતે સમજાવો
        - આ પ્રકરણ મને વાસ્તવિક જીવનના ઉદાહરણો સાથે સમજાવો. 
        - આ પ્રકરણમાં આવતા વિવિધ મુદ્દાઓની વ્યાખ્યા આપો
        - મને આ વિષયને લગતા વિવિધ પરીક્ષાલક્ષી દાખલા આપો.
        - વાસ્તવિક જીવનમાં આ પ્રકરણનું શું મહત્વ છે?   
        """,
        "Chemistry": """
        - આ પ્રકરણમાં આવતા વિવિધ રાસાયણિક સમીકરણોની યાદી બનાવો.
        - આ રાસાયણિક પ્રક્રિયાનું સમીકરણ અને પરિણામ શું છે? આ રાસાયણિક પ્રક્રિયાનો ઉપયોગ પણ જણાવો.
        - આ પ્રકરણમાં કઈ મૂળભૂત બાબતો મને ઝડપથી શીખવામાં મદદ કરશે?
        - આ પ્રકરણ સમજવા માટે મને મદદરૂપ "notes" આપો.
        - આ પ્રકરણને લાંબા સમય સુધી યાદ રાખવાની શ્રેષ્ઠ રીત કઈ છે? 
        """,
        "Biology": """
        - આ પ્રકરણમાંથી મને મહત્વપૂર્ણ મુદ્દાઓ આપો.
        - આ પ્રકરણ સમજવા માટે મને મદદરૂપ notes  આપો.  
        - શું તમે આ મુદ્દાને એવી રીતે સમજાવી શકો છો કે તેઓ એક દેશ છે?
        - આ પ્રકરણના બધા જ પારિભાષિક શબ્દો સરળ શબ્દોમાં સમજાવો. 
        - આ પ્રકરણને અસરકારક રીતે સમજવા માટે મને તેનો એક Roadmap આપો. 
        """,
        "Maths": """
        - આ પ્રકરણમાં આવતા સૂત્રની યાદી આપો.
        - આ દાખલા ને સૌથી સરળ અને અસરકારક રીતે ઉકેલો.  
        - આ પ્રકરણને લગતા વિવિધ દાખલા પ્રેક્ટિસ માટે આપો. 
        - આ પ્રકરણ માં આવતી થિયરી સમજાવો.
        - આ પ્રકરણમાંથી પરીક્ષાલક્ષી MCQ પ્રશ્ન આપો.
        """,
        "Gujarati": """
        - આ પ્રકરણની વાર્તાનો સારાંશ લગભગ 50 શબ્દોમાં આપો. 
        - આ પ્રકરણનો કૃતિ અને કર્તા પરિચય આપો,
        - આ પ્રકરણના સમાનાર્થી, વિરોધી શબ્દો, રૂઢિપ્રયોગો,કહેવત,શબ્દસમૂહ,વગેરે આપો.  
        - આ પ્રકરણમાં આપેલા પ્રશ્નનો વિસ્તારથી લગભગ ૧૦૦ શબ્દો માં જવાબ આપો. 
        - આ પ્રકરણમાંથી પરીક્ષામાં કયા પ્રશ્નો હોઈ શકે?  
        """
    }

    st.markdown(prompts[selected_subject]) 
