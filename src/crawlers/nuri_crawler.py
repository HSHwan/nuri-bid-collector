import time
from typing import List
from src.core.base_crawler import BaseCrawler
from src.models.bid_notice import BidNotice
from src.crawlers.components.nuri_navigator import NuriNavigator
from src.crawlers.components.nuri_parser import NuriParser

class NuriCrawler(BaseCrawler):
    """누리장터(Nuri Market) 크롤러 구현체"""
    def __init__(self, config):
        super().__init__(config)
        self.nav = None
        self.parser = NuriParser(self.logger)

    def _navigate_to_target(self):
        """누리장터 접속 및 검색 조건 설정"""
        self.nav = NuriNavigator(self.ctx, self.logger)

        base_url = self.config['system']['crawler']['base_url']
        
        # 접속 및 초기화
        self.nav.go_to_main(base_url)
        self.nav.go_to_bid_list()
        
        # 검색 조건 적용
        self.nav.set_search_conditions(self.config.get('search', {}))
    
    def _extract_data(self) -> List[BidNotice]:
        """전체 페이지 데이터 추출"""
        all_results = []
        page_num = 1
        self.logger.info("Starting FULL extraction...")

        while True:
            self.logger.info(f"=== Processing Page {page_num} ===")
            
            # 현재 페이지 수집
            results = self._process_page()
            all_results.extend(results)

            if not results and page_num > 1:
                break

            # 다음 페이지 이동
            if not self.nav.move_to_next_page(page_num):
                self.logger.info("End of pages.")
                break
            
            page_num += 1
            time.sleep(2.0)
        
        return all_results
    
    def _process_page(self) -> List[BidNotice]:
        results = []
        grid_selector = "table[id*='grdBidPbancList_body_table']"

        try:
            self.page.locator(grid_selector).first.wait_for(state="visible", timeout=10000)
            rows = self.page.locator(f"{grid_selector} tbody tr")
            count = rows.count()
            self.logger.info(f"Found {count} rows.")

            for i in range(count):
                try:
                    # DOM 갱신 대응                    
                    self.page.locator(grid_selector).first.wait_for(state="visible", timeout=5000)
                    row = self.page.locator(f"{grid_selector} tbody tr").nth(i)
                    if not row.is_visible(): continue

                    # 목록 데이터 추출
                    notice_code_full, title, link = self.parser.parse_list_row(row)
                    if not link: continue
                    self.logger.info(f"Processing [{i+1}/{count}]: {title}")

                    # 상세 진입
                    if not self.nav.enter_detail_page(link):
                        self.logger.warning("Failed to enter detail. Skipping.")
                        continue

                    basic_data = {
                        'title': title,
                        'notice_code_full': notice_code_full
                    }
                    
                    # 상세 파싱 수행
                    bid = self.parser.parse_detail(self.page, basic_data)
                    
                    if bid:
                        # 공고번호/차수 분리
                        if "-" in notice_code_full:
                            code, degree = notice_code_full.split("-", 1)
                            bid.notice_code = code
                            bid.degree = degree
                        else:
                            bid.notice_code = notice_code_full
                            bid.degree = "00"
                        results.append(bid)
                    
                    # 목록 복귀
                    self.nav.go_back_to_list()

                except Exception as e:
                    self.logger.error(f"Row error: {e}")
                    self.page.go_back()
                    continue

        except Exception as e:
            self.logger.error(f"Page error: {e}")
            return []

        return results