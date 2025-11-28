import re
from typing import Optional
from datetime import datetime
from models import ProblemDetails, Explanation

def extract_problem_number(problem_name: str, problem_number: Optional[int]) -> tuple:
    """Extract problem number from name or use provided number"""
    if problem_number:
        return problem_number, problem_name
    
    match = re.match(r"^(\d+)\.\s*(.+)$", problem_name.strip())
    if match:
        return int(match.group(1)), match.group(2).strip()
    
    return None, problem_name

def get_file_extension(language: str) -> str:
    extensions = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "csharp": "cs",
        "go": "go",
        "rust": "rs",
        "sql": "sql",
        "swift": "swift"
    }
    return extensions.get(language.lower(), "txt")

def get_folder_and_filename(problem_number: Optional[int], problem_name: str, extension: str) -> tuple:
    """Generate folder and filename based on problem number"""
    clean_name = problem_name.lower().replace(" ", "_").replace("-", "_")
    
    if problem_number:
        folder = f"{problem_number:04d}_{clean_name}"
        filename = f"{problem_number:04d}_{clean_name}.{extension}"
    else:
        folder = clean_name
        filename = f"{clean_name}.{extension}"
    
    return folder, filename

def create_solution_file(code: str, language: str) -> str:
    return f"# Solution - {language.upper()}\n\n{code}\n"

def create_notes(problem: ProblemDetails, explanation: Explanation) -> str:
    difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    emoji = difficulty_emoji.get(problem.difficulty.lower(), "🟡")
    
    problem_num_str = f"{problem.problem_number}. " if problem.problem_number else ""

    notes = f"""# {problem_num_str}{problem.problem_name}

**Difficulty:** {emoji} {problem.difficulty.upper()}

**Topics/Tags:** {', '.join([f'`{tag}`' for tag in problem.tags])}

---

## 📝 Problem Statement

{problem.original_statement}

### Input
{problem.input_description}

### Output
{problem.output_description}

---


## 💡 Explanation

{explanation.explanation}

---

## 🔑 Key Insights

"""
    
    for i, insight in enumerate(explanation.key_insights, 1):
        notes += f"{i}. {insight}\n"

    notes += f"""
---

## 🎯 Hints

"""
    
    for i, hint in enumerate(explanation.hints, 1):
        notes += f"{i}. {hint}\n"

    notes += f"""
---

## 🔍 Algorithm

```
{explanation.algorithm}
```

---

## 📋 Approach

"""
    for i, step in enumerate(explanation.approach, 1):
        notes += f"{i}. {step}\n"

    notes += f"""
---

## 🚶 Step-by-Step Walkthrough

{explanation.walkthrough}

---

## 📊 Complexity Analysis

### Time Complexity
{explanation.time_complexity}

### Space Complexity
{explanation.space_complexity}

---

## ⚠️ Edge Cases

"""
    for edge_case in explanation.edge_cases:
        notes += f"- {edge_case}\n"

    notes += f"\n---\n\n## 📥 Examples\n\n"
    
    for i, example in enumerate(problem.examples, 1):
        notes += f"### Example {i}\n"
        notes += f"**Input:** `{example.input}`\n"
        notes += f"**Output:** `{example.output}`\n\n"

    notes += f"---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return notes
