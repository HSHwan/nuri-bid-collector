import re
from typing import Dict, Any, List
from src.models.bid_notice import BidNotice, BidDetail, BidAttachment

class BidFactory:
    """Raw 데이터를 도메인 모델(BidNotice)로 변환하는 팩토리"""

    @staticmethod
    def create_bid_notice(raw_data: Dict[str, Any]) -> BidNotice:
        """
        raw_data: Extractor가 추출한 딕셔너리
        """
        # 첨부파일 객체 변환 (String List -> Object List)
        attachment_names = raw_data.get('attachment_names', [])
        attachments = [BidAttachment(file_name=name) for name in attachment_names]

        # 상세 정보 생성
        detail = BidFactory._create_bid_detail(raw_data)
        
        # 날짜 포맷팅
        def fmt_date(d_str):
            if not d_str or not isinstance(d_str, str):
                return None
            temp = d_str.replace("/", "-").strip()
            temp = re.sub(r"(\d{4}-\d{2}-\d{2})(\d{2}:\d{2})", r"\1 \2", temp)
            return temp

        # 최종 객체 반환
        return BidNotice(
            notice_code="", # Crawler 레벨에서 주입됨
            degree="",      # Crawler 레벨에서 주입됨
            title=raw_data.get('title', ''),
            status=raw_data.get('status', '게시'),
            category=raw_data.get('category'),
            process_type=raw_data.get('process_type'),
            date_posted=fmt_date(raw_data.get('date_posted')),
            bid_start_dt=fmt_date(raw_data.get('bid_start_dt')),
            bid_end_dt=fmt_date(raw_data.get('bid_end_dt')),
            opening_dt=fmt_date(raw_data.get('opening_dt')),
            contract_method=raw_data.get('contract_method', ''),
            bid_method=raw_data.get('bid_method', ''),
            succ_method=raw_data.get('succ_method', ''),
            collected_at=None,
            detail_info=detail,
            attachments=attachments
        )

    @staticmethod
    def _create_bid_detail(data: Dict[str, Any]) -> BidDetail:
        briefing_text = data.get('briefing_yn_text', '')
        is_briefing = "N"
        if "예" in briefing_text or "참가" in briefing_text or "Y" in briefing_text.upper():
            is_briefing = "Y"

        return BidDetail(
            doc_number=data.get('doc_number', ''),
            manager_dept=data.get('manager_dept', ''),
            manager_name=data.get('manager_name', ''),
            construction_name=data.get('title', ''),
            client_name=data.get('client_name', ''),
            client_address=data.get('client_address', ''),
            budget_amt=BidFactory._parse_money(data.get('budget_amt')),
            base_price=BidFactory._parse_money(data.get('base_price')),
            briefing_yn=is_briefing,
            briefing_place=data.get('briefing_place', '')
        )

    @staticmethod
    def _parse_money(text: Any) -> int:
        """문자열에서 숫자만 추출하여 int로 변환"""
        if not text or not isinstance(text, str):
            return 0
        clean = re.sub(r"[^\d]", "", text)
        return int(clean) if clean else 0