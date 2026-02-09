import time
from playwright.sync_api import Page
from src.core.page_context import PageContext

class NuriNavigator:
    def __init__(self, context: PageContext, logger):
        self.ctx = context
        self.logger = logger

    @property
    def page(self) -> Page:
        return self.ctx.current

    def go_to_main(self, url: str):
        self.logger.info(f"Navigating to {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        self._close_popups()

    def _close_popups(self):
        time.sleep(1.0)
        # 최대 5개의 팝업이 있다고 가정하고 순차적으로 닫기 시도
        for _ in range(5):
            close_buttons = self.page.locator(".w2window_close, .w2window_close_icon, button[title='닫기']")
            
            count = close_buttons.count()
            if count == 0:
                break # 더 이상 닫을 팝업이 없음

            self.logger.info(f"Found {count} popups. Closing them...")                
            # 보이는 닫기 버튼을 모두 클릭
            for i in range(count):
                btn = close_buttons.nth(i)
                if btn.is_visible():
                    btn.click(force=True)
                    time.sleep(0.5)

    def go_to_bid_list(self):
        """입찰공고 목록 메뉴로 이동"""
        self.logger.info("Moving to Bid Notice List...")
        try:
            # 상단 메뉴 Hover
            self.page.locator("#mf_wfm_gnb_wfm_gnbMenu_genDepth1_1_btn_menuLvl1").hover()
            time.sleep(0.5)
            # 하위 메뉴 클릭
            self.page.get_by_role("link", name="입찰공고목록").click()
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            self.logger.error(f"Menu navigation failed: {e}")
            raise e

    def set_search_conditions(self, config: dict):
        """검색 조건 설정"""
        self.logger.info("Applying search conditions...")
        self.page.get_by_role("button", name="상세조건").click()
        try:
            # 키워드
            if config.get('keyword'):
                try: self.page.get_by_label("입찰공고명").fill(config['keyword'])
                except: self.page.locator("#mf_wfm_container_tbxBidPbancNm").fill(config['keyword'])
            
            # 날짜 (1개월)
            preset = config.get('date', {}).get('preset_value', '1개월')
            try: self.page.get_by_text(preset, exact=True).click()
            except: pass

            # 드롭다운
            dropdowns = {
                "category": "공고분류",
                "progress": "진행상태",
                "notice_type": "공고구분",
                "notice_kind": "공고종류",
                "contract_method": "계약방법",
                "selection_method": "낙찰방법"
            }
            for key, label in dropdowns.items():
                val = config.get(key)
                if val and val != "전체":
                    try:
                        t = self.page.get_by_label(label).first
                        if t.is_visible(): t.select_option(label=val)
                    except Exception as e:
                        self.logger.warning(f"Failed to set dropdown {label}: {e}")
            
            # 검색 버튼 클릭
            self.page.get_by_role("button", name="검색", exact=True).click()
            self.page.wait_for_load_state("networkidle")
            time.sleep(1.0)

        except Exception as e:
            self.logger.error(f"Error setting conditions: {e}")

    def move_to_next_page(self, current_page: int) -> bool:
        """페이지네이션 처리"""
        next_page = current_page + 1
        self.logger.info(f"Attempting to move to page {next_page}...")

        try:
            # 숫자 버튼
            next_btn = self.page.locator(f".w2pageList_label:text-is('{next_page}')").first
            if next_btn.is_visible():
                next_btn.click(force=True)
                return True
            
            # 화살표 버튼
            arrow = self.page.locator("#mf_wfm_container_pagelist_next_btn")
            if arrow.is_visible():
                self.logger.info("Clicking next group arrow...")
                arrow.click(force=True)
                time.sleep(2.0)
                self.page.wait_for_load_state("networkidle")

                # 이동 확인 (현재 선택된 페이지 번호 확인)
                curr_selected = self.page.locator(".w2pageList_label_selected").first
                if curr_selected.is_visible() and curr_selected.inner_text().strip() == str(next_page):
                    return True
                
                # 버튼 다시 찾기
                next_btn_after = self.page.locator(f".w2pageList_label:text-is('{next_page}')").first
                if next_btn_after.is_visible():
                    next_btn_after.click(force=True)
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Pagination error: {e}")
            return False

    def enter_detail_page(self, link_element) -> bool:
        """상세 페이지 진입"""
        detail_header = "#mf_wfm_cntsHeader_spnHeaderTitle"

        try:
            # 클릭 전 요소 안정성 확보
            if not link_element.is_visible():
                self.logger.warning("Link element not visible.")
                return False

            self.logger.info("Clicking detail link...")
            
            # 클릭
            try: link_element.evaluate("el => el.click()")
            except: link_element.click(force=True)
            
            # 화면 전환 대기
            for _ in range(10):
                try:
                    header = self.page.locator(detail_header)
                    if header.is_visible() and "상세" in header.inner_text():
                        return True
                except: pass
                time.sleep(0.5)
            
            # 타임아웃
            self.logger.error("Timeout waiting for detail page header.")
            return False

        except Exception as e:
            self.logger.error(f"Error entering detail: {e}")
            return False

    def go_back_to_list(self):
        """목록으로 복귀"""
        grid_selector = "table[id*='grdBidPbancList_body_table']"
        
        try:
            self.logger.info("Returning to list...")
            back_btn = self.page.get_by_text("목록", exact=True)
            
            if not back_btn.is_visible():
                back_btn = self.page.locator("input[value='목록']").first

            if back_btn.is_visible():
                back_btn.click()
            
            else:
                self.logger.warning("'List' button not found. Executing Browser Back.")
                self.page.go_back()
            
            self.page.locator(grid_selector).first.wait_for(state="visible", timeout=15000)
            time.sleep(1.0)

        except Exception as e:
            self.logger.error(f"Failed to return to list: {e}")
            self.page.go_back()
            self.page.locator(grid_selector).first.wait_for(state="visible", timeout=15000)