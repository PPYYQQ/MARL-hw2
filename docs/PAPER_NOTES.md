# Paper Notes

These notes summarize how the local reference papers informed the assignment implementation and report.

## AFlow

Source: `refpaper/2410.10762v4.pdf`

- AFlow treats agentic workflow construction as a search problem over code-represented workflows.
- A workflow is represented as LLM-invoking nodes plus edges that define execution order, dependencies, and conditional logic.
- Reusable operators such as ensemble, review, revise, test, and code generation reduce the search space and make generated workflows easier to execute.
- The optimizer uses a Monte Carlo Tree Search style loop: select candidate workflow states, expand with LLM-driven code changes, evaluate execution feedback, and backpropagate experience.
- The assignment implementation uses AFlow's workflow and operator interfaces but keeps the final workflows manual. This avoids the higher API cost of full automatic search while preserving the same engineering abstraction.

## Multi-Agent Debate

Source: `refpaper/2305.14325v1.pdf`

- Multi-agent debate improves reasoning by asking multiple model instances to produce candidate answers and then revise after seeing other agents' answers.
- The useful mechanism for this assignment is candidate diversity plus cross-checking, not necessarily long multi-round debate.
- The MATH `manual_v1` workflow borrows this idea by generating three independent solution candidates before selection.
- The HumanEval variants borrow the same diversity idea, then compare it with execution feedback from public tests.

## Implementation Implications

- The project should compare direct prompting, CoT, and multi-call workflows because the papers argue that workflow structure can change quality and cost.
- The report should state token/call costs explicitly because the papers' stronger multi-agent methods require more inference.
- Validation subsets are useful before full runs because workflow search and debate-style methods multiply API calls.
- Ablations are necessary: the assignment must separate improvements from candidate diversity, self-consistency selection, and public-test feedback.
