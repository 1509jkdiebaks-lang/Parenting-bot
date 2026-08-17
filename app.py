import os
import streamlit as st
import google.generativeai as genai

# 1. PAGE SETUP
st.set_page_config(page_title="NeuroParent Assistant", page_icon="🧩", layout="wide")

# 2. GET API KEY FROM STREAMLIT SECRETS OR ENVIRONMENT
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Gemini API Key missing! Please add GEMINI_API_KEY to your Streamlit App Secrets.")
    st.stop()

# Configure the Gemini client
genai.configure(api_key=api_key)

# 3. SIDEBAR: CHILD PROFILES
st.sidebar.title("👨‍👩‍👧‍👦 Child Profiles")
st.sidebar.caption("Configure profile details to personalize guidance.")

active_child = st.sidebar.radio("Select Active Child:", ["Child 1", "Child 2"])

default_profiles = {
    "Child 1": {
        "name": "Leo",
        "age": 7,
        "diagnoses": "Autism (Level 1), Sensory Processing Sensitivity",
        "triggers": "Loud noises, unexpected routine shifts, itchy clothing tags",
        "strengths": "Deep passion for trains, high visual memory"
    },
    "Child 2": {
        "name": "Maya",
        "age": 10,
        "diagnoses": "ADHD (Combined Type)",
        "triggers": "Long verbal instructions, open-ended tasks, rejection sensitivity",
        "strengths": "Creative storytelling, empathetic, high energy"
    }
}

if "profiles" not in st.session_state:
    st.session_state.profiles = default_profiles

with st.sidebar.expander(f"⚙️ Edit {active_child}'s Profile", expanded=False):
    p = st.session_state.profiles[active_child]
    st.session_state.profiles[active_child]["name"] = st.text_input("Name", p["name"])
    st.session_state.profiles[active_child]["age"] = st.number_input("Age", value=int(p["age"]))
    st.session_state.profiles[active_child]["diagnoses"] = st.text_input("Diagnoses / Profile", p["diagnoses"])
    st.session_state.profiles[active_child]["triggers"] = st.text_area("Triggers & Challenges", p["triggers"])
    st.session_state.profiles[active_child]["strengths"] = st.text_area("Strengths & Interests", p["strengths"])

# 4. CHAT STATE
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {"Child 1": [], "Child 2": []}

current_profile = st.session_state.profiles[active_child]
child_name = current_profile["name"]

st.title(f"🧩 Parenting Assistant for {child_name}")
st.caption("Grounded in pediatric behavioral health and neurodiversity-affirming research.")

BASE_SYSTEM_PROMPT = f"""
You are an expert pediatric parenting assistant specializing in neurodiversity-affirming care. Your advice is grounded in UCLA Health, the American Academy of Pediatrics (AAP), and pediatric behavioral frameworks.

Current Focus Child Profile:
- Name: {current_profile['name']}
- Age: {current_profile['age']}
- Diagnoses/Characteristics: {current_profile['diagnoses']}
- Triggers: {current_profile['triggers']}
- Strengths & Interests: {current_profile['strengths']}

Directives:
1. Recommend evidence-based strategies tailored specifically to {child_name}'s profile.
2. Leverage {child_name}'s interests and strengths in proposed solutions when applicable.
3. Maintain an empathetic, direct tone for a busy parent.
"""

# Render history
for message in st.session_state.chat_histories[active_child]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. CHAT INPUT
if user_prompt := st.chat_input(f"Ask something regarding {child_name}..."):
    st.session_state.chat_histories[active_child].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Initialize Gemini model with instructions
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=BASE_SYSTEM_PROMPT
    )

    # Format history for Google SDK
    contents = []
    for msg in st.session_state.chat_histories[active_child]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [msg["content"]]})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = model.generate_content(contents)
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.chat_histories[active_child].append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error querying Gemini API: {e}")
