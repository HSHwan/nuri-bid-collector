from typing import Dict
from crawlers.nuri_crawler import NuriCrawler
from storage.mysql_storage import MySqlStorage
from core.base_crawler import BaseCrawler
from core.base_storage import BaseStorage

class AppContainer:
    def __init__(self, config: Dict):
        self.config = config

    def create_storage(self) -> BaseStorage:
        db_url = self.config['system']['mysql']['db_url']
        return MySqlStorage(db_url)

    def create_crawler(self) -> BaseCrawler:
        return NuriCrawler(self.config)