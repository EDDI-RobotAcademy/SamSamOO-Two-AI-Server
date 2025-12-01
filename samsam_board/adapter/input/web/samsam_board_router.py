from typing import List

from fastapi import APIRouter, HTTPException, Cookie

from samsam_board.adapter.input.web.request.create_samsam_board_request import (
    CreateSamsamBoardRequest,
)
from samsam_board.adapter.input.web.response.samsam_board_response import (
    SamsamBoardResponse,
)
from samsam_board.application.usecase.samsam_board_usecase import (
    SamsamBoardUseCase,
)

samsam_board_router = APIRouter(tags=["board"])

usecase = SamsamBoardUseCase.getInstance()

@samsam_board_router.post("/create", response_model=SamsamBoardResponse)
def create_board(
    request: CreateSamsamBoardRequest,
    session_id: str | None = Cookie(None),
):

    writer_nickname = "samsamUser"  # default


    board = usecase.create_board(
        request.title,
        request.content,
        writer_nickname=writer_nickname,
    )

    return SamsamBoardResponse(
        id=board.id,
        title=board.title,
        content=board.content,
        writer_nickname=board.writer_nickname,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@samsam_board_router.get("/list", response_model=List[SamsamBoardResponse])
def list_boards():
    boards = usecase.list_boards()
    return [
        SamsamBoardResponse(
            id=b.id,
            title=b.title,
            content=b.content,
            writer_nickname=b.writer_nickname,
            created_at=b.created_at,
            updated_at=b.updated_at,
        )
        for b in boards
    ]


@samsam_board_router.get("/read/{board_id}", response_model=SamsamBoardResponse)
def get_board(board_id: int):
    board = usecase.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return SamsamBoardResponse(
        id=board.id,
        title=board.title,
        content=board.content,
        writer_nickname=board.writer_nickname,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@samsam_board_router.delete("/delete/{board_id}")
def delete_board(board_id: int):
    success = usecase.delete_board(board_id)
    if not success:
        raise HTTPException(status_code=404, detail="Board not found")
    return {"message": "Deleted successfully"}
