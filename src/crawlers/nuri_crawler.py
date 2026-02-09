import time
import json
import os
from typing import List, Tuple
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
        self.state_file = "crawling_state.json"

    def _navigate_to_target(self):
        """누리장터 접속 및 검색 조건 설정"""
        self.nav = NuriNavigator(self.ctx, self.logger)
        base_url = self.config['system']['crawler']['base_url']
        
        # 접속 및 초기화
        self.nav.go_to_main(base_url)
        self.nav.go_to_bid_list()
        
        # 검색 조건 적용
        self.nav.set_search_conditions(self.config.get('search', {}))
    
    def _restore_search_state(self, target_page: int):
        """직전 검색 상태를 복원"""
        self.logger.warning(f"State lost or starting. Restoring to page {target_page}...")
        
        # 목표 페이지까지 이동
        current = 1
        while current < target_page:
            if not self.nav.move_to_next_page(current):
                self.logger.error("Failed to restore page position.")
                break
            current += 1
            # 차단 방지용 미세 딜레이
            time.sleep(0.01)
        
        self.logger.info(f"Restored position to page {current}.")
        time.sleep(1.0)
    
    def _extract_data(self) -> List[BidNotice]:
        """전체 페이지 데이터 추출"""
        all_results = []
        
        # 체크포인트 로드
        start_page, start_index = self._load_checkpoint()

        # 시작 페이지가 1보다 크면 복구 실행
        if start_page > 1:
            self.logger.info(f"Checkpoint loaded. Page: {start_page}, Index: {start_index}")
            self._restore_search_state(start_page)

        current_page = start_page
        current_index_start = start_index 

        while True:
            self.logger.info(f"=== Processing Page {current_page} (Start Index: {current_index_start}) ===")
            
            # 페이지 처리
            results = self._process_page_items(current_page, current_index_start)
            all_results.extend(results)

            # 다음 페이지 이동
            if not self.nav.move_to_next_page(current_page):
                self.logger.info("End of pages.")
                break
            
            current_page += 1
            current_index_start = 0 
            
            self._save_checkpoint(current_page, 0)
            time.sleep(2.0)

        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
                self.logger.info("Crawling finished successfully. State file deleted.")
            except Exception as e:
                self.logger.warning(f"Failed to delete state file: {e}")
        
        return all_results
    
    def _process_page_items(self, expected_page: int, start_index: int) -> List[BidNotice]:
        """한 페이지의 아이템들을 처리"""
        results = []
        grid_selector = "table[id*='grdBidPbancList_body_table']"

        try:
            # 그리드 로딩
            self.page.locator(f"{grid_selector} tbody tr").first.wait_for(state="visible", timeout=15000)
            rows = self.page.locator(f"{grid_selector} tbody tr")
            count = rows.count()
            self.logger.info(f"Found {count} rows. Starting from index {start_index}.")

            for i in range(start_index, count):
                try:
                    # DOM 재조회
                    self.page.locator(f"{grid_selector} tbody tr").first.wait_for(state="visible", timeout=15000)
                    current_rows = self.page.locator(f"{grid_selector} tbody tr")
                    
                    if i >= current_rows.count():
                        break

                    row = current_rows.nth(i)
                    if not row.is_visible(): continue

                    row_data = self.parser.parse_list_row(row)
                    
                    notice_code_full = row_data['notice_code']
                    title = row_data['title']
                    link = row_data['link']
                    if not link: continue
                    
                    self.logger.info(f"Processing [{i+1}/{count}]: {title}")

                    # 상세 진입
                    if not self.nav.enter_detail_page(link):
                        continue

                    # 파싱
                    basic_data = {
                        'title': title, 
                        'notice_code_full': notice_code_full,
                        'date_posted': row_data['date_posted'],
                        'category': row_data['category'],     
                        'process_type': row_data['process_type']
                    }

                    bid = self.parser.parse_detail(self.page, basic_data)
                    if bid:
                        if "-" in notice_code_full:
                            code, degree = notice_code_full.split("-", 1)
                        else:
                            code, degree = notice_code_full, "00"
                        bid.notice_code = code
                        bid.degree = degree
                        results.append(bid)
                    
                    # 목록 복귀
                    self.nav.go_back_to_list()
                    
                    # 성공 시 다음 인덱스 저장
                    self._save_checkpoint(expected_page, i + 1)

                except Exception as e:
                    self.logger.error(f"Row error: {e}")
                    self._restore_search_state(expected_page)
                    continue

        except Exception as e:
            self.logger.error(f"Page processing error: {e}")
            return []

        return results

    def _load_checkpoint(self) -> Tuple[int, int]:
        """(페이지, 인덱스) 반환"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('page', 1), data.get('index', 0)
            except: pass
        return 1, 0

    def _save_checkpoint(self, page: int, index: int):
        """페이지와 인덱스 저장"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'page': page, 'index': index}, f)
        except: pass