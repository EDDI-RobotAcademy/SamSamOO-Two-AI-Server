
from samsam_board.domain.samsam_board import SamsamBoard
from samsam_board.infrastructure.repository.samsam_board_repository_impl import SamsamBoardRepositoryImpl


class SamsamBoardUseCase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.repo = SamsamBoardRepositoryImpl.getInstance()
        self._initialized = True

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def create_board(
            self,
            title: str,
            content: str,
            writer_nickname: str | None = None,
    ) -> SamsamBoard:
        board = SamsamBoard(
            title=title,
            content=content,
            writer_nickname=writer_nickname,
        )
        return self.repo.save(board)
    def list_boards(self):
        return self.repo.list_all()

    def get_board(self, board_id: int):
        return self.repo.get_by_id(board_id)

    def delete_board(self, board_id: int) -> bool:
        if not self.repo.get_by_id(board_id):
            return False
        self.repo.delete(board_id)
        return True
