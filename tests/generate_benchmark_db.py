import asyncio
from pathlib import Path

from datasets import Dataset, load_dataset
from llm_judge import LLMJudge
from rich.console import Console
from rich.progress import Progress

from haiku.rag.client import HaikuRAG
from haiku.rag.qa import get_qa_agent

console = Console()

db_path = Path(__file__).parent / "data" / "benchmark.sqlite"


async def populate_db():
    ds: Dataset = load_dataset("ServiceNow/repliqa")["repliqa_3"]  # type: ignore
    corpus = ds.filter(lambda doc: doc["document_topic"] == "News Stories")

    with Progress() as progress:
        task = progress.add_task("[green]Populating database...", total=len(corpus))

        async with HaikuRAG(db_path) as rag:
            for doc in corpus:
                uri = doc["document_id"]  # type: ignore
                existing_doc = await rag.get_document_by_uri(uri)
                if existing_doc is not None:
                    progress.advance(task)
                    continue

                await rag.create_document(
                    content=doc["document_extracted"],  # type: ignore
                    uri=uri,
                )
                progress.advance(task)


async def run_match_benchmark():
    ds: Dataset = load_dataset("ServiceNow/repliqa")["repliqa_3"]  # type: ignore
    corpus = ds.filter(lambda doc: doc["document_topic"] == "News Stories")

    correct_at_1 = 0
    correct_at_2 = 0
    correct_at_3 = 0
    total_queries = 0

    with Progress() as progress:
        task = progress.add_task(
            "[blue]Running retrieval benchmark...", total=len(corpus)
        )

        async with HaikuRAG(db_path) as rag:
            for doc in corpus:
                doc_id = doc["document_id"]  # type: ignore
                matches = await rag.search(
                    query=doc["question"],  # type: ignore
                    limit=3,
                )

                total_queries += 1

                # Check position of correct document in results
                for position, (chunk, _) in enumerate(matches):
                    retrieved = await rag.get_document_by_id(chunk.document_id)
                    if retrieved and retrieved.uri == doc_id:
                        if position == 0:  # First position
                            correct_at_1 += 1
                            correct_at_2 += 1
                            correct_at_3 += 1
                        elif position == 1:  # Second position
                            correct_at_2 += 1
                            correct_at_3 += 1
                        elif position == 2:  # Third position
                            correct_at_3 += 1
                        break

                progress.advance(task)

    # Calculate recall metrics
    recall_at_1 = correct_at_1 / total_queries
    recall_at_2 = correct_at_2 / total_queries
    recall_at_3 = correct_at_3 / total_queries

    console.print("\n=== Retrieval Benchmark Results ===", style="bold cyan")
    console.print(f"Total queries: {total_queries}")
    console.print(f"Recall@1: {recall_at_1:.4f}")
    console.print(f"Recall@2: {recall_at_2:.4f}")
    console.print(f"Recall@3: {recall_at_3:.4f}")

    return {"recall@1": recall_at_1, "recall@2": recall_at_2, "recall@3": recall_at_3}


async def run_qa_benchmark(k: int | None = None):
    """Run QA benchmarking on the corpus."""
    ds: Dataset = load_dataset("ServiceNow/repliqa")["repliqa_3"]  # type: ignore
    corpus = ds.filter(lambda doc: doc["document_topic"] == "News Stories")

    if k is not None:
        corpus = corpus.select(range(min(k, len(corpus))))

    judge = LLMJudge()
    correct_answers = 0
    total_questions = 0

    with Progress() as progress:
        task = progress.add_task("[yellow]Running QA benchmark...", total=len(corpus))

        async with HaikuRAG(db_path) as rag:
            qa = get_qa_agent(rag)

            for doc in corpus:
                question = doc["question"]  # type: ignore
                expected_answer = doc["answer"]  # type: ignore

                generated_answer = await qa.answer(question)
                is_equivalent = await judge.judge_answers(
                    question, generated_answer, expected_answer
                )
                console.print(f"Question: {question}")
                console.print(f"Expected: {expected_answer}")
                console.print(f"Generated: {generated_answer}")
                console.print(f"Equivalent: {is_equivalent}\n")

                if is_equivalent:
                    correct_answers += 1
                total_questions += 1
                console.print("Current score:", correct_answers, "/", total_questions)

                progress.advance(task)

    accuracy = correct_answers / total_questions if total_questions > 0 else 0

    console.print("\n=== QA Benchmark Results ===", style="bold cyan")
    console.print(f"Total questions: {total_questions}")
    console.print(f"Correct answers: {correct_answers}")
    console.print(f"QA Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")


async def main():
    await populate_db()

    console.print("Running retrieval benchmarks...", style="bold blue")
    await run_match_benchmark()

    console.print("\nRunning QA benchmarks...", style="bold yellow")
    await run_qa_benchmark()


if __name__ == "__main__":
    asyncio.run(main())
