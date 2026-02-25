"""
콘텐츠 파서 유틸리티
다양한 HTML 구조에서 본문 추출
"""

from bs4 import BeautifulSoup, Tag
from typing import List, Optional
import re


class ContentParser:
    """
    재사용 가능한 콘텐츠 파싱 클래스
    다양한 신문사의 HTML 구조에서 본문을 추출
    """
    
    # 제거할 HTML 태그
    UNWANTED_TAGS = ['script', 'style', 'iframe', 'img', 'button', 'nav', 'header', 'footer']
    
    # 제거할 클래스/ID 패턴
    UNWANTED_PATTERNS = [
        'ad', 'advertisement', 'banner', 'sidebar', 'menu',
        'related', 'recommend', 'popular', 'share', 'social'
    ]
    
    # 필터링할 키워드
    NOISE_KEYWORDS = [
        '저작권', 'Copyright', '무단', '전재', '배포금지',
        'googletag', 'display:', 'width:', 'margin:', 'padding:',
        'MobileAd', 'function()', 'cmd.push', 'gpt-ad',
        'src=', 'href=', 'class=', 'div>', '<img', '<div',
        'window.', 'document.', '.jpg', '.png', '.webp', '.gif',
        '기사를 듣', 'AI 음성', '뉴스레터', '구독', '팔로우'
    ]
    
    @staticmethod
    def extract_from_selector(soup: BeautifulSoup, 
                              selectors: List[str],
                              min_length: int = 100) -> str:
        """
        CSS 선택자로 본문 추출
        
        Args:
            soup: BeautifulSoup 객체
            selectors: 시도할 CSS 선택자 리스트
            min_length: 최소 텍스트 길이
            
        Returns:
            추출된 본문
        """
        for selector in selectors:
            content_div = soup.select_one(selector)
            if content_div:
                text = ContentParser._clean_element(content_div)
                if len(text) >= min_length:
                    return text
        
        return ''
    
    @staticmethod
    def extract_from_paragraphs(soup: BeautifulSoup,
                                 container_selector: Optional[str] = None,
                                 min_paragraph_length: int = 30) -> str:
        """
        p 태그들에서 본문 추출
        
        Args:
            soup: BeautifulSoup 객체
            container_selector: p 태그를 찾을 컨테이너 (None이면 전체)
            min_paragraph_length: 문단별 최소 길이
            
        Returns:
            추출된 본문
        """
        container = soup.select_one(container_selector) if container_selector else soup
        
        if not container:
            return ''
        
        paragraphs = container.select('p')
        content_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            
            # 길이 체크 및 노이즈 필터링
            if (len(text) >= min_paragraph_length and 
                not ContentParser._is_noise(text)):
                content_parts.append(text)
        
        return ' '.join(content_parts)
    
    @staticmethod
    def extract_from_textlines(soup: BeautifulSoup,
                               container_selector: str,
                               min_line_length: int = 20) -> str:
        """
        텍스트 라인 단위로 추출 (br 태그로 구분된 경우)
        
        Args:
            soup: BeautifulSoup 객체
            container_selector: 본문 컨테이너 선택자
            min_line_length: 라인별 최소 길이
            
        Returns:
            추출된 본문
        """
        content_div = soup.select_one(container_selector)
        
        if not content_div:
            return ''
        
        # 불필요한 요소 제거
        ContentParser._remove_unwanted_elements(content_div)
        
        # 텍스트 추출
        text = content_div.get_text(separator='\n', strip=True)
        lines = text.split('\n')
        
        # 필터링
        content_parts = []
        for line in lines:
            line = line.strip()
            if (len(line) >= min_line_length and 
                not ContentParser._is_noise(line) and
                not ContentParser._is_url_or_path(line)):
                content_parts.append(line)
        
        return ' '.join(content_parts)
    
    @staticmethod
    def _clean_element(element: Tag) -> str:
        """요소에서 깨끗한 텍스트 추출"""
        # 불필요한 요소 제거
        ContentParser._remove_unwanted_elements(element)
        
        # 텍스트 추출
        text = element.get_text(separator=' ', strip=True)
        
        # 중복 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def _remove_unwanted_elements(element: Tag) -> None:
        """불필요한 HTML 요소 제거"""
        # 태그 제거
        for tag in element.select(','.join(ContentParser.UNWANTED_TAGS)):
            tag.decompose()
        
        # 클래스/ID 패턴 제거
        for pattern in ContentParser.UNWANTED_PATTERNS:
            for elem in element.select(f'[class*="{pattern}"], [id*="{pattern}"]'):
                elem.decompose()
    
    @staticmethod
    def _is_noise(text: str) -> bool:
        """노이즈 텍스트 판별"""
        return any(keyword in text for keyword in ContentParser.NOISE_KEYWORDS)
    
    @staticmethod
    def _is_url_or_path(text: str) -> bool:
        """URL이나 경로 판별"""
        if text.startswith('/'):
            return True
        if re.match(r'^[\d\s\-:]+$', text):  # 숫자/날짜만
            return True
        return False
