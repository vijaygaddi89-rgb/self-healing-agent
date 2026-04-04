from typing import List
from agent.state import AttemptRecord


CODE_GENERATION_PROMPT = """You are an expert Python developer.

Your job is to write clean, correct Python code based on the task description below.

TASK:
{task}

REQUIREMENTS:
- Write complete, executable Python code
- Include all necessary imports
- Handle edge cases
- Do NOT include any explanation or markdown
- Return ONLY raw Python code, nothing else
"""


ERROR_FIX_PROMPT = """You are an expert Python debugger.

A previous attempt to solve this task produced errors. Your job is to analyze
the full attempt history and write a corrected version of the code.

ORIGINAL TASK:
{task}

ATTEMPT HISTORY:
{attempt_history}

LATEST ERROR:
{latest_error}

INSTRUCTIONS:
- Study every previous attempt and its error carefully
- Do NOT repeat the same approach that already failed
- Think about the root cause, not just the symptom
- Return ONLY raw corrected Python code, no explanation, no markdown
"""


CODE_EXTRACTION_PROMPT = """Extract only the raw Python code from the text below.

Remove all markdown formatting, explanations, and comments.
Return ONLY the executable Python code, nothing else.

TEXT:
{raw_text}
"""


def format_attempt_history(attempts: List[AttemptRecord]) -> str:
    if not attempts:
        return "No previous attempts."
    
    history = ""
    for attempt in attempts:
        history += f"\n--- Attempt {attempt.iteration} ---\n"
        history += f"Code written:\n{attempt.code}\n"
        if attempt.error:
            history += f"Error received:\n{attempt.error}\n"
        else:
            history += "Result: Passed\n"
    
    return history