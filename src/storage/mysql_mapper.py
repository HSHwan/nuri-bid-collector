from src.models.bid_notice import BidNotice, BidDetail, BidAttachment
from src.storage.entities import BidNoticeEntity, BidNoticeDetailEntity, BidAttachmentEntity

class MySqlBidMapper:
    """Pydantic DTO를 MySQL Entity로 변환하는 Mapper 클래스"""

    def to_entity(self, dto: BidNotice) -> BidNoticeEntity:
        """DTO -> Master Entity 변환"""
        entity = self._create_master_entity(dto)

        if dto.detail_info:
            entity.detail = self._create_detail_entity(
                dto.notice_code, 
                dto.degree, 
                dto.detail_info
            )

        if dto.attachments:
            entity.attachments = [
                self._create_attachment_entity(
                    dto.notice_code, 
                    dto.degree, 
                    attach
                )
                for attach in dto.attachments
            ]
            
        return entity
    
    def _create_master_entity(self, dto: BidNotice) -> BidNoticeEntity:
        """BidNotice DTO -> BidNoticeEntity (Master)"""
        return BidNoticeEntity(
            notice_code=dto.notice_code,
            degree=dto.degree,
            title=dto.title,
            status=dto.status,
            category=dto.category,
            process_type=dto.process_type,
            date_posted=dto.date_posted,
            bid_start_dt=dto.bid_start_dt,
            bid_end_dt=dto.bid_end_dt,
            opening_dt=dto.opening_dt,
            contract_method=dto.contract_method,
            bid_method=dto.bid_method,
            succ_method=dto.succ_method
        )

    def _create_detail_entity(self, code: str, degree: str, detail: BidDetail) -> BidNoticeDetailEntity:
        """Detail DTO -> Detail Entity"""
        return BidNoticeDetailEntity(
            notice_code=code,
            degree=degree,
            doc_number=detail.doc_number,
            manager_dept=detail.manager_dept,
            manager_name=detail.manager_name,
            construction_name=detail.construction_name,
            completion_date=detail.completion_date,
            site_name=detail.site_name,
            client_name=detail.client_name,
            client_address=detail.client_address,
            total_area=detail.total_area,
            household_cnt=detail.household_cnt,
            budget_amt=detail.budget_amt,
            base_price=detail.base_price,
            briefing_yn=detail.briefing_yn,
            briefing_dt=detail.briefing_dt,
            briefing_place=detail.briefing_place,
        )

    def _create_attachment_entity(self, code: str, degree: str, attach: BidAttachment) -> BidAttachmentEntity:
        """Attachment DTO -> Attachment Entity"""
        return BidAttachmentEntity(
            notice_code=code,
            degree=degree,
            file_name=attach.file_name,
            file_size=attach.file_size,
            download_url=attach.download_url
        )