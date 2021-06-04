from abc import ABCMeta, abstractmethod
from ..helpers import LoggerMixin
from typing import Dict, List, Union


class BaseRequest(LoggerMixin, metaclass=ABCMeta):

    @abstractmethod
    def work_on(self, number: int):
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def request_reviewers(self, reviewers: Union[List[str], None] = None, teams: Union[List[str], None] = None):
        pass

    @abstractmethod
    def list(self, **kwargs: Dict[str, str]) -> List[dict]:
        pass

    @abstractmethod
    def view(self) -> Dict[str, str]:
        pass
