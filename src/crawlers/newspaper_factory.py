"""
신문사 크롤러 팩토리
설정 기반으로 크롤러를 자동 생성
"""

from base_crawler import BaseCrawler
from utils import ContentParser, DateParser, TextCleaner
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class NewspaperConfig:
    """신문사 설정 클래스"""
    
    def __init__(self,
                 newspaper_name: str,
                 region: str,
                 base_url: str,
                 list_url: str,
                 article_link_selector: str,
                 content_selectors: List[str],
                 parsing_method: str = 'selector'):
        """
        Args:
            newspaper_name: 신문사명
            region: 지역명
            base_url: 메인 URL
            list_url: 기사 목록 페이지 URL
            article_link_selector: 기사 링크 선택자
            content_selectors: 본문 선택자 리스트 (우선순위대로)
            parsing_method: 파싱 방법 ('selector', 'paragraphs', 'textlines')
        """
        self.newspaper_name = newspaper_name
        self.region = region
        self.base_url = base_url
        self.list_url = list_url
        self.article_link_selector = article_link_selector
        self.content_selectors = content_selectors
        self.parsing_method = parsing_method


class GenericNewspaperCrawler(BaseCrawler):
    """
    재사용 가능한 범용 신문 크롤러
    설정만으로 새로운 신문사 추가 가능
    """
    
    def __init__(self, config: NewspaperConfig):
        """
        Args:
            config: NewspaperConfig 객체
        """
        self.news_config = config
        
        super().__init__(
            newspaper_name=config.newspaper_name,
            region=config.region,
            base_url=config.base_url,
            config={}
        )
    
    def get_article_urls(self) -> List[str]:
        """기사 URL 목록 추출"""
        soup = self.fetch_page(self.news_config.list_url)
        
        if not soup:
            return []
        
        urls = []
        articles = soup.select(self.news_config.article_link_selector)
        
        for article in articles[:50]:
            href = article.get('href')
            if href:
                full_url = href if href.startswith('http') else self.base_url + href
                if full_url not in urls:
                    urls.append(full_url)
        
        return urls
    
    def parse_article(self, url: str) -> Optional[Dict]:
        """개별 기사 파싱"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # 제목 추출
            title = self._extract_title(soup)
            
            # 본문 추출 (파싱 방법에 따라)
            content = self._extract_content(soup)
            
            # 메타데이터 추출
            page_text = soup.get_text()
            date_str = DateParser.extract_date(page_text)
            writer = DateParser.extract_writer(page_text)
            
            # 텍스트 정제
            content = TextCleaner.clean_article_text(content)
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'date': date_str,
                'writer': writer,
                'source': self.newspaper_name,
                'collected_at': self._get_timestamp()
            }
        except Exception as e:
            self.logger.error(f"파싱 실패 ({url}): {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        for selector in ['h1', 'h2.title', 'div.title h1', 'article h1']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """본문 추출 (설정된 방법 사용)"""
        method = self.news_config.parsing_method
        
        if method == 'selector':
            return ContentParser.extract_from_selector(
                soup, 
                self.news_config.content_selectors
            )
        elif method == 'paragraphs':
            return ContentParser.extract_from_paragraphs(
                soup,
                container_selector=self.news_config.content_selectors[0] if self.news_config.content_selectors else None
            )
        elif method == 'textlines':
            return ContentParser.extract_from_textlines(
                soup,
                container_selector=self.news_config.content_selectors[0]
            )
        else:
            return ContentParser.extract_from_selector(
                soup,
                self.news_config.content_selectors
            )
    
    def _get_timestamp(self) -> str:
        """현재 시간 문자열"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class NewspaperFactory:
    """
    신문사 크롤러 생성 팩토리
    """
    
    # 사전 정의된 신문사 설정
    PRESETS = {
        '서울신문': NewspaperConfig(
            newspaper_name='서울신문',
            region='서울',
            base_url='https://www.seoul.co.kr',
            list_url='https://www.seoul.co.kr/newsList/economy/',
            article_link_selector='a[href*="/news/economy/"]',
            content_selectors=['div.viewContent', 'div.viewContentWrap'],
            parsing_method='textlines'
        ),
        '경기일보': NewspaperConfig(
            newspaper_name='경기일보',
            region='경기도',
            base_url='https://www.kyeonggi.com',
            list_url='https://www.kyeonggi.com/list/25',
            article_link_selector='h3 a[href*="/article/"]',
            content_selectors=['body'],
            parsing_method='paragraphs'
        ),
        '강원도민일보': NewspaperConfig(
            newspaper_name='강원도민일보',
            region='강원도',
            base_url='https://www.kado.net',
            list_url='https://www.kado.net/news/articleList.html?sc_section_code=S1N4',
            article_link_selector='a[href*="/news/articleView"]',
            content_selectors=['article.user-snizer'],
            parsing_method='paragraphs'
        )
    }
    
    @staticmethod
    def create(newspaper_name: str) -> Optional[GenericNewspaperCrawler]:
        """
        사전 정의된 신문사 크롤러 생성
        
        Args:
            newspaper_name: 신문사명
            
        Returns:
            크롤러 객체 또는 None
        """
        config = NewspaperFactory.PRESETS.get(newspaper_name)
        
        if config:
            return GenericNewspaperCrawler(config)
        else:
            return None
    
    @staticmethod
    def create_custom(config: NewspaperConfig) -> GenericNewspaperCrawler:
        """
        커스텀 설정으로 크롤러 생성
        
        Args:
            config: NewspaperConfig 객체
            
        Returns:
            크롤러 객체
        """
        return GenericNewspaperCrawler(config)
    
    @staticmethod
    def list_available() -> List[str]:
        """사용 가능한 신문사 목록"""
        return list(NewspaperFactory.PRESETS.keys())
