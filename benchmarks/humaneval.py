import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import agent
from agent.state import AgentState
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

HUMANEVAL_PROBLEMS = [
    {
        "task_id": "HE-1",
        "description": "Write a function called 'has_close_elements' that takes a list of numbers and a threshold. Return True if any two numbers in the list are closer to each other than the threshold.",
        "test_code": """
assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False
assert has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True
assert has_close_elements([1.0, 2.0, 3.0], 1.5) == True
print("HE-1 passed")
"""
    },
    {
        "task_id": "HE-2",
        "description": "Write a function called 'separate_paren_groups' that takes a string of multiple groups of nested parentheses and returns a list of strings, each containing a single group.",
        "test_code": """
assert separate_paren_groups('( ) (( )) (( )( ))') == ['()', '(())', '(()())']
assert separate_paren_groups('( ) (( ))') == ['()', '(())']
print("HE-2 passed")
"""
    },
    {
        "task_id": "HE-3",
        "description": "Write a function called 'truncate_number' that takes a positive floating point number and returns the decimal part only.",
        "test_code": """
assert truncate_number(3.5) == 0.5
assert truncate_number(1.25) == 0.25
assert truncate_number(123.456) == round(0.456, 3)
print("HE-3 passed")
"""
    },
    {
        "task_id": "HE-4",
        "description": "Write a function called 'below_zero' that takes a list of deposit and withdrawal operations on a bank account starting at zero. Return True if the balance goes below zero at any point.",
        "test_code": """
assert below_zero([1, 2, 3]) == False
assert below_zero([1, 2, -4, 5]) == True
assert below_zero([1, 2, 3, -6]) == True
print("HE-4 passed")
"""
    },
    {
        "task_id": "HE-5",
        "description": "Write a function called 'mean_absolute_deviation' that takes a list of numbers and returns the Mean Absolute Deviation around the mean of the dataset.",
        "test_code": """
assert abs(mean_absolute_deviation([1.0, 2.0, 3.0, 4.0]) - 1.0) < 0.001
assert abs(mean_absolute_deviation([1.0, 2.0, 3.0]) - round(2/3, 3)) < 0.001
print("HE-5 passed")
"""
    },
    {
        "task_id": "HE-6",
        "description": "Write a function called 'intersperse' that takes a list of numbers and a delimiter. Insert the delimiter between every two consecutive elements and return the new list.",
        "test_code": """
assert intersperse([], 4) == []
assert intersperse([1, 2, 3], 4) == [1, 4, 2, 4, 3]
assert intersperse([1, 2], 4) == [1, 4, 2]
print("HE-6 passed")
"""
    },
    {
        "task_id": "HE-7",
        "description": "Write a function called 'parse_nested_parens' that takes a string of space-separated groups of nested parentheses and returns a list of integers representing the maximum depth of nesting for each group.",
        "test_code": """
assert parse_nested_parens('(()()) ((())) () ((())()())') == [2, 3, 1, 3]
assert parse_nested_parens('() (())') == [1, 2]
print("HE-7 passed")
"""
    },
    {
        "task_id": "HE-8",
        "description": "Write a function called 'filter_by_substring' that takes a list of strings and a substring. Return only the strings that contain the given substring.",
        "test_code": """
assert filter_by_substring([], 'a') == []
assert filter_by_substring(['abc', 'bacd', 'cde', 'array'], 'a') == ['abc', 'bacd', 'array']
print("HE-8 passed")
"""
    },
    {
        "task_id": "HE-9",
        "description": "Write a function called 'sum_product' that takes a list of integers and returns a tuple of the sum and product of all the integers in the list.",
        "test_code": """
assert sum_product([]) == (0, 1)
assert sum_product([1, 2, 3, 4]) == (10, 24)
assert sum_product([1, 1, 1]) == (3, 1)
print("HE-9 passed")
"""
    },
    {
        "task_id": "HE-10",
        "description": "Write a function called 'rolling_max' that takes a list of integers and returns a list of the rolling maximum elements found until the given moment in the sequence.",
        "test_code": """
assert rolling_max([1, 2, 3, 2, 3, 4, 2]) == [1, 2, 3, 3, 3, 4, 4]
assert rolling_max([3, 2, 1]) == [3, 3, 3]
assert rolling_max([1]) == [1]
print("HE-10 passed")
"""
    }
]


def run_benchmark():
    console.print(Panel(
        "[bold blue]Self-Healing Agent — HumanEval Benchmark[/bold blue]\n"
        f"Running {len(HUMANEVAL_PROBLEMS)} problems...",
        title="Benchmark"
    ))

    results = []

    for problem in HUMANEVAL_PROBLEMS:
        console.print(f"\n[yellow]Testing {problem['task_id']}...[/yellow]")

        full_task = (
            f"{problem['description']}\n\n"
            f"After the function, include these exact tests:\n"
            f"{problem['test_code']}"
        )

        initial_state: AgentState = {
            "task": full_task,
            "generated_code": "",
            "execution_output": "",
            "error_message": None,
            "iterations": 0,
            "max_iterations": 5,
            "attempt_history": [],
            "status": "running",
            "final_code": None
        }

        try:
            result = agent.invoke(initial_state)
            passed = result["status"] == "success"
            iterations = result["iterations"]
        except Exception as e:
            passed = False
            iterations = 0
            console.print(f"[red]Exception: {e}[/red]")

        results.append({
            "task_id": problem["task_id"],
            "passed": passed,
            "iterations": iterations
        })

        status = "[green]PASS ✓[/green]" if passed else "[red]FAIL ✗[/red]"
        console.print(f"{problem['task_id']}: {status} — {iterations} iteration(s)")

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    score = (passed_count / total) * 100

    table = Table(title="Benchmark Results")
    table.add_column("Problem", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Iterations", style="yellow")

    for r in results:
        status = "PASS ✓" if r["passed"] else "FAIL ✗"
        table.add_row(r["task_id"], status, str(r["iterations"]))

    console.print(table)
    console.print(Panel(
        f"[bold green]Score: {passed_count}/{total} ({score:.1f}%)[/bold green]",
        title="Final Score"
    ))

    return score


if __name__ == "__main__":
    run_benchmark()