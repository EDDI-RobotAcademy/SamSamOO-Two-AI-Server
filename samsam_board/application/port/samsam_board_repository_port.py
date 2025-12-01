from abc import ABC, abstractmethod
from typing import List, Optional

from samsam_board.domain.samsam_board import SamsamBoard


class SamsamBoardRepositoryPort(ABC):

    @abstractmethod
    def save(self, board: SamsamBoard) -> SamsamBoard:
        pass

    @abstractmethod
    def get_by_id(self, board_id: int) -> Optional[SamsamBoard]:
        pass

    @abstractmethod
    def list_all(self) -> List[SamsamBoard]:
        pass

    @abstractmethod
    def delete(self, board_id: int) -> None:
        pass
