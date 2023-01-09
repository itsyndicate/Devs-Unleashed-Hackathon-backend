from abc import ABC, abstractmethod


class JsonSerializable(ABC):
    @abstractmethod
    def to_json(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_json(json_data):
        raise NotImplementedError
