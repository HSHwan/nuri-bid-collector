from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page, Locator
from src.models.bid_notice import BidNotice
from src.crawlers.components.nuri_detail_extractor import NuriDetailExtractor
from src.crawlers.components.bid_factory import BidFactory

class NuriParser:
    def __init__(self, logger):
        self.logger = logger
        self.extractor = NuriDetailExtractor(logger)

    def parse_list_row(self, row: Locator) -> Tuple[Dict[str, str], Locator]:
        """목록 행 파싱"""
        notice_code = ""
        title = ""
        link = None

        try:
            # 공고번호 추출
            code_col = row.locator("td[col_id='bidNtceNo']")
            if code_col.count() > 0:
                notice_code = code_col.inner_text().strip()
            else:
                # 백업: 2번째 컬럼
                notice_code = row.locator("td").nth(1).inner_text().strip()

            # 제목 및 링크 요소 추출
            title_col = row.locator("td[col_id='bidPbancNm']")
            if title_col.count() > 0:
                link = title_col.locator("a").first
                title = link.inner_text().strip()
            else:
                # 백업: 링크 태그 검색
                links = row.locator("a").all()
                for l in links:
                    txt = l.inner_text().strip()
                    if len(txt) > 5:
                        link = l
                        title = txt
                        break

        except Exception as e:
            self.logger.warning(f"List row parsing warning: {e}")

        return notice_code, title, link

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