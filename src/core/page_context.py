from playwright.sync_api import Page

class PageContext:
    """
    페이지 공유 컨텍스트
    모든 컴포넌트가 이 객체를 통해 브라우저 페이지에 접근합니다.
    """
    def __init__(self, page: Page):
        self._page = page

    @property
    def current(self) -> Page:
        """현재 활성화된 페이지 반환"""
        return self._page