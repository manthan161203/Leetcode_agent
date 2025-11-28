import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import ProblemDetails, Explanation

# Load environment variables from .env file
load_dotenv()

# LLM SETUP (Gemini 2.5)
google_api_key = os.getenv("GOOGLE_API_KEY")

if google_api_key:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        max_tokens=4000,
        google_api_key=google_api_key
    )
else:
    llm = None


# PROMPT TEMPLATES + PARSERS
problem_parser = PydanticOutputParser(pydantic_object=ProblemDetails)

problem_prompt = PromptTemplate(
    template=(
        "You are an expert LeetCode problem analyzer.\n"
        "Extract and structure data from this problem statement:\n\n"
        "{problem_statement}\n\n"
        "IMPORTANT RULES:\n"
        "1. Extract problem_number if it exists (e.g., 1, 2, 15, 121), else set to null\n"
        "2. problem_name: Clean name only (e.g., 'Two Sum', 'Best Time to Buy and Sell Stock')\n"
        "3. difficulty: Must be one of 'Easy', 'Medium', 'Hard'\n"
        "4. tags: List of specific algorithmic tags (not generic). Examples:\n"
        "   - 'Array', 'Hash Table', 'Dynamic Programming', 'Two Pointers', 'Greedy'\n"
        "   - 'Binary Search', 'Graph', 'Tree', 'String', 'Stack', 'Queue'\n"
        "   - 'Recursion', 'Backtracking', 'Divide and Conquer', 'Trie'\n"
        "5. original_statement: Format this field with proper Markdown:\n"
        "   - Write the problem description in clear, well-structured paragraphs\n"
        "   - Use **bold** for important terms and constraints\n"
        "   - Format examples properly with headers (### Example 1, ### Example 2, etc.)\n"
        "   - Each example should have:\n"
        "     - **Input:** followed by the input value\n"
        "     - **Output:** followed by the output value\n"
        "     - **Explanation:** followed by the explanation (if provided)\n"
        "   - Format constraints section with a header (### Constraints) and bullet points\n"
        "   - Use code formatting with backticks for values (e.g., `k = 1`, `n = 111`)\n"
        "   - Ensure proper spacing and line breaks for readability\n"
        "6. input_description: What does input represent (1-2 sentences)\n"
        "7. output_description: What should be output (1-2 sentences)\n"
        "8. examples: List with 'input' and 'output' fields (simple values only, not full explanations)\n\n"
        "Format your response as JSON matching this schema:\n"
        "{format_instructions}"
    ),
    input_variables=["problem_statement"],
    partial_variables={"format_instructions": problem_parser.get_format_instructions()}
)

explanation_parser = PydanticOutputParser(pydantic_object=Explanation)

explanation_prompt = PromptTemplate(
    template=(
        "You are an expert coding educator.\n"
        "Analyze this LeetCode problem and provide detailed learning material.\n\n"
        "Problem:\n{problem_statement}\n\n"
        "Solution Code ({language}):\n{code}\n\n"
        "CRITICAL REQUIREMENTS:\n\n"
        "0. FORMATTING & TONE:\n"
        "   - Use proper Markdown formatting for all text fields\n"
        "   - Ensure the content is easy to read and understandable\n"
        "   - Use headers, lists, and bold text effectively to improve readability\n\n"
        "1. EXPLANATION (3-4 lines):\n"
        "   - Clear, concise explanation of what the solution does\n"
        "   - Explain the core insight\n"
        "   - Use **bold** for key terms and concepts\n\n"
        "2. KEY INSIGHTS (3-5 insights):\n"
        "   - Identify the core insights that make this problem solvable\n"
        "   - Focus on the 'aha!' moments or critical observations\n"
        "   - Each insight should be a complete, standalone statement\n"
        "   - Use **bold** for the main concept in each insight\n"
        "   - Examples of good insights:\n"
        "     * 'The problem can be reduced to finding **remainders modulo k**'\n"
        "     * 'Using **modular arithmetic** avoids overflow issues with large numbers'\n"
        "     * 'If k is divisible by 2 or 5, no repunit can divide it (ends in 0, 2, 4, 5, 6, 8)'\n"
        "     * 'By **Pigeonhole Principle**, we must find a cycle within k iterations'\n\n"
        "3. HINTS (5-6 hints):\n"
        "   - Each hint should highlight a key concept\n"
        "   - Use **bold** around important terms\n"
        "   - Example: 'Use a **Hash Table** to store seen elements for O(1) lookup'\n\n"
        "4. ALGORITHM:\n"
        "   - Write full pseudocode or algorithmic description\n"
        "   - Use proper indentation for nested structures\n"
        "   - Include loop structures, conditionals clearly\n"
        "   - Format like:\n"
        "     function solve(input):\n"
        "       if condition:\n"
        "         do something\n"
        "       else:\n"
        "         do other\n"
        "       for item in collection:\n"
        "         process item\n"
        "       return result\n\n"
        "5. APPROACH (step by step list):\n"
        "   - Each point is a logical step\n"
        "   - Keep points concise but complete\n"
        "   - Use **bold** for the main action in each step\n\n"
        "6. WALKTHROUGH (with visual examples):\n"
        "   - Create a highly visual, step-by-step execution trace\n"
        "   - Use **bold** for step numbers and key actions\n"
        "   - Format variable states using code blocks or tables\n"
        "   - Use ASCII art for data structures:\n"
        "     * Arrays: [1, 2, 3] with arrows → pointing to current element\n"
        "     * Pointers: Use ↑ or ^ to show positions\n"
        "     * Trees: Use simple ASCII tree structure\n"
        "     * Stacks/Queues: Show vertical or horizontal boxes\n"
        "   - Example format:\n"
        "     **Step 1:** Initialize variables\n"
        "     ```\n"
        "     array = [1, 2, 3, 4]\n"
        "             ↑\n"
        "           left\n"
        "     ```\n"
        "     **Step 2:** Process element at index 0\n"
        "     - Current value: `1`\n"
        "     - Action taken: Add to hash map\n"
        "     \n"
        "   - Use tables for tracking multiple variables:\n"
        "     | Step | Index | Value | HashMap | Result |\n"
        "     |------|-------|-------|---------|--------|\n"
        "     | 1    | 0     | 1     | {{1: 0}}  | []     |\n"
        "     \n"
        "   - Add visual separators between major steps (---)\n"
        "   - Use emojis sparingly for clarity (✓ for success, ✗ for failure)\n"
        "   - Include 'Before' and 'After' states for complex operations\n"
        "7. TIME COMPLEXITY:\n"
        "   - Give Big O notation\n"
        "   - Explain why this complexity\n"
        "   - Use **bold** for the final complexity (e.g., **O(n)**)\n"
        "8. SPACE COMPLEXITY:\n"
        "   - Give Big O notation\n"
        "   - Explain what data structures take space\n"
        "   - Use **bold** for the final complexity (e.g., **O(n)**)\n"
        "   - Example: 'O(n) - Hash table stores up to n elements'\n\n"
        "9. EDGE CASES (specific edge cases):\n"
        "   - List actual edge cases not generic ones\n"
        "   - Example instead of 'empty array': 'Array of size 1', 'All negative numbers', 'Duplicate elements'\n"
        "   - Include why each edge case is important\n\n"
        "Respond ONLY with valid JSON matching this schema:\n"
        "{format_instructions}"
    ),
    input_variables=["problem_statement", "code", "language"],
    partial_variables={"format_instructions": explanation_parser.get_format_instructions()}
)
