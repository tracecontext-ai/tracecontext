from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os

class ADRModel(BaseModel):
    title: str = Field(description="Title of the ADR")
    status: str = Field(description="Status of the decision")
    context: str = Field(description="Problem description and context")
    decision: str = Field(description="The chosen solution")
    consequences: str = Field(description="Pros and cons of the decision")

class ArchitectureDistiller:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)

    def distill(self, diff: str, commit_msg: str) -> ADRModel:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software architect. Distill the following code changes into a structured ADR in MADR format."),
            ("user", "Commit Message: {commit_msg}\n\nDiff:\n{diff}")
        ])
        
        chain = prompt | self.llm.with_structured_output(ADRModel)
        try:
            return chain.invoke({"commit_msg": commit_msg, "diff": diff})
        except Exception as e:
            print(f"Distiller Agent Error (likely billing): {e}")
            return ADRModel(
                title="[MOCK] Architecture Change Detected",
                status="Proposed",
                context="Mock context due to API error. Real agent would analyze commit: " + commit_msg,
                decision="Adopted " + (commit_msg.split(' ')[0] if commit_msg else "change"),
                consequences="Improved system architecture (Mock)"
            )
