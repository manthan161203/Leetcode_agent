import streamlit as st
import requests
import base64
import logging
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from models import GithubConfig, LeetcodeSolution, ProblemDetails, Explanation
from utils import get_file_extension, get_folder_and_filename, create_solution_file, create_notes
from langchain_core.output_parsers import StrOutputParser
from prompts import problem_prompt, problem_parser, explanation_prompt, explanation_parser, translation_prompt, chat_prompt

# Page Configuration
st.set_page_config(
    page_title="LeetCode GitHub Agent",
    page_icon="🚀",
    layout="centered"
)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session state initialization
if 'github_config' not in st.session_state:
    st.session_state.github_config = {}
if 'google_api_key' not in st.session_state:
    st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY")
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'current_code' not in st.session_state:
    st.session_state.current_code = None
if 'current_language' not in st.session_state:
    st.session_state.current_language = None

# Helper Functions
def configure_github(token, username, repo):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.get("https://api.github.com/user", headers=headers)
        if r.status_code == 200:
            user = r.json().get("login")
            st.session_state.github_config = {
                "github_token": token,
                "github_username": username,
                "github_repo": repo
            }
            return True, f"Connected as {user}"
        return False, "Invalid GitHub token"
    except Exception as e:
        return False, str(e)

def get_llm():
    api_key = st.session_state.google_api_key
    if not api_key:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        max_tokens=8192,
        google_api_key=api_key
    )

def save_solution_logic(problem_statement, code, language, target_languages, problem_name=None):
    if not st.session_state.github_config:
        return False, "GitHub not configured"
    
    llm_instance = get_llm()
    if not llm_instance:
        return False, "Google API Key not configured"

    config = st.session_state.github_config
    headers = {
        "Authorization": f"token {config['github_token']}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Extract Problem Details
        problem_chain = problem_prompt | llm_instance | problem_parser
        problem_details = problem_chain.invoke({"problem_statement": problem_statement})
        
        # 2. Generate Explanation
        explain_chain = explanation_prompt | llm_instance | explanation_parser
        explanation = explain_chain.invoke({
            "problem_statement": problem_statement,
            "code": code,
            "language": language
        })

        # 3. Prepare Files
        extension = get_file_extension(language)
        folder, filename = get_folder_and_filename(
            problem_details.problem_number,
            problem_details.problem_name,
            extension
        )
        code_file = create_solution_file(code, language)
        notes_file = create_notes(problem_details, explanation)

        files_pushed = []

        # Helper to push file to GitHub
        def push_to_github(path, content, message):
            # Check if file exists to get sha
            get_r = requests.get(
                 f"https://api.github.com/repos/{config['github_username']}/{config['github_repo']}/contents/{path}",
                 headers=headers
            )
            sha = get_r.json().get('sha') if get_r.status_code == 200 else None
            
            payload = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha
                payload["message"] = f"Update: {message}"

            r = requests.put(
                f"https://api.github.com/repos/{config['github_username']}/{config['github_repo']}/contents/{path}",
                headers=headers,
                json=payload
            )
            return r.status_code in (200, 201), r.text

        # 4. Push Original Code File
        code_path = f"solutions/{folder}/{filename}"
        success, msg = push_to_github(code_path, code_file, f"Add solution: {problem_details.problem_name} ({language})")
        if success:
            files_pushed.append(code_path)
        else:
            return False, f"GitHub Code push failed: {msg}"

        # 5. Push Notes File
        notes_filename = filename.replace(f".{extension}", ".md")
        notes_path = f"solutions/{folder}/{notes_filename}"
        success, msg = push_to_github(notes_path, notes_file, f"Add notes: {problem_details.problem_name}")
        if success:
            files_pushed.append(notes_path)
        else:
            return False, f"GitHub Notes push failed: {msg}"

        # 6. Handle Translations
        if target_languages:
            translation_chain = translation_prompt | llm_instance | StrOutputParser()
            
            for target_lang in target_languages:
                if target_lang == language:
                    continue
                    
                translated_code = translation_chain.invoke({
                    "source_language": language,
                    "target_language": target_lang,
                    "code": code
                })
                
                target_ext = get_file_extension(target_lang)
                # Use same filename base but different extension
                _, target_filename = get_folder_and_filename(
                    problem_details.problem_number,
                    problem_details.problem_name,
                    target_ext
                )
                
                target_path = f"solutions/{folder}/{target_filename}"
                target_content = create_solution_file(translated_code, target_lang)
                
                success, msg = push_to_github(target_path, target_content, f"Add solution: {problem_details.problem_name} ({target_lang})")
                if success:
                    files_pushed.append(target_path)

        return True, {
            "problem": problem_details.dict(),
            "files_pushed": files_pushed
        }

    except Exception as e:
        return False, str(e)

def main():
    st.title("🚀 LeetCode GitHub Agent")
    st.markdown("Generate notes, translate code, and push solutions to GitHub automatically.")

    # Sidebar: Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google API Key Config
        if not st.session_state.google_api_key:
            st.warning("🔑 Google API Key missing")
            api_key_input = st.text_input("Enter Google API Key", type="password")
            if api_key_input:
                st.session_state.google_api_key = api_key_input
                st.success("API Key saved!")
                st.rerun()
        else:
            st.success("✅ Google API Key Configured")
            if st.button("Change API Key"):
                st.session_state.google_api_key = None
                st.rerun()
        
        st.divider()

        # GitHub Config
        if st.session_state.github_config:
            st.success(f"✅ Connected to GitHub as {st.session_state.github_config.get('github_username')}")
            if st.button("Disconnect GitHub"):
                st.session_state.github_config = {}
                st.rerun()
        else:
            st.warning("❌ GitHub Not Connected")
            with st.form("github_config_form"):
                token = st.text_input("GitHub Token", type="password")
                username = st.text_input("GitHub Username")
                repo = st.text_input("Repository Name", value="leetcode-solutions")
                if st.form_submit_button("Connect"):
                    if token and username:
                        success, msg = configure_github(token, username, repo)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Please fill all fields")

    if not st.session_state.google_api_key:
        st.info("👈 Please enter your Google API Key in the sidebar to continue.")
        st.stop()

    if not st.session_state.github_config:
        st.info("👈 Please configure GitHub in the sidebar to start.")
        st.stop()

    # Tabs
    tab1, tab2 = st.tabs(["📝 Submit Solution", "💬 Chat with Solution"])

    with tab1:
        with st.form("solution_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                problem_name = st.text_input("Problem Name (Optional)", placeholder="e.g. Two Sum")
            with col2:
                language = st.selectbox("Language", ["python", "javascript", "java", "cpp", "go", "rust", "sql"])
                
            problem_statement = st.text_area("Problem Statement", height=150, placeholder="Paste problem description here...")
            code = st.text_area("Solution Code", height=250, placeholder="Paste your code here...")
            
            st.markdown("### 🌐 Auto-Translate")
            target_languages = st.multiselect(
                "Also save in:",
                ["python", "javascript", "java", "cpp", "go", "rust"],
                help="Select languages to automatically translate and save your solution to."
            )
            
            submitted = st.form_submit_button("🚀 Process & Push", type="primary")

        if submitted:
            if not problem_statement or not code:
                st.error("Please provide both problem statement and code.")
            else:
                # Save context for chat
                st.session_state.current_problem = problem_statement
                st.session_state.current_code = code
                st.session_state.current_language = language
                st.session_state.chat_history = [] # Reset chat on new submission

                with st.spinner("Processing... Analyzing, Translating, and Pushing to GitHub..."):
                    success, result = save_solution_logic(problem_statement, code, language, target_languages, problem_name)
                    
                    if success:
                        st.success("✅ Solution saved successfully!")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {result}")

    with tab2:
        st.header("💬 Chat with Your Solution")
        
        if not st.session_state.current_code:
            st.info("Please submit a solution in the 'Submit Solution' tab first to start chatting.")
        else:
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Ask a question about your solution..."):
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate response
                with st.chat_message("assistant"):
                    llm_instance = get_llm()
                    if llm_instance:
                        chat_chain = chat_prompt | llm_instance | StrOutputParser()
                        response = chat_chain.invoke({
                            "problem_statement": st.session_state.current_problem,
                            "language": st.session_state.current_language,
                            "code": st.session_state.current_code,
                            "question": prompt
                        })
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    else:
                        st.error("LLM not initialized")

if __name__ == "__main__":
    main()
