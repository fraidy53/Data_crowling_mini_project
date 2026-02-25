"""
데이터베이스 로더
news.db에서 뉴스 데이터를 가져옵니다
"""

import sqlite3
import os
from typing import List, Dict, Optional


class NewsDBLoader:
    """뉴스 데이터베이스 로더"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 데이터베이스 경로 (기본값: ../data/news.db)
        """
        if db_path is None:
            # map 폴더 기준 상위 폴더의 data/news.db
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(os.path.dirname(current_dir), 'data', 'news.db')
        
        self.db_path = db_path
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"데이터베이스 파일을 찾을 수 없습니다: {self.db_path}")
    
    def get_all_news(self) -> List[Dict]:
        """
        모든 뉴스 가져오기
        
        Returns:
            뉴스 딕셔너리 리스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, region, sentiment_score, 
                   published_time, url, keyword, collected_at
            FROM news
            ORDER BY published_time DESC
        ''')
        
        news_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return news_list
    
    def get_news_by_region(self, region: str) -> List[Dict]:
        """
        특정 지역 뉴스 가져오기
        
        Args:
            region: 지역명 (서울, 경기도, 강원도, 충청도, 경상도, 전라도)
        
        Returns:
            뉴스 딕셔너리 리스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, region, sentiment_score, 
                   published_time, url, keyword, collected_at
            FROM news
            WHERE region = ?
            ORDER BY published_time DESC
        ''', (region,))
        
        news_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return news_list
    
    def get_region_stats(self) -> Dict[str, Dict]:
        """
        지역별 통계 가져오기
        
        Returns:
            {
                '서울': {
                    'count': 10,
                    'avg_sentiment': 0.5,
                    'positive_count': 6,
                    'negative_count': 4
                },
                ...
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                region,
                COUNT(*) as count,
                AVG(sentiment_score) as avg_sentiment,
                SUM(CASE WHEN sentiment_score > 0 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment_score < 0 THEN 1 ELSE 0 END) as negative_count
            FROM news
            GROUP BY region
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            region, count, avg_sentiment, positive, negative = row
            stats[region] = {
                'count': count,
                'avg_sentiment': avg_sentiment or 0.0,
                'positive_count': positive or 0,
                'negative_count': negative or 0
            }
        
        conn.close()
        return stats
    
    def get_latest_news_by_region(self, region: str, limit: int = 5) -> List[Dict]:
        """
        지역별 최신 뉴스 N개 가져오기
        
        Args:
            region: 지역명
            limit: 가져올 개수
        
        Returns:
            뉴스 딕셔너리 리스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, region, sentiment_score, 
                   published_time, url, keyword, collected_at
            FROM news
            WHERE region = ?
            ORDER BY published_time DESC
            LIMIT ?
        ''', (region, limit))
        
        news_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return news_list

    def get_keywords_by_regions(self, regions: List[str]) -> List[str]:
        """
        여러 지역의 키워드 목록 가져오기
        
        Args:
            regions: 지역명 리스트
        
        Returns:
            키워드 문자열 리스트
        """
        if not regions:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ",".join(["?"] * len(regions))
        query = f"""
            SELECT keyword
            FROM news
            WHERE region IN ({placeholders})
              AND keyword IS NOT NULL
              AND TRIM(keyword) != ''
        """
        cursor.execute(query, regions)

        keywords = [row[0] for row in cursor.fetchall()]
        conn.close()

        return keywords


if __name__ == '__main__':
    # 테스트
    loader = NewsDBLoader()
    
    print("=== 전체 뉴스 개수 ===")
    all_news = loader.get_all_news()
    print(f"총 {len(all_news)}개 뉴스")
    
    print("\n=== 지역별 통계 ===")
    stats = loader.get_region_stats()
    for region, stat in stats.items():
        print(f"{region}: {stat['count']}개 (평균 감성: {stat['avg_sentiment']:.2f})")
    
    print("\n=== 서울 최신 뉴스 3개 ===")
    seoul_news = loader.get_latest_news_by_region('서울', 3)
    for news in seoul_news:
        print(f"- {news['title'][:50]}... (감성: {news['sentiment_score']})")
