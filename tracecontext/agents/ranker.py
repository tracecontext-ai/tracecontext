import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List


class ContextScore(BaseModel):
    id: str
    relevance_score: float = Field(description="Score between 0 and 1 indicating relevance to the task")
    reasoning: str = Field(description="Brief reason for the score")


class RankingResult(BaseModel):
    scores: List[ContextScore]


class ContextRanker:
    def __init__(self):
        self.llm = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")

    def rank(self, task_description: str, context_chunks: List[dict]) -> RankingResult:
        if self.llm is None:
            return RankingResult(scores=[
                ContextScore(id=c.get("id", "mock"), relevance_score=0.9, reasoning="Set OPENAI_API_KEY for real scoring.")
                for c in context_chunks
            ])

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a context relevance expert. Score the following context chunks based on their relevance to the provided task description."),
            ("user", "Task: {task_description}\n\nChunks:\n{chunks}")
        ])

        chunks_str = "\n".join([f"- ID: {c.get('id', 'N/A')}: {c.get('content', '')}" for c in context_chunks])

        chain = prompt | self.llm.with_structured_output(RankingResult)
        try:
            return chain.invoke({"task_description": task_description, "chunks": chunks_str})
        except Exception as e:
            print(f"Ranker Agent Error: {e}")
            return RankingResult(scores=[
                ContextScore(id=c.get("id", "mock"), relevance_score=0.9, reasoning=f"API error: {e}")
                for c in context_chunks
            ])
