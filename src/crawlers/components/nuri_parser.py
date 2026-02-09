from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page, Locator
from src.models.bid_notice import BidNotice
from src.crawlers.components.nuri_detail_extractor import NuriDetailExtractor
from src.crawlers.components.bid_factory import BidFactory

class NuriParser:
    def __init__(self, logger):
        self.logger = logger
        self.extractor = NuriDetailExtractor(logger)

    def parse_list_row(self, row: Locator) -> Dict[str, Any]:
        """목록 행 파싱"""
        data = {
            "notice_code": "",
            "title": "",
            "link": None,
            "date_posted": "",
            "category": "",
            "process_type": ""
        }
        try:
            cells = row.locator("td")
            
            # 공고번호 추출
            data["notice_code"] = cells.nth(1).inner_text().strip()
            
            # 제목 추출
            title_cell = cells.nth(2)
            data["title"] = title_cell.inner_text().strip()
            data["link"] = title_cell.locator("a").first
            
            # 공고구분, 공고분류 추출
            data["process_type"] = cells.nth(3).inner_text().strip()
            data["category"] = cells.nth(4).inner_text().strip()
            
            # 공고일자 추출
            date_posted = cells.nth(19).inner_text().strip()
            if date_posted:
                date_posted = date_posted.replace("/", "-")
            data["date_posted"] = date_posted
            
            return data

        except Exception as e:
            self.logger.error(f"Error parsing list row: {e}")
            return data

    def parse_detail(self, page: Page, list_data: Dict[str, Any]) -> Optional[BidNotice]:
        """상세 페이지 파싱"""
        try:
            # HTML에서 Raw Data 추출
            raw_data = self.extractor.extract_all(page, list_data)
            
            # 객체 생성
            bid_notice = BidFactory.create_bid_notice(raw_data)
            
            # 파싱 성공 로그
            if bid_notice:
                self.logger.info(f"Parsed Successfully: {bid_notice.title}")
            
            return bid_notice

        except Exception as e:
            self.logger.error(f"Detail parsing failed: {e}")
            return None