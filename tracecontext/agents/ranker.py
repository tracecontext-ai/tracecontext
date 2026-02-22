from langchain_anthropic import ChatAnthropic
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
        self.llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)

    def rank(self, task_description: str, context_chunks: List[dict]) -> RankingResult:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a context relevance expert. Score the following context chunks based on their relevance to the provided task description."),
            ("user", "Task: {task_description}\n\nChunks:\n{chunks}")
        ])
        
        # Format chunks for the prompt
        chunks_str = "\n".join([f"- ID: {c.get('id', 'N/A')}: {c.get('content', '')}" for c in context_chunks])
        
        chain = prompt | self.llm.with_structured_output(RankingResult)
        try:
            return chain.invoke({"task_description": task_description, "chunks": chunks_str})
        except Exception as e:
            print(f"Ranker Agent Error (likely billing): {e}")
            return RankingResult(scores=[
                ContextScore(id=c.get('id', 'mock'), relevance_score=0.9, reasoning="Mock relevance due to API error")
                for c in context_chunks
            ])
