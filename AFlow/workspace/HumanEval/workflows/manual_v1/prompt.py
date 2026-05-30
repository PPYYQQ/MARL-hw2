CODE_GENERATION_INSTRUCTIONS = [
    """Write a correct Python implementation for the task.
Return only Python code. Include the required entry-point function and any helper functions it needs.

Task:
""",
    """Create an alternative robust Python solution for the task.
Pay attention to edge cases, input constraints, and simple readable code. Return only Python code.

Task:
""",
]

ENSEMBLE_PROBLEM_TEMPLATE = """Choose the most correct Python solution for this HumanEval task.
Prefer code that is simple, complete, and faithful to the required entry point `{entry_point}`.

Task:
{problem}
"""
