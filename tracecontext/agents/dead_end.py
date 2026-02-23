import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class DeadEndRecord(BaseModel):
    approach: str = Field(description="The approach that was attempted")
    failure_reason: str = Field(description="Why the approach was abandoned or reverted")
    alternatives: str = Field(description="What was done instead")


class DeadEndTracker:
    def __init__(self):
        self.llm = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")

    def track(self, event_sequence: str) -> DeadEndRecord:
        if self.llm is None:
            return DeadEndRecord(
                approach="[DEMO] Analyzed Approach",
                failure_reason="Set OPENAI_API_KEY to enable real AI analysis.",
                alternatives="See docs for setup instructions."
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the following developer activity. Identify if an approach was abandoned or reverted and explain why."),
            ("user", "Activity Log: {event_sequence}")
        ])

        chain = prompt | self.llm.with_structured_output(DeadEndRecord)
        try:
            return chain.invoke({"event_sequence": event_sequence})
        except Exception as e:
            print(f"DeadEnd Agent Error: {e}")
            return DeadEndRecord(
                approach="[DEMO] Analyzed Approach",
                failure_reason=f"API error: {e}",
                alternatives="Check OPENAI_API_KEY and billing."
            )
