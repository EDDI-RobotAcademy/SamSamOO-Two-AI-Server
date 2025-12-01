from pydantic import BaseModel

class CreateSamsamBoardRequest(BaseModel):
    title: str
    content: str
