import time
import re
from typing import List, Optional

from src.core.base_crawler import BaseCrawler
from src.models.bid_notice import BidNotice, BidDetail, BidAttachment

class NuriCrawler(BaseCrawler):
    """누리장터(Nuri Market) 크롤러 구현체"""

    def _navigate_to_target(self):
        """타겟 웹사이트(누리장터) 접속 및 검색 조건 설정"""
        try:
            base_url = self.config['system']['crawler']['base_url']
        except KeyError:
            self.logger.warning("Base URL not found in config. Using default.")
            base_url = "https://nuri.g2b.go.kr"
        
        self.logger.info("Navigating to Nuri Market...")

        try:
            self.page.goto(base_url)
            self.page.wait_for_load_state("networkidle")

            self._close_main_popups()
            
            self.logger.info("Hovering '입찰공고' top menu...")
            self.page.locator("#mf_wfm_gnb_wfm_gnbMenu_genDepth1_1_btn_menuLvl1").hover()
            time.sleep(0.5)

            self.logger.info("Clicking '입찰공고목록' sub menu...")
            sub_menu = self.page.get_by_role("link", name="입찰공고목록")
            sub_menu.wait_for(state="visible", timeout=5000)
            sub_menu.click(force=True)
            
            self.page.wait_for_load_state("networkidle")

            time.sleep(1)
            
            self.page.get_by_role("button", name="상세조건").click()

            # 검색 조건 적용
            self._set_search_conditions()

            # 검색 버튼 클릭
            self.logger.info("Clicking Search button...")
            self.page.get_by_role("button", name="검색", exact=True).click()

            self._wait_for_loading_bar()
            time.sleep(1)

        except Exception as e:
            self.logger.error(f"Failed to navigate/search: {e}")
            raise e

    def _close_main_popups(self):
        """메인 화면의 팝업 창 닫기"""
        self.logger.info("Closing popups...")
        try:            
            # 최대 5개의 팝업이 있다고 가정하고 순차적으로 닫기 시도
            for _ in range(5):
                # 닫기 버튼 식별
                close_buttons = self.page.locator(".w2window_close, .w2window_close_icon, button[title='닫기']")
                
                count = close_buttons.count()
                if count == 0:
                    break # 더 이상 닫을 팝업이 없음

                self.logger.info(f"Found {count} popups. Closing them...")
                
                # 보이는 닫기 버튼을 모두 클릭
                for i in range(count):
                    btn = close_buttons.nth(i)
                    if btn.is_visible():
                        try:
                            btn.click(force=True)
                            time.sleep(0.5)
                        except:
                            pass
                
                time.sleep(0.5)
                
        except Exception as e:
            self.logger.warning(f"Popup closing process warning: {e}")

    def _set_search_conditions(self):
        """검색 조건 및 페이지당 조회 건수 설정"""
        self.logger.info("Applying search conditions...")
        cfg = self.config.get('search', {})

        try:
            # 텍스트 입력 (공고명, 번호)
            if cfg.get('keyword'):
                try:
                    self.page.get_by_label("입찰공고명").fill(cfg['keyword'])
                except:
                    self.page.locator("#mf_wfm_container_tbxBidPbancNm").fill(cfg['keyword'])

            if cfg.get('notice_code'):
                try:
                    self.page.get_by_label("입찰공고번호").fill(str(cfg['notice_code']))
                except:
                    self.page.locator("#mf_wfm_container_tbxBidPbancNo").fill(str(cfg['notice_code']))

            # 날짜 설정
            date_cfg = cfg.get('date', {})
            preset = date_cfg.get('preset_value', '1개월')
            try:
                self.page.get_by_text(preset, exact=True).click()
            except:
                pass

            # 드롭다운 (Select) 설정
            # 매핑: {config_key: label_name}
            dropdowns = {
                "category": "공고분류",
                "progress": "진행상태",
                "notice_type": "공고구분",
                "notice_kind": "공고종류",
                "contract_method": "계약방법",
                "selection_method": "낙찰방법"
            }

            for key, label in dropdowns.items():
                val = cfg.get(key)
                if val and val != "전체":
                    self.logger.info(f"Setting {label}: {val}")
                    try:
                        target = self.page.get_by_label(label).first
                        if target.is_visible():
                            target.select_option(label=val)
                        else:
                            self.page.locator(f"//th[contains(., '{label}')]/following-sibling::td//select").first.select_option(label=val)
                    except Exception as e:
                        self.logger.warning(f"Failed to set dropdown {label}: {e}")

        except Exception as e:
            self.logger.error(f"Error setting conditions: {e}")
    
    def _wait_for_loading_bar(self):
        """로딩 바가 사라질 때까지 대기"""
        try:
            # 일반적인 로딩 바 클래스나 ID
            loading_selector = "#___processbar2, #___processbar2_i, .w2modal"
            
            try:
                self.page.locator(loading_selector).first.wait_for(state="visible", timeout=500)
            except:
                pass

            # 로딩바가 사라질 때까지 대기
            self.page.locator(loading_selector).first.wait_for(state="hidden", timeout=10000)
            
        except Exception:
            pass

    def _extract_data(self) -> List[BidNotice]:
        """전체 페이지 데이터 추출"""
        all_results = []
        page_num = 1
        
        self.logger.info("Starting FULL data extraction...")

        while True:
            self.logger.info(f"=== Processing Page {page_num} ===")
            
            # 현재 페이지 데이터 수집
            current_page_results = self._process_current_page_rows()
            
            if current_page_results is None:
                self.logger.warning("Current page results returned None. Treating as empty list.")
                current_page_results = []

            all_results.extend(current_page_results)
            
            # 데이터가 하나도 없으면 종료 (빈 페이지)
            if not current_page_results and page_num > 1:
                self.logger.info("No data on this page. Finishing.")
                break
            
            # 다음 페이지 이동
            if not self._move_to_next_page(page_num):
                self.logger.info("Crawling finished (Last Page Reached).")
                break
            
            page_num += 1
            time.sleep(2.0)
            
        self.logger.info(f"Total collected items: {len(all_results)}")
        return all_results
    
    def _process_current_page_rows(self) -> List[BidNotice]:
        """현재 페이지의 그리드 행(Row)들을 파싱"""
        results = []
        
        # 그리드 ID (list.html 분석 결과)
        grid_selector = "table[id*='grdBidPbancList_body_table']"
        
        try:
            self.page.locator(grid_selector).first.wait_for(state="visible", timeout=10000)
        except:
            self.logger.error("List grid not found.")
            return []

        rows = self.page.locator(f"{grid_selector} tbody tr")
        count = rows.count()
        self.logger.info(f"Found {count} rows on current page.")

        if count == 0: return []

        for i in range(count):
            try:
                # [복구] 그리드 상태 재확인
                try:
                    self.page.locator(grid_selector).first.wait_for(state="visible", timeout=5000)
                except:
                    self.page.go_back()
                    self.page.locator(grid_selector).first.wait_for(state="visible", timeout=5000)

                row = self.page.locator(f"{grid_selector} tbody tr").nth(i)
                if not row.is_visible(): continue

                # --- 데이터 추출 (제목, 공고번호) ---
                notice_code_full = ""
                title_text = ""
                title_link = None

                # 공고번호
                code_col = row.locator("td[col_id='bidNtceNo']")
                if code_col.count() > 0:
                    notice_code_full = code_col.inner_text().strip()
                else:
                    cols = row.locator("td").all()
                    if len(cols) > 1: notice_code_full = cols[1].inner_text().strip()

                # 제목
                title_col = row.locator("td[col_id='bidPbancNm']")
                if title_col.count() > 0:
                    title_link = title_col.locator("a").first
                    title_text = title_link.inner_text().strip()
                else:
                    for link in row.locator("a").all():
                        txt = link.inner_text().strip()
                        if len(txt) > 5:
                            title_link = link
                            title_text = txt
                            break
                
                # 이미 수집한 데이터인지 확인 (선택 사항)
                self.logger.info(f"Processing: {title_text}")
                if not title_link: continue

                # 상세 페이지 진입
                title_link.evaluate("el => el.click()")
                
                is_entered = False
                for _ in range(5):
                    try:
                        title_el = self.page.locator("#mf_wfm_cntsHeader_spnHeaderTitle")
                        if title_el.is_visible():
                            curr_title = title_el.inner_text().strip()
                            if "상세" in curr_title or ("목록" not in curr_title and curr_title != ""):
                                is_entered = True
                                break
                        time.sleep(1)
                    except: time.sleep(1)

                if not is_entered:
                    # 클릭 재시도
                    title_link.click(force=True)
                    time.sleep(3)
                    title_el = self.page.locator("#mf_wfm_cntsHeader_spnHeaderTitle")
                    if title_el.is_visible() and "상세" in title_el.inner_text():
                        is_entered = True

                if not is_entered:
                    self.logger.warning("Failed to enter detail. Skipping.")
                    continue

                # 상세 파싱
                bid = self._parse_detail_page(self.page)
                
                if bid:
                    if "-" in notice_code_full:
                        c, d = notice_code_full.split("-", 1)
                    else:
                        c, d = notice_code_full, "00"
                    bid.notice_code = c
                    bid.degree = d
                    
                    if not bid.title or "목록" in bid.title:
                        bid.title = title_text
                    
                    results.append(bid)
                    self.logger.info(f"Parsed: {bid.title}")

                # 목록 복귀
                back_btn = self.page.locator("input[value='목록'], button:has-text('목록')").first
                if back_btn.is_visible():
                    back_btn.click(force=True)
                else:
                    self.page.go_back()
                
                self.page.locator(grid_selector).first.wait_for(state="visible", timeout=10000)
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Row processing error: {e}")
                try: self.page.go_back()
                except: pass
                continue

        return results
    
    def _move_to_next_page(self, current_page_num: int) -> bool:
        """다음 페이지로 이동 (숫자 클릭 or 화살표 클릭)"""
        next_page_num = current_page_num + 1
        self.logger.info(f"Attempting to move to page {next_page_num}...")

        try:
            # 숫자 버튼 찾기 (현재 화면에 번호가 있는지)
            # 예: 1~10 페이지인 상태에서 '2' 버튼 찾기
            next_btn = self.page.locator(f".w2pageList_label:text-is('{next_page_num}')").first
            
            if next_btn.is_visible():
                self.logger.info(f"Found page {next_page_num} button. Clicking...")
                next_btn.click(force=True)
                return True
            
            # 번호가 없으면 '다음 그룹(>)' 화살표 찾기
            next_group_arrow = self.page.locator("#mf_wfm_container_pagelist_next_btn")
            
            if next_group_arrow.is_visible():
                self.logger.info(f"Page {next_page_num} not visible. Clicking 'Next Group' arrow...")
                
                # 클릭 전 현재 페이지 번호 확인
                prev_page_el = self.page.locator(".w2pageList_label_selected")
                prev_page_text = prev_page_el.inner_text() if prev_page_el.is_visible() else str(current_page_num)

                # 화살표 클릭
                next_group_arrow.click(force=True)
                
                # 로딩 대기 (페이지 번호가 바뀔 때까지)
                time.sleep(2.0)
                self.page.wait_for_load_state("networkidle")

                # 클릭 후 상태 확인
                curr_selected_el = self.page.locator(".w2pageList_label_selected").first
                if curr_selected_el.is_visible():
                    curr_page_text = curr_selected_el.inner_text().strip()
                    self.logger.info(f"Current page after arrow click: {curr_page_text}")
                    
                    if curr_page_text == str(next_page_num):
                        self.logger.info(f"Successfully moved to page {next_page_num} via arrow.")
                        return True
                
                # 혹시 자동 이동이 안 되고 목록만 갱신된 경우를 대비해 버튼 다시 찾기
                next_btn_after = self.page.locator(f".w2pageList_label:text-is('{next_page_num}')").first
                if next_btn_after.is_visible():
                    self.logger.info(f"Arrow clicked, but need to click number {next_page_num} manually.")
                    next_btn_after.click(force=True)
                    return True

                self.logger.warning(f"Clicked arrow but could not confirm move to {next_page_num}. Current: {curr_page_text}")
                # 페이지가 안 바뀌었으면 끝으로 간주
                if prev_page_text == curr_page_text:
                    return False
            
            self.logger.info("No next page button or arrow found.")
            return False

        except Exception as e:
            self.logger.error(f"Pagination failed: {e}")
            return False

    def _parse_detail_page(self, page) -> Optional[BidNotice]:
        """상세 페이지 파싱"""
        try:
            # 제목
            title = ""
            h2 = page.locator("#mf_wfm_cntsHeader_spnHeaderTitle")
            if h2.is_visible():
                title = h2.inner_text().replace("입찰공고진행상세", "").strip()
            
            # 헬퍼 함수
            def get_val(labels: List[str], max_len=100):
                for label in labels:
                    loc = page.locator(f"//th[contains(., '{label}')]/following-sibling::td")
                    if loc.count() > 0:
                        txt = loc.first.inner_text().strip()
                        if "\n" in txt:
                            lines = [l.strip() for l in txt.split("\n") if l.strip()]
                            if len(lines) > 5: return "" 
                            return lines[0]
                        return txt[:max_len]
                return ""

            def parse_money(text):
                if not text: return 0
                clean = re.sub(r"[^\d]", "", text)
                if not clean: return 0
                return int(clean)

            # 데이터 매핑
            status = get_val(["공고상태", "진행상태"], max_len=20) or "게시"
            date_posted = get_val(["게시일시", "공고게시일자"], max_len=20)
            if date_posted: date_posted = date_posted.split(" ")[0].replace("/", "-")

            # 상세 정보 추출
            detail = BidDetail(
                doc_number=get_val(["문서번호", "관리번호"], max_len=50),
                manager_dept=get_val(["담당부서", "집행관서"], max_len=50),
                manager_name=get_val(["담당자", "입력자"], max_len=30),
                construction_name=title,
                client_name=get_val(["수요기관", "발주기관"], max_len=50),
                client_address=get_val(["납품장소", "현장위치"], max_len=100),
                budget_amt=parse_money(get_val(["배정예산", "사업금액"])),
                base_price=parse_money(get_val(["기초금액", "예정가격"])),
                briefing_yn="Y" if "참가" in get_val(["현장설명"]) else "N",
                briefing_place=get_val(["현장설명장소"], max_len=100)
            )

            # 첨부파일
            attachments = []
            links = page.locator("//th[contains(., '첨부파일')]/following-sibling::td//a").all()
            for link in links:
                fname = link.inner_text().strip()
                if fname: attachments.append(BidAttachment(file_name=fname))

            return BidNotice(
                notice_code="", degree="",
                title=title,
                status=status,
                category="공사", process_type="일반",
                date_posted=date_posted,
                detail_info=detail,
                attachments=attachments
            )

        except Exception as e:
            self.logger.error(f"Detail parsing error: {e}")
            return None