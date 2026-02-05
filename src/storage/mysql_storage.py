from typing import List, Dict, Optional, Any
from src.core.base_storage import BaseStorage

class MySqlStorage(BaseStorage):
    def __init__(self, db_url: str):
        self.db_url = db_url
        # TODO: SQLAlchemy Engine 및 Session 초기화 변수 선언

    def connect(self):
        """
        [TODO] DB 연결 세션 생성
        - sqlalchemy.create_engine()
        - sessionmaker()
        """
        print(f"[TODO] Connecting to DB: {self.db_url} (Not Implemented Yet)")
        pass

    def save(self, data: List[Any]):
        """
        [TODO] 데이터 저장
        - session.add_all() or merge()
        - commit()
        """
        print(f"[TODO] Saving {len(data)} records to DB (Not Implemented Yet)")
        pass

    def get_last_checkpoint(self) -> Optional[Dict]:
        """
        [TODO] 마지막 수집 시점 조회
        - SELECT max(date_posted) FROM bid_notices ...
        """
        return None

    def close(self):
        """
        [TODO] 연결 종료
        - session.close()
        """
        print("[TODO] Closing DB connection (Not Implemented Yet)")
        pass