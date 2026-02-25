"""
날짜 및 메타데이터 파싱 유틸리티
"""

import re
from typing import Optional, Dict
from datetime import datetime


class DateParser:
    """
    날짜, 작성자 등 메타데이터 추출 유틸리티
    """
    
    # 날짜 패턴들
    DATE_PATTERNS = [
        r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})',  # 2026-02-23 15:30
        r'(\d{4})-(\d{2})-(\d{2})',                      # 2026-02-23
        r'(\d{4})\.(\d{2})\.(\d{2})',                    # 2026.02.23
        r'(\d{4})/(\d{2})/(\d{2})',                      # 2026/02/23
        r'승인\s*(\d{4}-\d{2}-\d{2})',                   # 승인 2026-02-23
        r'입력\s*(\d{4}-\d{2}-\d{2})',                   # 입력 2026-02-23
    ]
    
    # 작성자 패턴들
    WRITER_PATTERNS = [
        r'([가-힣]{2,4})\s*기자',                        # 홍길동 기자
        r'기자\s+([가-힣]{2,4})',                        # 기자 홍길동
        r'([가-힣]{2,4})\s*특파원',                      # 홍길동 특파원
        r'([가-힣]{2,4})\s*리포터',                      # 홍길동 리포터
    ]
    
    @staticmethod
    def extract_date(text: str, format: str = 'YYYY-MM-DD') -> str:
        """
        텍스트에서 날짜 추출
        
        Args:
            text: 검색할 텍스트
            format: 반환 형식
            
        Returns:
            날짜 문자열 또는 빈 문자열
        """
        for pattern in DateParser.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                # 그룹이 여러 개면 조합
                groups = match.groups()
                if len(groups) >= 3:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                else:
                    return match.group(1)
        
        return ''
    
    @staticmethod
    def extract_writer(text: str) -> str:
        """
        텍스트에서 작성자 추출
        
        Args:
            text: 검색할 텍스트
            
        Returns:
            작성자명 또는 빈 문자열
        """
        for pattern in DateParser.WRITER_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    @staticmethod
    def extract_metadata(soup, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        선택자 기반 메타데이터 일괄 추출
        
        Args:
            soup: BeautifulSoup 객체
            selectors: {'date': 'span.date', 'writer': 'span.author'} 형식
            
        Returns:
            추출된 메타데이터 딕셔너리
        """
        metadata = {}
        
        for key, selector in selectors.items():
            elem = soup.select_one(selector)
            if elem:
                metadata[key] = elem.get_text(strip=True)
            else:
                metadata[key] = ''
        
        return metadata
    
    @staticmethod
    def normalize_date(date_str: str) -> str:
        """
        날짜 문자열을 표준 형식으로 변환
        
        Args:
            date_str: 입력 날짜 문자열
            
        Returns:
            YYYY-MM-DD 형식 또는 원본
        """
        # 이미 YYYY-MM-DD 형식이면 그대로 반환
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # 점(.) 구분자를 하이픈(-)으로 변환
        date_str = date_str.replace('.', '-')
        
        # 슬래시(/) 구분자를 하이픈(-)으로 변환
        date_str = date_str.replace('/', '-')
        
        # YYYY-MM-DD 부분만 추출
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
        if match:
            return match.group(1)
        
        return date_str
