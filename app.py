import os
import streamlit as st
from openai import OpenAI

# Page Configuration
st.set_page_config(page_title="NeuroParent Assistant", page_icon="🧩", layout="wide")()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------------------------------------------------------
# 1. SIDEBAR: CHILD PROFILES & CONTEXT
# -----------------------------------------------------------------------------
st.sidebar.title("👨‍👩‍👧‍👦 Child Profiles")
st.sidebar.caption("Fill in profile details to personalize AI guidance.")

active_child = st.sidebar.radio("Select Active Child:", ["Child 1", "Child 2"])

# Default Profile Structures
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
        "triggers": "Long verbal instructions, open-ended tasks, emotional rejection sensitivity",
        "strengths": "Creative storytelling, empathetic, highly energetic"
    }
}

# Store Profiles in Session State
if "profiles" not in st.session_state:
    st.session_state.profiles = default_profiles

# Editable Profile Panel for Active Child
with st.sidebar.expander(f"⚙️ Edit {active_child}'s Profile", expanded=False):
    p = st.session_state.profiles[active_child]
    st.session_state.profiles[active_child]["name"] = st.text_input("Name", p["name"])
    st.session_state.profiles[active_child]["age"] = st.number_input("Age", value=int(p["age"]))
    st.session_state.profiles[active_child]["diagnoses"] = st.text_input("Diagnoses / Profile", p["diagnoses"])
    st.session_state.profiles[active_child]["triggers"] = st.text_area("Triggers & Challenges", p["triggers"])
    st.session_state.profiles[active_child]["strengths"] = st.text_area("Strengths & Interests", p["strengths"])

# -----------------------------------------------------------------------------
# 2. CHAT HISTORY INITIALIZATION
# -----------------------------------------------------------------------------
# Maintain distinct chat threads for each child profile
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {"Child 1": [], "Child 2": []}

current_profile = st.session_state.profiles[active_child]
child_name = current_profile["name"]

st.title(f"🧩 Parenting Assistant for {child_name}")
st.caption("Evidence-based parenting advice grounded in UCLA Health, AAP, and pediatric behavioral research.")

# -----------------------------------------------------------------------------
# 3. DYNAMIC SYSTEM PROMPT INJECTION
# -----------------------------------------------------------------------------
BASE_SYSTEM_PROMPT = f"""
You are an expert pediatric parenting assistant specializing in neurodiversity-affirming care. Your advice is grounded in UCLA Health (UC-LEND), the American Academy of Pediatrics (AAP), and clinical neurodivergent care frameworks.

Current Focus Child Profile:
- Name: {current_profile['name']}
- Age: {current_profile['age']}
- Diagnoses/Characteristics: {current_profile['diagnoses']}
- Triggers: {current_profile['triggers']}
- Strengths & Interests: {current_profile['strengths']}

Directives:
1. Grounding: Recommend evidence-based strategies tailored specifically to {child_name}'s profile (e.g., visual schedules, low-arousal co-regulation, single-step commands, sensory adaptations).
2. Leverage Strengths: Use {child_name}'s interests and strengths in proposed solutions when applicable.
3. Tone: Empathic, direct, and actionable for a busy parent.
4. Disclaimer: Remind the user when appropriate that you are an informational assistant, not a clinical provider.
"""

# Render Active Child's Chat History
for message in st.session_state.chat_histories[active_child]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------------------------
# 4. CHAT INPUT & OPENAI INTERACTION
# -----------------------------------------------------------------------------
if user_prompt := st.chat_input(f"Ask something regarding {child_name}..."):
    # Append user message
    st.session_state.chat_histories[active_child].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build message array with injected profile context
    api_messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
    for msg in st.session_state.chat_histories[active_child]:
        api_messages.append({"role": "msg.role", "content": msg["content"]})

    # Query OpenAI Model
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_messages,
                temperature=0.5
            )
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
            
            # Save Assistant response to active child's chat history
            st.session_state.chat_histories[active_child].append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error querying API: {e}")
