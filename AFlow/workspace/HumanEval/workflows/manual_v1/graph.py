import asyncio
from pathlib import Path

import workspace.HumanEval.workflows.manual_v1.prompt as prompt_custom
import workspace.HumanEval.workflows.template.operator as operator
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
        self.code_generate = operator.CustomCodeGenerate(self.llm)
        self.sc_ensemble = operator.ScEnsemble(self.llm)
        self.test = operator.Test(self.llm)
        self.public_test_path = Path("data/datasets/humaneval_public_test.jsonl")

    async def _generate_candidates(self, problem: str, entry_point: str) -> list[str]:
        tasks = [
            self.code_generate(problem=problem, entry_point=entry_point, instruction=instruction)
            for instruction in prompt_custom.CODE_GENERATION_INSTRUCTIONS
        ]
        responses = await asyncio.gather(*tasks)
        return [response.get("response", "") for response in responses if response.get("response")]

    async def _repair_with_public_tests(self, problem: str, entry_point: str, candidates: list[str]) -> list[str]:
        if not self.public_test_path.exists():
            return candidates

        repaired_candidates: list[str] = []
        for candidate in candidates:
            try:
                test_result = await self.test(problem=problem, solution=candidate, entry_point=entry_point, test_loop=2)
            except Exception:
                repaired_candidates.append(candidate)
                continue
            solution = test_result.get("solution", candidate)
            if test_result.get("result"):
                return [solution]
            repaired_candidates.append(solution)
        return repaired_candidates or candidates

    async def _select_candidate(self, problem: str, entry_point: str, candidates: list[str]) -> str:
        if not candidates:
            return ""
        if len(candidates) == 1:
            return candidates[0]
        ensemble_problem = prompt_custom.ENSEMBLE_PROBLEM_TEMPLATE.format(problem=problem, entry_point=entry_point)
        try:
            selected = await self.sc_ensemble(solutions=candidates, problem=ensemble_problem)
            return selected.get("response", candidates[0])
        except Exception:
            return candidates[0]

    async def __call__(self, problem: str, entry_point: str):
        candidates = await self._generate_candidates(problem, entry_point)
        repaired_candidates = await self._repair_with_public_tests(problem, entry_point, candidates)
        selected = await self._select_candidate(problem, entry_point, repaired_candidates)
        return selected, self.llm.get_usage_summary()["total_cost"]
