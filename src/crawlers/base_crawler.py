"""
Base Crawler 클래스
모든 지역 신문 크롤러의 부모 클래스
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import logging
from abc import ABC, abstractmethod
import time
from typing import List, Dict, Optional
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)


class BaseCrawler(ABC):
    """
    모든 지역 신문 크롤러의 부모 클래스
    각 신문사별로 상속하여 사용

    사용 방식:
        1. newspaper_name: 신문사명
        2. region: 지역명
        3. base_url: 메인 URL
        4. config: CSS 선택자 등 설정
    """

    def __init__(self,
                 newspaper_name: str,
                 region: str,
                 base_url: str,
                 config: Dict):
        """
        Args:
            newspaper_name: 신문사명 (예: 서울신문, 경기일보)
            region: 지역명 (예: 서울, 경기도)
            base_url: 메인 URL
            config: CSS 선택자 딕셔너리
        """
        self.newspaper_name = newspaper_name
        self.region = region
        self.base_url = base_url
        self.config = config
        self.logger = logging.getLogger(newspaper_name)

        # User-Agent (봇으로 차단당하지 않도록)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        self.articles = []
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @abstractmethod
    def get_article_urls(self) -> List[str]:
        """
        신문사의 경제섹션에서 기사 URL 목록 추출
        각 신문사의 URL 구조에 맞게 구현
        """
        pass

    @abstractmethod
    def parse_article(self, url: str) -> Optional[Dict]:
        """
        개별 기사 파싱
        제목, 본문, 날짜, 출처 등 추출
        """
        pass

    def fetch_page(self, url: str, use_selenium: bool = False, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        HTML 페이지 요청 및 파싱 (재시도 로직 포함)

        Args:
            url: 요청 URL
            use_selenium: JavaScript 렌더링 필요 여부
            retries: 재시도 횟수

        Returns:
            BeautifulSoup 객체 또는 None
        """
        for attempt in range(retries):
            try:
                if use_selenium:
                    return self._fetch_with_selenium(url)
                response = self.session.get(url, timeout=15)

                # 인코딩 자동 감지 및 설정
                if response.encoding and response.encoding.lower() in ['iso-8859-1', 'windows-1252']:
                    response.encoding = 'utf-8'
                elif not response.encoding:
                    response.encoding = response.apparent_encoding or 'utf-8'

                if response.status_code == 200:
                    self.logger.debug(f"✓ 페이지 로드: {url[:60]}...")
                    return BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')

                self.logger.warning(f"✗ 상태 코드 {response.status_code}: {url}")
                return None

            except requests.Timeout:
                if attempt < retries - 1:
                    self.logger.warning(f"⏱ 타임아웃 (재시도 {attempt + 1}/{retries}): {url[:60]}...")
                    time.sleep(1)
                else:
                    self.logger.error(f"✗ 타임아웃 (최종 실패): {url}")
                    return None

            except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
                if attempt < retries - 1:
                    self.logger.warning(f"🔄 연결 오류 (재시도 {attempt + 1}/{retries}): {url[:60]}...")
                    time.sleep(2)
                else:
                    self.logger.error(f"✗ 연결 실패 (최종): {e}")
                    return None

            except Exception as e:
                if attempt < retries - 1:
                    self.logger.warning(f"⚠ 오류 (재시도 {attempt + 1}/{retries}): {e}")
                    time.sleep(1)
                else:
                    self.logger.error(f"✗ 페이지 로드 실패: {e}")
                    return None

        return None

    def _fetch_with_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Selenium을 사용한 JavaScript 렌더링 페이지 로드"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # 컨텐츠 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body'))
            )

            html = driver.page_source
            driver.quit()

            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.logger.error(f"✗ Selenium 로드 실패: {e}")
            return None

    def extract_text(self, element, selector: str, default: str = 'N/A') -> str:
        """
        CSS 선택자로 텍스트 추출 (유틸리티 함수)

        Args:
            element: BeautifulSoup 요소
            selector: CSS 선택자
            default: 찾지 못했을 때 기본값

        Returns:
            추출된 텍스트
        """
        if not element:
            return default

        try:
            elem = element.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
            return default
        except Exception:
            return default

    def crawl(self, max_articles: int = 50) -> List[Dict]:
        """
        전체 크롤링 프로세스

        Args:
            max_articles: 최대 수집할 기사 수

        Returns:
            기사 딕셔너리 리스트
        """
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"[{self.newspaper_name}({self.region})] 크롤링 시작")
        self.logger.info(f"{'=' * 60}")

        try:
            # 1단계: 기사 URL 수집
            self.logger.info("1단계: 기사 URL 수집 중...")
            article_urls = self.get_article_urls()

            if not article_urls:
                self.logger.warning("수집된 URL이 없습니다.")
                return self.articles

            article_urls = article_urls[:max_articles]
            self.logger.info(f"✓ {len(article_urls)}개 URL 수집 완료")

            # 2단계: 각 기사 파싱
            self.logger.info(f"2단계: {len(article_urls)}개 기사 파싱 중...")

            for idx, url in enumerate(article_urls, 1):
                self.logger.info(f"  [{idx}/{len(article_urls)}] 파싱...")

                article = self.parse_article(url)
                if article:
                    article['newspaper'] = self.newspaper_name
                    article['region'] = self.region
                    self.articles.append(article)

                # 서버 부하 방지 (요청 간 1초 대기)
                time.sleep(1)

            self.logger.info(f"✓ 크롤링 완료: {len(self.articles)}개 기사 수집")
            self.logger.info(f"{'=' * 60}\n")

            return self.articles

        except Exception as e:
            self.logger.error(f"✗ 크롤링 중 오류: {e}")
            return self.articles

    def to_dataframe(self) -> pd.DataFrame:
        """수집한 기사를 DataFrame으로 반환"""
        if not self.articles:
            return pd.DataFrame()
        return pd.DataFrame(self.articles)

    def save_to_csv(self, filename: str):
        """CSV 파일로 저장"""
        df = self.to_dataframe()
        if df.empty:
            self.logger.warning("저장할 데이터가 없습니다.")
            return

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        self.logger.info(f"✓ 파일 저장: {filename}")
