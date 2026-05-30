import workspace.MATH.workflows.manual_v1.prompt as prompt_custom
import workspace.MATH.workflows.template.operator as operator
from scripts.async_llm import create_llm_instance
from scripts.evaluator import DatasetType


class Workflow:
    def __init__(
        self,
        name: str,
        llm_config,
        dataset: DatasetType,
    ) -> None:
        self.name = name
        self.dataset = dataset
        self.llm = create_llm_instance(llm_config)
        self.custom = operator.Custom(self.llm)

    async def __call__(self, problem: str):
        initial = await self.custom(input=problem, instruction=prompt_custom.MATH_SOLVER_INSTRUCTIONS[0])
        selected = initial.get("response", "")
        final_input = f"Problem:\n{problem}\n\nCandidate solution:\n{selected}"
        final = await self.custom(input=final_input, instruction=prompt_custom.FINALIZE_INSTRUCTION)
        answer = final.get("response") or selected
        return answer, self.llm.get_usage_summary()["total_cost"]
