from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# 첨부파일
class BidAttachment(BaseModel):
    file_name: str = Field(..., description="파일명")
    file_size: Optional[str] = Field(None, description="파일크기 (예: 14.5KB)")
    download_url: Optional[str] = Field(None, description="다운로드 링크")

# 상세 정보
class BidDetail(BaseModel):
    # 문서 및 담당자
    doc_number: Optional[str] = None      # 문서번호
    manager_dept: Optional[str] = None    # 담당부서
    manager_name: Optional[str] = None    # 담당자

    # 공사/용역 개요
    construction_name: Optional[str] = None # 공사명/용역명
    completion_date: Optional[str] = None   # 준공기한
    site_name: Optional[str] = None         # 현장명

    # 발주처(단지) 정보
    client_name: Optional[str] = None       # 수요기관/단지명
    client_address: Optional[str] = None    # 단지주소
    total_area: Optional[str] = None        # 연면적
    household_cnt: Optional[str] = None     # 세대수
    
    # 금액 정보
    vat_include: Optional[str] = "N"        # 부가세포함여부
    budget_amt: Optional[int] = 0           # 배정예산
    base_price: Optional[int] = 0           # 기초금액
    
    # 투찰 제한 및 설명회
    region_limit: Optional[str] = None      # 지역제한
    license_limit: Optional[str] = None     # 업종제한
    briefing_yn: Optional[str] = "N"        # 현장설명회 여부
    briefing_dt: Optional[datetime] = None  # 현장설명회 일시
    briefing_place: Optional[str] = None    # 현장설명회 장소

# 입찰 공고
class BidNotice(BaseModel):
    # 식별자
    notice_code: str = Field(..., description="공고번호")
    degree: str = Field(..., description="차수 (예: 000)")

    # 메타 정보
    title: str = Field(..., description="공고명")
    status: str = Field(..., description="공고상태 (게시/마감)")
    category: Optional[str] = None          # 업무분류 (공사/용역)
    process_type: Optional[str] = None      # 공고처리구분 (등록/취소)
    
    # 일정 정보
    date_posted: Optional[datetime] = None  # 공고게시일시
    bid_start_dt: Optional[datetime] = None # 입찰서 접수 시작
    bid_end_dt: Optional[datetime] = None   # 입찰서 접수 마감
    opening_dt: Optional[datetime] = None   # 개찰일시
    
    # 방식 정보
    contract_method: Optional[str] = None   # 계약방법
    bid_method: Optional[str] = None        # 입찰방식
    succ_method: Optional[str] = None       # 낙찰방법

    # 포함 관계
    detail_info: Optional[BidDetail] = None 
    attachments: List[BidAttachment] = []

    @field_validator('title')
    @classmethod
    def clean_title(cls, v: str) -> str:
        return v.strip() if v else ""