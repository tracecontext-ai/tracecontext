import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ADRModel(BaseModel):
    title: str = Field(description="Title of the ADR")
    status: str = Field(description="Status of the decision")
    context: str = Field(description="Problem description and context")
    decision: str = Field(description="The chosen solution")
    consequences: str = Field(description="Pros and cons of the decision")


class ArchitectureDistiller:
    def __init__(self):
        self.llm = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")

    def distill(self, diff: str, commit_msg: str) -> ADRModel:
        if self.llm is None:
            return ADRModel(
                title=f"[DEMO] Change: {commit_msg[:60] if commit_msg else 'Unknown'}",
                status="Proposed",
                context="Set OPENAI_API_KEY to enable real AI distillation.",
                decision=commit_msg or "No commit message provided.",
                consequences="See docs for setup instructions."
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software architect. Distill the following code changes into a structured ADR in MADR format."),
            ("user", "Commit Message: {commit_msg}\n\nDiff:\n{diff}")
        ])

        chain = prompt | self.llm.with_structured_output(ADRModel)
        try:
            return chain.invoke({"commit_msg": commit_msg, "diff": diff})
        except Exception as e:
            print(f"Distiller Agent Error: {e}")
            return ADRModel(
                title=f"[DEMO] Change: {commit_msg[:60] if commit_msg else 'Unknown'}",
                status="Proposed",
                context=f"API error: {e}",
                decision=commit_msg or "No commit message provided.",
                consequences="Check OPENAI_API_KEY and billing."
            )
