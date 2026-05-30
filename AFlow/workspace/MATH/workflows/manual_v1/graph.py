import asyncio

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
        self.sc_ensemble = operator.ScEnsemble(self.llm)

    async def _generate_candidates(self, problem: str) -> list[str]:
        tasks = [
            self.custom(input=problem, instruction=instruction)
            for instruction in prompt_custom.MATH_SOLVER_INSTRUCTIONS
        ]
        responses = await asyncio.gather(*tasks)
        return [response.get("response", "") for response in responses if response.get("response")]

    async def _select_candidate(self, problem: str, candidates: list[str]) -> str:
        if not candidates:
            return ""
        if len(candidates) == 1:
            return candidates[0]
        try:
            selected = await self.sc_ensemble(solutions=candidates, problem=problem)
            return selected.get("response", candidates[0])
        except Exception:
            return candidates[0]

    async def __call__(self, problem: str):
        candidates = await self._generate_candidates(problem)
        selected = await self._select_candidate(problem, candidates)
        final_input = f"Problem:\n{problem}\n\nCandidate solution:\n{selected}"
        final = await self.custom(input=final_input, instruction=prompt_custom.FINALIZE_INSTRUCTION)
        answer = final.get("response") or selected
        return answer, self.llm.get_usage_summary()["total_cost"]
