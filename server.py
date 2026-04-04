import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.graph import agent
from agent.state import AgentState

load_dotenv()

app = FastAPI(
    title="Self-Healing Agent API",
    description="AI-powered code generation and self-healing agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class HealRequest(BaseModel):
    task: str
    max_iterations: int = 5


class HealResponse(BaseModel):
    status: str
    code: str
    iterations: int
    message: str


@app.get("/")
def root():
    return {"message": "Self-Healing Agent API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/heal", response_model=HealResponse)
def heal(request: HealRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    initial_state: AgentState = {
        "task": request.task,
        "generated_code": "",
        "execution_output": "",
        "error_message": None,
        "iterations": 0,
        "max_iterations": request.max_iterations,
        "attempt_history": [],
        "status": "running",
        "final_code": None
    }

    result = agent.invoke(initial_state)

    if result["status"] == "success":
        return HealResponse(
            status="success",
            code=result["final_code"],
            iterations=result["iterations"],
            message=f"Code generated successfully in {result['iterations']} iteration(s)"
        )
    else:
        return HealResponse(
            status="failed",
            code=result["generated_code"],
            iterations=result["iterations"],
            message=f"Agent could not solve the task in {result['iterations']} iteration(s)"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)