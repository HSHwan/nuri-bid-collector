from typing import List, Dict, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session

from src.core.base_storage import BaseStorage
from src.models.bid_notice import BidNotice
from src.storage.entities import Base, BidNoticeEntity, BidNoticeDetailEntity, BidAttachmentEntity

class MySqlStorage(BaseStorage):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """DB 연결 및 테이블 생성"""
        self.engine = create_engine(
            self.db_url,
            pool_recycle=3600,
            pool_size=10,
            echo=True
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print(f"[MySqlStorage] Connected to {self.db_url}")

    def save(self, data: List[BidNotice]):
        """
        데이터 저장 (Upsert 전략)
        Pydantic 모델 -> ORM 엔티티 변환 후 Merge
        """
        if not data:
            return

        session: Session = self.SessionLocal()
        try:
            for item in data:
                # ORM 객체 매핑
                entity = BidNoticeEntity(
                    notice_code=item.notice_code,
                    degree=item.degree,
                    title=item.title,
                    status=item.status,
                    category=item.category,
                    process_type=item.process_type,
                    date_posted=item.date_posted,
                    bid_start_dt=item.bid_start_dt,
                    bid_end_dt=item.bid_end_dt,
                    opening_dt=item.opening_dt,
                    contract_method=item.contract_method,
                    bid_method=item.bid_method,
                    succ_method=item.succ_method
                )

                # Detail 매핑 (1:1)
                if item.detail_info:
                    d = item.detail_info
                    entity.detail = BidNoticeDetailEntity(
                        notice_code=item.notice_code,
                        degree=item.degree,
                        doc_number=d.doc_number,
                        manager_dept=d.manager_dept,
                        manager_name=d.manager_name,
                        construction_name=d.construction_name,
                        completion_date=d.completion_date,
                        site_name=d.site_name,
                        client_name=d.client_name,
                        client_address=d.client_address,
                        total_area=d.total_area,
                        household_cnt=d.household_cnt,
                        budget_amt=d.budget_amt,
                        base_price=d.base_price,
                        briefing_yn=d.briefing_yn,
                        briefing_dt=d.briefing_dt,
                        briefing_place=d.briefing_place,
                    )

                # Attachments 매핑 (1:N)
                entity.attachments = [
                    BidAttachmentEntity(
                        notice_code=item.notice_code,
                        degree=item.degree,
                        file_name=f.file_name,
                        file_size=f.file_size,
                        download_url=f.download_url
                    ) for f in item.attachments
                ]

                # Upsert (Merge)
                # PK가 같으면 Update, 없으면 Insert
                session.merge(entity)
            
            session.commit()
            print(f"[MySqlStorage] Saved/Updated {len(data)} records.")

        except Exception as e:
            session.rollback()
            print(f"[Error] DB Save failed: {e}")
            raise e
        finally:
            session.close()

    def get_last_checkpoint(self) -> Optional[Dict]:
        """
        가장 최근에 수집된 공고의 날짜 조회
        """
        session: Session = self.SessionLocal()
        try:
            # 게시일자(date_posted) 기준 내림차순 1개 조회
            last_date = session.query(func.max(BidNoticeEntity.date_posted)).scalar()
            
            if last_date:
                return {'last_date': last_date}
            return None
        except Exception:
            return None
        finally:
            session.close()

    def close(self):
        if self.engine:
            self.engine.dispose()