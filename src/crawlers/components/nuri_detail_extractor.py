from typing import Dict, Any, List
from playwright.sync_api import Page

class NuriDetailExtractor:
    """HTML 페이지에서 데이터를 추출하여 딕셔너리(Raw Data)로 반환하는 클래스"""

    # 추출할 필드 정의 (Key : ([라벨 목록], 최대길이))
    # 최대길이 0은 제한 없음을 의미
    FIELD_CONFIG = {
        'doc_number': (["문서번호", "관리번호"], 50),
        'manager_dept': (["담당부서", "집행관서"], 50),
        'manager_name': (["담당자", "입력자"], 30),
        'client_address': (["납품장소", "현장위치"], 100),
        'budget_amt': (["배정예산", "사업금액"], 0),
        'base_price': (["기초금액", "예정가격"], 0),
        'briefing_yn_text': (["현장설명회대상여부", "현장설명여부", "현장설명"], 20), 
        'briefing_place': (["현장설명회장소", "현장설명장소"], 100),
        'client_name_detail': (["수요기관", "발주기관", "공고기관"], 50),
    }

    def __init__(self, logger):
        self.logger = logger

    def extract_all(self, page: Page, list_data: Dict[str, str]) -> Dict[str, Any]:
        """
        상세 페이지 정보 추출 및 목록 데이터 병합
        - list_data: 목록에서 수집한 기본 정보 (제목, 날짜, 상태, 공고번호 등)
        """
        
        # 상세 페이지 필드 추출
        detail_data = self._extract_fields(page)

        # 제목 추출
        header_title = self._extract_title(page)
        
        # 데이터 병합 (상세 페이지 데이터 + 목록 데이터)
        final_data = list_data.copy()
        final_data.update(detail_data)
        
        # 제목 보정
        if header_title:
            final_data['title'] = header_title

        # 수요기관 보정
        if not final_data.get('client_name'):
            final_data['client_name'] = final_data.get('client_name_detail') or final_data.get('manager_dept', '')

        # 첨부파일 추출
        final_data['attachment_names'] = self._extract_attachment_names(page)
        
        return final_data
    
    def _extract_fields(self, page: Page) -> Dict[str, str]:
        """설정(FIELD_CONFIG)에 따라 필드값 일괄 추출"""
        result = {}
        for key, (labels, max_len) in self.FIELD_CONFIG.items():
            result[key] = self._get_text(page, labels, max_len)
        return result

    def _extract_title(self, page: Page) -> str:
        h2 = page.locator("#mf_wfm_cntsHeader_spnHeaderTitle")
        if h2.is_visible():
            return h2.inner_text().replace("입찰공고진행상세", "").strip()
        return ""

    def _extract_attachment_names(self, page: Page) -> List[str]:
        file_names = []
        links = page.locator("//th[contains(., '첨부파일')]/following-sibling::td//a").all()
        for link in links:
            txt = link.inner_text().strip()
            if txt:
                file_names.append(txt)
        return file_names

    def _get_text(self, page: Page, labels: List[str], max_len: int = 100) -> str:
        """라벨을 기반으로 텍스트 추출"""
        for label in labels:
            loc = page.locator(f"//th[contains(., '{label}')]/following-sibling::td")
            if loc.count() > 0:
                txt = loc.first.inner_text().strip()
                # 노이즈 제거
                if "\n" in txt:
                    txt = txt.split("\n")[0].strip()
                # 길이 제한 (0이면 제한 없음)
                if max_len > 0:
                    return txt[:max_len]
                return txt
        return ""