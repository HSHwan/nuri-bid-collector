import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page, Playwright, BrowserContext

class BaseCrawler(ABC):
    """
    크롤러의 실행 흐름(Lifecycle)을 정의하는 추상 클래스
    구체적인 동작(이동, 추출)은 자식 클래스에서 구현해야 합니다.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def run(self) -> List[Any]:
        results = []
        try:
            self._setup_browser()
            self._navigate_to_target()
            
            data = self._extract_data()
            results.extend(data)
            
            self.logger.info(f"Crawling session finished. Collected {len(results)} items.")
            return results
            
        except Exception as e:
            self.logger.error(f"Critical error during crawling: {e}")
            raise e
        finally:
            self._teardown_browser()

    def _setup_browser(self):
        pw_config = self.config['system'].get('playwright', {})
        
        self._playwright = sync_playwright().start()
        
        self.browser = self._playwright.chromium.launch(
            headless=pw_config.get('headless', True)
        )
        
        self.context = self.browser.new_context(
            user_agent=pw_config.get('user_agent'),
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.context.set_default_timeout(pw_config.get('timeout', 30000))
        
        self.page = self.context.new_page()
        self.logger.info("Browser launched successfully.")

    def _teardown_browser(self):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
        self.logger.info("Browser resources released.")
    
    @abstractmethod
    def _navigate_to_target(self):
        """타겟 웹사이트 접속 및 검색 조건 설정"""
        pass

    @abstractmethod
    def _extract_data(self) -> List[Any]:
        """현재 페이지(또는 전체 페이지) 데이터 파싱 및 추출"""
        pass