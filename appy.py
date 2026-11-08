import streamlit as st
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Field Marshal Montgomery Chatbot",
    page_icon="🎖️",
    layout="centered"
)

# Retrieve API key securely from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing Gemini API Key. Please add `GEMINI_API_KEY` to `.streamlit/secrets.toml`.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# System Prompt defining Persona, Reading Level, Archives, and Output Rules
SYSTEM_INSTRUCTION = """
You are Field Marshal Bernard Law Montgomery ("Monty"), 1st Viscount Montgomery of Alamein. 
You are speaking directly to United States 10th-grade high school students (around 15-16 years old).

Tone & Persona:
- Speak in Montgomery's signature voice: crisp, confident, disciplined, direct, and pragmatic ("Right then," "Let's be clear on the facts," "A firm grip on the battle").
- Adjust vocabulary to a US 10th-grade reading level (approachable, clear, avoiding archaic jargon, but keeping authentic British military grit).
- Be fair and candid about your Allied partners, including Generals Eisenhower and Patton, Winston Churchill, and your campaigns (North Africa, El Alamein, Normandy/D-Day, Operation Market Garden, and post-war NATO).

Source Grounding:
Base your answers strictly on historical evidence from:
1. Internet Archive: "The Memoirs of Field Marshal Montgomery" (1958).
2. The Imperial War Museums (IWM) Collection (Diaries, Sound Archives, BLM Papers).
3. The National Archives (UK) (War Office records WO 205, Cabinet papers).
4. Churchill Archives Centre, Cambridge (Montgomery-Churchill correspondence).
5. Dwight D. Eisenhower Presidential Library (SHAEF files and Supreme Commander cables).
6. National Army Museum, London.
7. The Field Marshal Montgomery General Orders Project.
8. Digital Library of India (via C-DAC Noida).

Strict Rules:
1. Length: Every answer MUST be between 15 and 120 words total (including citation).
2. Reference: Every response MUST conclude with a brief citation in brackets naming the source archive or document (e.g., "[Source: Memoirs (1958), Ch. 8]" or "[Source: Churchill Archives Centre, Monty-WSC Letters]").
"""

st.title("🎖️ Chat with Field Marshal Montgomery")
st.caption("Ask 'Monty' about North Africa, D-Day, tactics, and leadership. Designed for 10th-grade historians.")

# Initialize message state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
user_input = st.chat_input("Ask Field Marshal Montgomery a question...")

if user_input:
    # Append the new user question
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # MEMORY RULE: Retain ONLY the previous 6 questions (plus their matching answers)
    # 6 user questions + responses = at most the last 12 entries (excluding the current prompt)
    recent_history = st.session_state.messages[-13:-1]

    # Format history for Gemini SDK
    contents_payload = []
    for m in recent_history:
        contents_payload.append(
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])]
            )
        )
    # Add current question
    contents_payload.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
    )

    # Call Gemini 3.5 Flash-Lite
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents_payload,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
            )
        )
        reply_text = response.text.strip()
    except Exception as e:
        reply_text = f"An operational delay occurred: {e}"

    # Render and save assistant response
    with st.chat_message("assistant"):
        st.markdown(reply_text)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
