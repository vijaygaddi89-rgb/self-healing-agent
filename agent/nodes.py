import os
from typing import Any
from dotenv import load_dotenv
from anthropic import Anthropic
from agent.state import AgentState, AttemptRecord
from agent.prompts import (
    CODE_GENERATION_PROMPT,
    ERROR_FIX_PROMPT,
    CODE_EXTRACTION_PROMPT,
    format_attempt_history
)

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "claude-opus-4-5")


def call_llm(prompt: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def extract_code(raw: str) -> str:
    if "```python" in raw:
        raw = raw.split("```python")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    return raw.strip()


def generate_code_node(state: AgentState) -> AgentState:
    prompt = CODE_GENERATION_PROMPT.format(task=state["task"])
    raw_response = call_llm(prompt)
    code = extract_code(raw_response)
    
    return {
        **state,
        "generated_code": code,
        "iterations": state["iterations"] + 1,
        "status": "running"
    }


def execute_code_node(state: AgentState) -> AgentState:
    import subprocess
    import tempfile
    import os

    code = state["generated_code"]

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        error = result.stderr

        if result.returncode == 0:
            return {
                **state,
                "execution_output": output,
                "error_message": None,
                "status": "success",
                "final_code": code
            }
        else:
            return {
                **state,
                "execution_output": output,
                "error_message": error,
                "status": "running"
            }
    except subprocess.TimeoutExpired:
        return {
            **state,
            "execution_output": "",
            "error_message": "Execution timed out after 30 seconds.",
            "status": "running"
        }
    finally:
        os.unlink(tmp_path)


def analyze_error_node(state: AgentState) -> AgentState:
    attempt = AttemptRecord(
        iteration=state["iterations"],
        code=state["generated_code"],
        error=state["error_message"],
        passed=False
    )

    updated_history = state["attempt_history"] + [attempt]
    formatted_history = format_attempt_history(updated_history)

    prompt = ERROR_FIX_PROMPT.format(
        task=state["task"],
        attempt_history=formatted_history,
        latest_error=state["error_message"]
    )

    raw_response = call_llm(prompt)
    fixed_code = extract_code(raw_response)

    return {
        **state,
        "generated_code": fixed_code,
        "attempt_history": updated_history,
        "iterations": state["iterations"] + 1,
        "status": "running"
    }


def should_continue(state: AgentState) -> str:
    if state["status"] == "success":
        return "done"
    if state["iterations"] >= state["max_iterations"]:
        return "failed"
    return "fix"