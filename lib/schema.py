from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field


class Quiz(BaseModel):
    questions: List[str] = Field(
        title="Questions",
        description="List of questions for the quiz",
        example=["What is the capital of France?", "What is the capital of Germany?"],
    )
    answers: List[str] = Field(
        title="Answers",
        description="List of answers for the quiz",
        example=["Paris", "Berlin"],
    )

    @property
    def as_str(self) -> str:
        return "\n\n".join([
            f"""
            **Q{i+1}**. {q}\n\n
            **A{i+1}**. {a}\n\n
            """
            for i, (q, a) in enumerate(zip(self.questions, self.answers))
        ])
        
