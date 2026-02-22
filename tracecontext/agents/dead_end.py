from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class DeadEndRecord(BaseModel):
    approach: str = Field(description="The approach that was attempted")
    failure_reason: str = Field(description="Why the approach was abandoned or reverted")
    alternatives: str = Field(description="What was done instead")

class DeadEndTracker:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)

    def track(self, event_sequence: str) -> DeadEndRecord:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the following developer activity. Identify if an approach was abandoned or reverted and explain why."),
            ("user", "Activity Log: {event_sequence}")
        ])
        
        chain = prompt | self.llm.with_structured_output(DeadEndRecord)
        try:
            return chain.invoke({"event_sequence": event_sequence})
        except Exception as e:
            print(f"DeadEnd Agent Error (likely billing): {e}")
            return DeadEndRecord(
                approach="[MOCK] Analyzed Approach",
                failure_reason="Mock failure reason due to API error",
                alternatives="Mock alternative approach"
            )
