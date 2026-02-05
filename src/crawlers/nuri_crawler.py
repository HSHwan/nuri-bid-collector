from typing import List, Any
from core.base_crawler import BaseCrawler

class NuriCrawler(BaseCrawler):
    def _navigate_to_target(self):
        """
        [TODO] 타겟 웹사이트(누리장터) 접속 및 검색 조건 설정
        1. config/system.yaml에서 URL 로드
        2. page.goto(url)
        3. config/search.yaml의 조건(날짜, 상태 등)을 UI에 입력
        4. 검색 버튼 클릭
        """
        self.logger.info("[TODO] Navigating to Nuri Market... (Not Implemented Yet)")
        pass

    def _extract_data(self) -> List[Any]:
        """
        [TODO] 데이터 파싱 및 추출 로직
        1. 검색 결과 리스트 반복 (Pagination)
        2. 각 공고의 상세 페이지 진입 또는 리스트 데이터 추출
        3. Pydantic 모델(BidNotice)로 변환하여 리스트에 추가
        """
        self.logger.info("[TODO] Extracting data... (Not Implemented Yet)")
        return []