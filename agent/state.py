from typing import TypedDict, List, Optional
from dataclasses import dataclass, field

@dataclass
class AttemptRecord:
    iteration: int
    code: str
    error: Optional[str] = None
    passed: bool = False

class AgentState(TypedDict):
    task: str
    generated_code: str
    execution_output: str
    error_message: Optional[str]
    iterations: int
    max_iterations: int
    attempt_history: List[AttemptRecord]
    status: str
    final_code: Optional[str]