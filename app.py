import os
import base64
import logging
import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from models import GithubConfig, LeetcodeSolution, ProblemDetails, Explanation
from utils import get_file_extension, get_folder_and_filename, create_solution_file, create_notes
from llm import llm, problem_prompt, problem_parser, explanation_prompt, explanation_parser

# LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# FASTAPI SETUP
app = FastAPI(title="LeetCode GitHub Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GITHUB CONFIG
github_config = {}

# ROUTES
@app.post("/configure-github")
async def configure_github(config: GithubConfig):
    global github_config
    github_config = config.dict()

    headers = {
        "Authorization": f"token {config.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        r = requests.get("https://api.github.com/user", headers=headers)
        if r.status_code == 200:
            user = r.json().get("login")
            logger.info(f"✅ GitHub connected: {user}")
            return {"status": "success", "user": user, "message": f"Connected as {user}"}
        else:
            raise HTTPException(status_code=401, detail="Invalid GitHub token.")
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-solution")
async def save_solution(solution: LeetcodeSolution = Depends(LeetcodeSolution.as_form)):
    if not github_config:
        raise HTTPException(status_code=400, detail="GitHub not configured. Call /configure-github first")

    headers = {
        "Authorization": f"token {github_config['github_token']}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        logger.info("🔍 Extracting problem details...")
        problem = problem_prompt | llm | problem_parser
        problem_details: ProblemDetails = problem.invoke(
            {"problem_statement": solution.problem_statement}
        )
        logger.info(f"✅ Problem extracted: {problem_details.problem_name}")
    except Exception as e:
        logger.error(f"❌ Problem parsing error: {e}")
        raise HTTPException(500, f"Failed to extract problem details: {e}")

    try:
        logger.info("📝 Generating explanation...")
        explain = explanation_prompt | llm | explanation_parser
        explanation: Explanation = explain.invoke({
            "problem_statement": solution.problem_statement,
            "code": solution.code,
            "language": solution.language
        })
        logger.info("✅ Explanation generated")
    except Exception as e:
        logger.error(f"❌ Explanation parsing error: {e}")
        raise HTTPException(500, f"Failed to generate explanation: {e}")

    # Get folder and filename
    extension = get_file_extension(solution.language)
    folder, filename = get_folder_and_filename(
        problem_details.problem_number,
        problem_details.problem_name,
        extension
    )

    code_file = create_solution_file(solution.code, solution.language)
    notes_file = create_notes(problem_details, explanation)

    try:
        files_pushed = []

        # CODE FILE
        code_path = f"solutions/{folder}/{filename}"
        logger.info(f"📤 Pushing code file: {code_path}")
        r = requests.put(
            f"https://api.github.com/repos/{github_config['github_username']}/"
            f"{github_config['github_repo']}/contents/{code_path}",
            headers=headers,
            json={
                "message": f"Add solution: {problem_details.problem_name} ({solution.language})",
                "content": base64.b64encode(code_file.encode()).decode(),
                "branch": "main"
            }
        )
        if r.status_code in (200, 201):
            files_pushed.append(code_path)
            logger.info(f"✅ Code file pushed")
        else:
            raise HTTPException(500, f"GitHub Code push failed: {r.text}")

        # NOTES FILE
        notes_filename = filename.replace(f".{extension}", ".md")
        notes_path = f"solutions/{folder}/{notes_filename}"
        logger.info(f"📤 Pushing notes file: {notes_path}")
        r = requests.put(
            f"https://api.github.com/repos/{github_config['github_username']}/"
            f"{github_config['github_repo']}/contents/{notes_path}",
            headers=headers,
            json={
                "message": f"Add notes: {problem_details.problem_name}",
                "content": base64.b64encode(notes_file.encode()).decode(),
                "branch": "main"
            }
        )
        if r.status_code in (200, 201):
            files_pushed.append(notes_path)
            logger.info(f"✅ Notes file pushed")
        else:
            raise HTTPException(500, f"GitHub Notes push failed: {r.text}")

        logger.info(f"🎉 Solution saved successfully!")
        return {
            "status": "success",
            "problem": problem_details.dict(),
            "files_pushed": files_pushed,
            "folder_structure": f"solutions/{folder}/"
        }

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, f"GitHub upload failed: {e}")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "LeetCode GitHub Agent API is running",
        "model": "gemini-2.5-flash-lite"
    }

@app.get("/github-status")
async def github_status():
    if github_config:
        return {
            "configured": True,
            "username": github_config.get('github_username'),
            "repo": github_config.get('github_repo')
        }
    return {"configured": False, "message": "GitHub not configured yet"}
