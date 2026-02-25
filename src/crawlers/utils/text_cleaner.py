"""
텍스트 정제 유틸리티
"""

import re
from typing import List


class TextCleaner:
    """
    텍스트 정제 및 정규화 유틸리티
    """
    
    @staticmethod
    def remove_special_chars(text: str, keep_korean: bool = True) -> str:
        """
        특수문자 제거
        
        Args:
            text: 입력 텍스트
            keep_korean: 한글 유지 여부
            
        Returns:
            정제된 텍스트
        """
        if keep_korean:
            # 한글, 영문, 숫자, 기본 문장부호만 유지
            text = re.sub(r'[^가-힣a-zA-Z0-9\s.,?!"\'\-()%]', '', text)
        else:
            # 영문, 숫자, 기본 문장부호만 유지
            text = re.sub(r'[^a-zA-Z0-9\s.,?!"\'\-()%]', '', text)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        공백 정규화
        
        Args:
            text: 입력 텍스트
            
        Returns:
            정규화된 텍스트
        """
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """
        URL 제거
        
        Args:
            text: 입력 텍스트
            
        Returns:
            URL이 제거된 텍스트
        """
        # http/https URL 제거
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # www.로 시작하는 URL 제거
        text = re.sub(r'www\.[^\s]+', '', text)
        
        return text
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """
        이메일 주소 제거
        
        Args:
            text: 입력 텍스트
            
        Returns:
            이메일이 제거된 텍스트
        """
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
        return text
    
    @staticmethod
    def clean_article_text(text: str, 
                          remove_urls: bool = True,
                          remove_emails: bool = True) -> str:
        """
        뉴스 기사 텍스트 종합 정제
        
        Args:
            text: 입력 텍스트
            remove_urls: URL 제거 여부
            remove_emails: 이메일 제거 여부
            
        Returns:
            정제된 텍스트
        """
        if remove_urls:
            text = TextCleaner.remove_urls(text)
        
        if remove_emails:
            text = TextCleaner.remove_emails(text)
        
        # 공백 정규화
        text = TextCleaner.normalize_whitespace(text)
        
        return text
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """
        텍스트 길이 제한
        
        Args:
            text: 입력 텍스트
            max_length: 최대 길이
            suffix: 잘렸을 때 붙일 접미사
            
        Returns:
            잘린 텍스트
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_sentences(text: str, max_sentences: int = None) -> List[str]:
        """
        문장 단위로 분리
        
        Args:
            text: 입력 텍스트
            max_sentences: 최대 문장 수
            
        Returns:
            문장 리스트
        """
        # 한글 문장 구분 (., !, ?)
        sentences = re.split(r'[.!?]\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if max_sentences:
            sentences = sentences[:max_sentences]
        
        return sentences
