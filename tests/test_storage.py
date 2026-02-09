import pytest
import os
import sys
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from src.models.bid_notice import BidNotice, BidDetail, BidAttachment
from src.storage.mysql_storage import MySqlStorage
from src.storage.entities import BidNoticeEntity

# 테스트 환경 설정
TEST_DB_URL = "mysql+pymysql://nuri_user:nuri_password@localhost:3306/nuri_db"

@pytest.fixture(scope="module")
def db_storage():
    """테스트용 DB 연결 및 스토리지 초기화"""
    storage = MySqlStorage(TEST_DB_URL)
    storage.connect()
    yield storage
    storage.close()

def test_save_full_structure(db_storage):
    """복합 구조(Master-Detail-Attach)의 공고 데이터를 저장한다."""
    # Given
    notice_code = "TEST-BID-001"
    degree = "000"
    
    bid_dto = BidNotice(
        notice_code=notice_code,
        degree=degree,
        title="[테스트] 승강기 교체 공사",
        status="게시",
        category="공사",
        process_type="일반",
        date_posted="2024-02-10",
        bid_start_dt=datetime(2024, 2, 10, 9, 0, 0),
        bid_end_dt=datetime(2024, 2, 15, 18, 0, 0),
        detail_info=BidDetail(
            client_name="아파트",
            budget_amt=100000000,
            briefing_yn="N"
        ),
        attachments=[
            BidAttachment(file_name="도면.pdf", file_size="5MB"),
            BidAttachment(file_name="시방서.hwp", file_size="10KB")
        ]
    )

    # When
    db_storage.save([bid_dto])

    # Then
    Session = sessionmaker(bind=db_storage.engine)
    session = Session()
    try:
        # Master 데이터 검증
        saved_entity = session.get(BidNoticeEntity, (notice_code, degree))
        assert saved_entity is not None, "데이터가 DB에 존재해야 한다."
        assert saved_entity.title == bid_dto.title
        
        # Detail 데이터 검증
        assert saved_entity.detail is not None, "상세 정보가 저장되어야 한다."
        assert saved_entity.detail.client_name == "아파트"
        
        # Attachment 데이터 검증
        assert len(saved_entity.attachments) == 2, "첨부파일 2개가 저장되어야 한다."
        file_names = [f.file_name for f in saved_entity.attachments]
        assert "도면.pdf" in file_names
        
        print("\n[Pass] 테스트 성공: test_save_full_structure")
        
    finally:
        session.close()

def test_upsert_logic(db_storage):
    """기존에 존재하는 공고를 다시 저장하면 내용이 업데이트되어야 한다."""
    # Given
    notice_code = "TEST-UPSERT"
    degree = "000"
    
    initial_dto = BidNotice(
        notice_code=notice_code,
        degree=degree,
        title="변경 전 제목",
        status="게시",
        date_posted="2024-02-10"
    )
    db_storage.save([initial_dto])

    # When
    updated_dto = BidNotice(
        notice_code=notice_code,
        degree=degree,
        title="변경 후 제목", # Changed
        status="마감",       # Changed
        date_posted="2024-02-10"
    )
    db_storage.save([updated_dto])

    # Then
    Session = sessionmaker(bind=db_storage.engine)
    session = Session()
    try:
        saved_entity = session.get(BidNoticeEntity, (notice_code, degree))
        
        assert saved_entity.title == "변경 후 제목", "제목이 업데이트 되어야 한다."
        assert saved_entity.status == "마감", "상태가 업데이트 되어야 한다."
        
        print("[Pass] 테스트 성공: test_upsert_logic")
        
    finally:
        session.close()