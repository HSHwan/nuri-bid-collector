import logging
from typing import List, Dict, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.core.base_storage import BaseStorage
from src.models.bid_notice import BidNotice
from src.storage.entities import Base, BidNoticeEntity
from src.storage.mysql_mapper import MySqlBidMapper

class MySqlStorage(BaseStorage):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mapper = MySqlBidMapper()

    def connect(self):
        """DB 연결 및 테이블 생성"""
        try:
            self.engine = create_engine(
                self.db_url,
                pool_recycle=3600,
                pool_size=10,
                echo=False
            )
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.logger.info(f"Connected to DB successfully.")
        except SQLAlchemyError as e:
            self.logger.critical(f"Failed to connect to DB: {e}")
            raise e

    def save(self, data: List[BidNotice]):
        """
        데이터 저장 (Upsert 전략)
        Pydantic 모델 -> ORM 엔티티 변환 후 Merge
        """
        if not data:
            self.logger.info("No data to save.")
            return

        session: Session = self.SessionLocal()
        try:
            for item in data:
                entity = self.mapper.to_entity(item)
                session.merge(entity)
            session.commit()
            self.logger.info(f"Successfully saved/updated {len(data)} records.")

        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"DB Transaction failed: {e}", exc_info=True)
            raise e
        finally:
            session.close()

    def get_last_checkpoint(self) -> Optional[Dict]:
        """가장 최근에 수집된 공고의 날짜 조회"""
        session: Session = self.SessionLocal()
        try:
            # 게시일자(date_posted) 기준 내림차순 1개 조회
            last_date = session.query(func.max(BidNoticeEntity.date_posted)).scalar()
            if last_date:
                return {'last_date': last_date}
            return None
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get checkpoint: {e}")
            return None
        finally:
            session.close()

    def close(self):
        if self.engine:
            self.engine.dispose()
            self.logger.info("DB connection closed.")