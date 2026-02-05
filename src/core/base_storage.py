from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class BaseStorage(ABC):
    """
    데이터 저장소 인터페이스
    MySQL, SQLite, CSV 등 다양한 저장 매체로 구현체를 교체할 수 있습니다.
    """
    
    @abstractmethod
    def connect(self):
        """저장소(DB) 연결 세션 생성"""
        pass

    @abstractmethod
    def save(self, data: List[Any]):
        """
        데이터 저장
        - param data: 저장할 DTO 객체 리스트 (예: List[BidNotice])
        Note: 중복 데이터 발생 시 Upsert 또는 Ignore 전략 구현 필요
        """
        pass

    @abstractmethod
    def get_last_checkpoint(self) -> Optional[Dict]:
        """
        중단점 복구를 위한 마지막 수집 상태 조회
        - return: {'last_date': '...', 'last_page': ...} 또는 None
        """
        pass
        
    @abstractmethod
    def close(self):
        """연결 종료 및 리소스 해제"""
        pass