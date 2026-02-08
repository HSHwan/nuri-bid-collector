from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BidNoticeEntity(Base):
    """[Master Table] 입찰 공고 메인"""
    __tablename__ = 'bid_notices'
    __table_args__ = {'comment': '입찰공고 마스터 정보'}

    # 복합 키
    notice_code = Column(String(50), primary_key=True)
    degree = Column(String(10), primary_key=True)

    # 기본 정보
    title = Column(String(255), nullable=False, index=True)
    status = Column(String(20))
    category = Column(String(50))
    process_type = Column(String(50))
    
    # 날짜
    date_posted = Column(String(20), index=True)
    bid_start_dt = Column(DateTime)
    bid_end_dt = Column(DateTime, index=True)
    opening_dt = Column(DateTime)
    
    # 방식
    contract_method = Column(String(50))
    bid_method = Column(String(50))
    succ_method = Column(String(50))

    # 메타 데이터
    collected_at = Column(DateTime, server_default=func.now())

    # 관계 설정 (Cascade Delete)
    detail = relationship("BidNoticeDetailEntity", back_populates="notice", uselist=False, cascade="all, delete-orphan")
    attachments = relationship("BidAttachmentEntity", back_populates="notice", cascade="all, delete-orphan")


class BidNoticeDetailEntity(Base):
    """[Detail Table] 입찰 공고 상세 (1:1)"""
    __tablename__ = 'bid_notice_details'

    notice_code = Column(String(50), primary_key=True)
    degree = Column(String(10), primary_key=True)
    
    # Composite FK
    __table_args__ = (
        ForeignKey('bid_notices.notice_code', 'bid_notices.degree'),
        {'comment': '입찰공고 상세 정보'}
    )

    # 상세 필드
    doc_number = Column(String(100))
    manager_dept = Column(String(100))
    manager_name = Column(String(50))
    
    construction_name = Column(String(255))
    completion_date = Column(String(50))
    site_name = Column(String(255))
    
    client_name = Column(String(255), index=True)
    client_address = Column(String(255))
    total_area = Column(String(50))
    household_cnt = Column(String(50))
    
    budget_amt = Column(BigInteger, default=0)
    base_price = Column(BigInteger, default=0)
    
    briefing_yn = Column(String(10))
    briefing_dt = Column(DateTime, nullable=True)
    briefing_place = Column(String(255))
    
    notice = relationship("BidNoticeEntity", back_populates="detail")


class BidAttachmentEntity(Base):
    """[File Table] 첨부파일 (1:N)"""
    __tablename__ = 'bid_attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # FK Columns
    notice_code = Column(String(50), nullable=False)
    degree = Column(String(10), nullable=False)
    
    # Composite FK
    __table_args__ = (
        ForeignKey('bid_notices.notice_code', 'bid_notices.degree'),
        {'comment': '입찰공고 첨부파일'}
    )

    file_name = Column(String(255), nullable=False)
    file_size = Column(String(50))
    download_url = Column(Text)

    notice = relationship("BidNoticeEntity", back_populates="attachments")