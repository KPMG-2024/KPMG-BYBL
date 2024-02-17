from abc import ABC, abstractmethod

class DataCollection(ABC):
    """데이터를 수집하는 역할 하는 추상 클래스

    """
    @classmethod
    @abstractmethod
    def request(cls):
        """데이터를 외부 API에 보내는 메서드"""
        pass

    @classmethod
    @abstractmethod
    def parse(cls):
        """요청받은 데이터를 파싱하는 메서드"""
        pass
    
    @classmethod
    @abstractmethod
    def save_data(cls):
        """요청받은 데이터를 저장하는 메서드"""
        pass