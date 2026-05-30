import inspect
import re
from math import isclose
from typing import Any, Callable, List, Optional, Tuple

import regex
from sympy import N, simplify
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from benchmarks.benchmark import BaseBenchmark
from scripts.logs import logger


class MATHBenchmark(BaseBenchmark):
    def __init__(self, name: str, file_path: str, log_path: str):
        super().__init__(name, file_path, log_path)

    def extract_model_answer(self, text: str) -> str:
        pattern = r"\\boxed{((?:[^{}]|{[^{}]*})*)}"
        boxed_matches = re.findall(pattern, text, re.DOTALL)
        if boxed_matches:
            return boxed_matches[-1].strip()

        sentence_end_pattern = r"(?<!\d)[.!?]\s+"
        sentences = re.split(sentence_end_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences[-1] if sentences else ""

    def extract_reference_answer(self, text: str) -> str:
        pattern = r"\\boxed{((?:[^{}]|{[^{}]*})*)}"
        boxed_matches = [match.strip() for match in re.findall(pattern, text, re.DOTALL) if match.strip()]
        if len(boxed_matches) > 1:
            return ",".join(boxed_matches)
        return self.extract_model_answer(text)

    def calculate_score(self, expected_output: str, prediction: str) -> Tuple[int, str]:
        expected_answer = self.extract_reference_answer(expected_output)
        predicted_answer = self.extract_model_answer(prediction)

        if self.math_equal(predicted_answer, expected_answer):
            return 1, predicted_answer
        else:
            return 0, predicted_answer

    def math_equal(self, prediction: Any, reference: Any) -> bool:
        if str(prediction) == str(reference):
            return True

        prediction = self.normalize_answer(prediction)
        reference = self.normalize_answer(reference)
        if prediction == reference:
            return True

        prediction_parts = self.split_answer_list(prediction)
        reference_parts = self.split_answer_list(reference)
        if prediction_parts is not None or reference_parts is not None:
            prediction_parts = prediction_parts or [prediction]
            reference_parts = reference_parts or [reference]
            if len(prediction_parts) != len(reference_parts):
                return False
            unmatched_references = list(reference_parts)
            for prediction_part in prediction_parts:
                match_index = next(
                    (
                        index
                        for index, reference_part in enumerate(unmatched_references)
                        if self.scalar_math_equal(prediction_part, reference_part)
                    ),
                    None,
                )
                if match_index is None:
                    return False
                unmatched_references.pop(match_index)
            return True

        return self.scalar_math_equal(prediction, reference)

    def scalar_math_equal(self, prediction: Any, reference: Any) -> bool:
        try:
            if self.is_digit(prediction) and self.is_digit(reference):
                prediction = self.parse_digits(prediction)
                reference = self.parse_digits(reference)
                return isclose(prediction, reference, abs_tol=1e-3)
        except:
            pass

        try:
            return self.symbolic_equal(prediction, reference)
        except:
            pass

        return False

    def normalize_answer(self, answer: Any) -> str:
        answer_text = str(answer).strip().strip("$")
        wrapper_match = re.fullmatch(r"\\(?:text|mathrm)\{(.+)\}", answer_text)
        if wrapper_match:
            answer_text = wrapper_match.group(1)
        answer_text = re.sub(r"\s*,\s*", ",", answer_text)
        answer_text = re.sub(r"\s+", " ", answer_text).strip()
        if re.fullmatch(r"[A-Za-z0-9, ]+", answer_text):
            answer_text = answer_text.replace(" ", "")
        return answer_text

    def split_answer_list(self, answer: str) -> Optional[List[str]]:
        if "," not in answer or self.is_thousands_number(answer):
            return None
        parts = [part.strip() for part in answer.split(",") if part.strip()]
        return parts if len(parts) > 1 else None

    def is_thousands_number(self, answer: str) -> bool:
        return bool(re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?%?", answer))

    def is_digit(self, num):
        return self.parse_digits(num) is not None

    def parse_digits(self, num):
        num = regex.sub(",", "", str(num))
        try:
            return float(num)
        except:
            if num.endswith("%"):
                num = num[:-1]
                if num.endswith("\\"):
                    num = num[:-1]
                try:
                    return float(num) / 100
                except:
                    pass
        return None

    def symbolic_equal(self, a, b):
        def _parse(s):
            for f in [parse_latex, parse_expr]:
                try:
                    return f(s)
                except:
                    pass
            return s

        a = _parse(a)
        b = _parse(b)

        try:
            if simplify(a - b) == 0:
                return True
        except:
            pass

        try:
            if isclose(N(a), N(b), abs_tol=1e-3):
                return True
        except:
            pass
        return False

    def get_function_code(self, func):
        try:
            source_code = inspect.getsource(func)
            return source_code
        except OSError:
            return "no code"

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1), retry=retry_if_exception_type(Exception), reraise=True)
    async def _generate_output(self, graph, input_text):
        return await graph(input_text)

    async def evaluate_problem(self, problem: dict, graph: Callable) -> Tuple[str, str, str, int, float]:
        input_text = problem["problem"]
        expected_output = problem["solution"]

        try:
            output, cost = await self._generate_output(graph, input_text)
            uni_score, extracted_output = self.calculate_score(expected_output, output)

            if uni_score == 0:
                self.log_mismatch(
                    input_text,
                    expected_output,
                    output,
                    extracted_output,
                    extract_answer_code=self.get_function_code(self.extract_model_answer),
                )

            return input_text, output, expected_output, uni_score, cost

        except Exception as e:
            logger.info(f"Maximum retries reached. Skipping this sample. Error: {e}")
            return input_text, str(e), expected_output, 0.0, 0.0

    def get_result_columns(self) -> List[str]:
        return ["question", "prediction", "expected_output", "score", "cost"]
