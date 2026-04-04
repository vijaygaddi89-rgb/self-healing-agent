import sys
import traceback

def run_code(code: str) -> dict:
    namespace = {}
    try:
        exec(compile(code, "<generated>", "exec"), namespace)
        return {"status": "success", "output": "Code executed successfully", "error": None}
    except Exception as e:
        return {"status": "error", "output": "", "error": traceback.format_exc()}

if __name__ == "__main__":
    code = sys.stdin.read()
    result = run_code(code)
    if result["status"] == "success":
        print(result["output"])
    else:
        print(result["error"], file=sys.stderr)
        sys.exit(1)