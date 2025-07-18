import json

from ollama import AsyncClient
from pydantic import BaseModel

from haiku.rag.config import Config


class LLMJudgeResponseSchema(BaseModel):
    equivalent: bool


class LLMJudge:
    """LLM-as-judge for evaluating answer equivalence using Ollama."""

    def __init__(self, model: str = "qwen3"):
        self.model = model
        self.client = AsyncClient(host=Config.OLLAMA_BASE_URL)

    async def judge_answers(
        self, question: str, answer: str, expected_answer: str
    ) -> bool:
        """
        Judge whether two answers are equivalent for a given question.

        Args:
            question: The original question
            answer: The generated answer to evaluate
            expected_answer: The reference/expected answer

        Returns:
            Dictionary with judgment result:
            - equivalent: bool indicating if answers are equivalent
            - explanation: str explaining the reasoning
            - score: str rating from 1-5
        """

        prompt = f"""
        You are an expert judge evaluating the equivalence of two answers to the same question.

        Question: {question}

        Generated Answer: {answer}

        Expected Answer: {expected_answer}

        Your task is to determine if these two answers are equivalent in meaning and both correctly answer the question. Consider:

        1. Do both answers provide the same answer?
        2. Do both answers directly address the question asked?
        3. Minor differences in wording or style are acceptable if the meaning of the answer is the same.
        4. If one answer is more detailed but the other is correct, they can still be considered equivalent.

        Be strict but fair in your evaluation. Focus on factual correctness and whether both answers would satisfy someone asking the question."""

        response = await self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format=LLMJudgeResponseSchema.model_json_schema(),
            think=False,
        )

        answer = response["message"]["content"].strip()
        try:
            res = json.loads(answer)
            assert "equivalent" in res, "Response must contain 'equivalent' key"
            return res["equivalent"]
        except json.JSONDecodeError:
            assert False, "Response is not valid JSON"
