from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import Form

class Example(BaseModel):
    input: str
    output: str

class ProblemDetails(BaseModel):
    problem_number: Optional[int] = None
    problem_name: str
    difficulty: str
    tags: List[str] = Field(description="Tags like array, hash-table, dynamic-programming etc")
    original_statement: str
    input_description: str
    output_description: str
    examples: List[Example]

class Explanation(BaseModel):
    explanation: str = Field(description="Detailed explanation in 3-4 lines")
    key_insights: List[str] = Field(description="3-5 key insights about the problem and solution")
    hints: List[str] = Field(description="5-6 hints with bold key concepts")
    algorithm: str = Field(description="Full algorithm with proper formatting, indentation, pseudocode")
    approach: List[str] = Field(description="Step by step approach points")
    walkthrough: str = Field(description="Visual step-by-step walkthrough with examples")
    time_complexity: str = Field(description="Time complexity with detailed explanation")
    space_complexity: str = Field(description="Space complexity with detailed explanation")
    edge_cases: List[str] = Field(description="Important edge cases")

class GithubConfig(BaseModel):
    github_token: str
    github_username: str
    github_repo: str = "leetcode-solutions"

class LeetcodeSolution(BaseModel):
    problem_statement: str = Field(...)
    code: str = Field(...)
    language: str = Field(default="python")
    problem_name: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        problem_statement: str = Form(...),
        code: str = Form(...),
        language: str = Form("python"),
        problem_name: str = Form(None)
    ):
        return cls(
            problem_statement=problem_statement,
            code=code,
            language=language,
            problem_name=problem_name
        )
