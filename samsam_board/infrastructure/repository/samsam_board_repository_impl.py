from typing import List, Optional
from sqlalchemy.orm import Session

from samsam_board.application.port.samsam_board_repository_port import SamsamBoardRepositoryPort
from samsam_board.domain.samsam_board import SamsamBoard
from samsam_board.infrastructure.orm.samsam_board_orm import SamsamBoardORM
from config.database.session import get_db_session


class SamsamBoardRepositoryImpl(SamsamBoardRepositoryPort):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def __init__(self):
        # __init__ 은 여러 번 호출 될 수 있음
        # 해당 경우 세션이 무분별하게 여러 개 만들어지고
        # 트랜잭션을 보장할 수 없게 될 것임.
        if not hasattr(self, 'db'):
            self.db: Session = get_db_session()

    def save(self, board: SamsamBoard) -> SamsamBoard:
        orm_board = SamsamBoardORM(
            title=board.title,
            content=board.content,
            writer_nickname=board.writer_nickname,  # ✅ 추가
        )
        self.db.add(orm_board)
        self.db.commit()
        self.db.refresh(orm_board)

        board.id = orm_board.id
        board.created_at = orm_board.created_at
        board.updated_at = orm_board.updated_at
        return board

    def get_by_id(self, board_id: int) -> Optional[SamsamBoard]:
        orm_board = (
            self.db.query(SamsamBoardORM)
            .filter(SamsamBoardORM.id == board_id)
            .first()
        )
        if orm_board:
            board = SamsamBoard(
                title=orm_board.title,
                content=orm_board.content,
                writer_nickname=orm_board.writer_nickname,
            )
            board.id = orm_board.id
            board.created_at = orm_board.created_at
            board.updated_at = orm_board.updated_at
            return board
        return None

    def list_all(self) -> List[SamsamBoard]:
        orm_boards = self.db.query(SamsamBoardORM).all()
        boards: List[SamsamBoard] = []
        for orm_board in orm_boards:
            board = SamsamBoard(
                title=orm_board.title,
                content=orm_board.content,
                writer_nickname=orm_board.writer_nickname,
            )
            board.id = orm_board.id
            board.created_at = orm_board.created_at
            board.updated_at = orm_board.updated_at
            boards.append(board)
        return boards

    def delete(self, board_id: int) -> None:
        self.db.query(SamsamBoardORM).filter(SamsamBoardORM.id == board_id).delete()
        self.db.commit()
