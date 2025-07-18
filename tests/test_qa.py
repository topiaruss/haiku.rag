import pytest
from datasets import Dataset

from haiku.rag.client import HaikuRAG
from haiku.rag.qa.ollama import QuestionAnswerOllamaAgent

try:
    from haiku.rag.qa.openai import QuestionAnswerOpenAIAgent

    OPENAI_AVAILABLE = True
except ImportError:
    QuestionAnswerOpenAIAgent = None
    OPENAI_AVAILABLE = False

try:
    from haiku.rag.qa.anthropic import QuestionAnswerAnthropicAgent

    ANTHROPIC_AVAILABLE = True
except ImportError:
    QuestionAnswerAnthropicAgent = None
    ANTHROPIC_AVAILABLE = False

from .llm_judge import LLMJudge


@pytest.mark.asyncio
async def test_qa_ollama(qa_corpus: Dataset):
    """Test QA with actual question from the dataset using LLM judge."""
    client = HaikuRAG(":memory:")
    qa = QuestionAnswerOllamaAgent(client)
    llm_judge = LLMJudge()

    doc = qa_corpus[1]
    await client.create_document(
        content=doc["document_extracted"], uri=doc["document_id"]
    )

    question = doc["question"]
    expected_answer = doc["answer"]

    answer = await qa.answer(question)
    is_equivalent = await llm_judge.judge_answers(question, answer, expected_answer)

    assert is_equivalent, (
        f"Generated answer not equivalent to expected answer.\nQuestion: {question}\nGenerated: {answer}\nExpected: {expected_answer}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI not available")
async def test_qa_openai(qa_corpus: Dataset):
    """Test OpenAI QA basic functionality."""
    client = HaikuRAG(":memory:")
    qa = QuestionAnswerOpenAIAgent(client)  # type: ignore
    llm_judge = LLMJudge()

    doc = qa_corpus[1]
    await client.create_document(
        content=doc["document_extracted"], uri=doc["document_id"]
    )

    question = doc["question"]
    expected_answer = doc["answer"]

    answer = await qa.answer(question)
    is_equivalent = await llm_judge.judge_answers(question, answer, expected_answer)

    assert is_equivalent, (
        f"Generated answer not equivalent to expected answer.\nQuestion: {question}\nGenerated: {answer}\nExpected: {expected_answer}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="Anthropic not available")
async def test_qa_anthropic(qa_corpus: Dataset):
    """Test Anthropic QA basic functionality."""
    client = HaikuRAG(":memory:")
    qa = QuestionAnswerAnthropicAgent(client)  # type: ignore
    llm_judge = LLMJudge()

    doc = qa_corpus[1]
    await client.create_document(
        content=doc["document_extracted"], uri=doc["document_id"]
    )

    question = doc["question"]
    expected_answer = doc["answer"]

    answer = await qa.answer(question)
    is_equivalent = await llm_judge.judge_answers(question, answer, expected_answer)

    assert is_equivalent, (
        f"Generated answer not equivalent to expected answer.\nQuestion: {question}\nGenerated: {answer}\nExpected: {expected_answer}"
    )
