import streamlit as st
import requests
import os

# Page Configuration
st.set_page_config(
    page_title="LeetCode GitHub Agent",
    page_icon="🚀",
    layout="centered"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Session state initialization
if 'github_configured' not in st.session_state:
    st.session_state.github_configured = False
if 'github_user' not in st.session_state:
    st.session_state.github_user = None

# Helper Functions
def check_api_health():
    try:
        requests.get(f"{API_BASE_URL}/health", timeout=2)
        return True
    except:
        return False

def check_github_status():
    try:
        response = requests.get(f"{API_BASE_URL}/github-status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('configured'):
                st.session_state.github_configured = True
                st.session_state.github_user = data.get('username')
                return True
        return False
    except:
        return False

def configure_github(token, username, repo):
    try:
        response = requests.post(
            f"{API_BASE_URL}/configure-github",
            json={"github_token": token, "github_username": username, "github_repo": repo},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.github_configured = True
            st.session_state.github_user = data.get('user')
            return True, data.get('message', 'Success')
        return False, response.json().get('detail', 'Configuration failed')
    except Exception as e:
        return False, str(e)

def save_solution(problem_statement, code, language, problem_name=None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/save-solution",
            data={
                "problem_statement": problem_statement,
                "code": code,
                "language": language,
                "problem_name": problem_name or ""
            },
            timeout=120
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get('detail', 'Save failed')
    except Exception as e:
        return False, str(e)

def main():
    st.title("🚀 LeetCode GitHub Agent")
    st.markdown("Generate notes and push solutions to GitHub automatically.")

    if not check_api_health():
        st.error("⚠️ API Server is not running. Please start the backend.")
        st.stop()

    # Sidebar: GitHub Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        check_github_status()
        
        if st.session_state.github_configured:
            st.success(f"Connected as {st.session_state.github_user}")
            if st.button("Reconfigure"):
                st.session_state.github_configured = False
                st.rerun()
        else:
            st.warning("Not Connected")
            with st.form("github_config"):
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

    if not st.session_state.github_configured:
        st.info("👈 Please configure GitHub in the sidebar to start.")
        st.stop()

    # Main Form
    with st.form("solution_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            problem_name = st.text_input("Problem Name (Optional)", placeholder="e.g. Two Sum")
        with col2:
            language = st.selectbox("Language", ["python", "javascript", "java", "cpp", "go", "rust", "sql"])
            
        problem_statement = st.text_area("Problem Statement", height=150, placeholder="Paste problem description here...")
        code = st.text_area("Solution Code", height=250, placeholder="Paste your code here...")
        
        submitted = st.form_submit_button("🚀 Process & Push", type="primary")

    if submitted:
        if not problem_statement or not code:
            st.error("Please provide both problem statement and code.")
        else:
            with st.spinner("Processing... Analyzing and pushing to GitHub..."):
                success, result = save_solution(problem_statement, code, language, problem_name)
                
                if success:
                    st.success("✅ Solution saved successfully!")
                    st.json(result)
                else:
                    st.error(f"❌ Error: {result}")

if __name__ == "__main__":
    main()
