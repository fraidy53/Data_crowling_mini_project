"""
Folium 지도 생성기
뉴스 데이터를 인터랙티브 지도에 시각화
"""

import folium
from folium import IFrame
from typing import List, Dict
import html

from db_loader import NewsDBLoader
from region_coords import REGION_COORDS, KOREA_CENTER, DEFAULT_ZOOM
from color_mapper import (
    get_sentiment_color, 
    get_sentiment_label, 
    get_sentiment_icon,
    get_region_color_by_avg
)


class NewsMapGenerator:
    """뉴스 지도 생성기"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 데이터베이스 경로
        """
        self.loader = NewsDBLoader(db_path)
        self.map = None
    
    def create_map(self) -> folium.Map:
        """
        기본 지도 생성
        
        Returns:
            folium.Map 객체
        """
        self.map = folium.Map(
            location=KOREA_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles='OpenStreetMap'
        )
        return self.map
    
    def _create_popup_html(self, news_list: List[Dict], region: str) -> str:
        """
        팝업 HTML 생성
        
        Args:
            news_list: 뉴스 리스트
            region: 지역명
        
        Returns:
            HTML 문자열
        """
        if not news_list:
            return f"<h4>{region}</h4><p>뉴스가 없습니다.</p>"
        
        # HTML 템플릿
        html_content = f"""
        <div style="width: 400px; max-height: 500px; overflow-y: auto; font-family: Arial, sans-serif;">
            <h3 style="margin: 0 0 10px 0; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">
                📍 {region} ({len(news_list)}개 뉴스)
            </h3>
        """
        
        # 각 뉴스 항목 추가 (최대 10개)
        for i, news in enumerate(news_list[:10]):
            title = html.escape(news.get('title', '제목 없음')[:80])
            url = news.get('url', '#')
            keyword = news.get('keyword', '키워드 없음')
            sentiment = news.get('sentiment_score', 0) or 0
            sentiment_label = get_sentiment_label(sentiment)
            sentiment_color = 'blue' if sentiment > 0 else 'red' if sentiment < 0 else 'gray'
            published_time = news.get('published_time', '날짜 없음')
            
            html_content += f"""
            <div style="margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid {sentiment_color}; border-radius: 4px;">
                <div style="margin-bottom: 5px;">
                    <strong style="color: #333; font-size: 14px;">{i+1}. {title}</strong>
                </div>
                <div style="font-size: 11px; color: #666; margin: 5px 0;">
                    <span style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px; margin-right: 5px;">
                        🏷️ {keyword}
                    </span>
                    <span style="background: #{'e8f5e9' if sentiment > 0 else 'ffebee' if sentiment < 0 else 'f5f5f5'}; padding: 2px 6px; border-radius: 3px;">
                        {sentiment_label} ({sentiment:.2f})
                    </span>
                </div>
                <div style="font-size: 11px; color: #999; margin: 5px 0;">
                    📅 {published_time}
                </div>
                <div style="margin-top: 5px;">
                    <a href="{url}" target="_blank" style="color: #1976d2; text-decoration: none; font-size: 11px;">
                        🔗 기사 보기
                    </a>
                </div>
            </div>
            """
        
        if len(news_list) > 10:
            html_content += f"""
            <div style="margin: 10px 0; padding: 10px; background: #fff3e0; border-radius: 4px; text-align: center; font-size: 12px; color: #666;">
                + {len(news_list) - 10}개 더 있음
            </div>
            """
        
        html_content += "</div>"
        return html_content
    
    def add_region_markers(self, max_news_per_region: int = 10):
        """
        지역별 마커 추가
        
        Args:
            max_news_per_region: 지역당 표시할 최대 뉴스 개수
        """
        if self.map is None:
            self.create_map()
        
        # 지역별 통계 가져오기
        stats = self.loader.get_region_stats()
        
        # 각 지역에 마커 추가
        for region, coord in REGION_COORDS.items():
            news_list = self.loader.get_latest_news_by_region(region, max_news_per_region)
            
            if not news_list:
                continue
            
            # 지역 평균 감성 점수
            stat = stats.get(region, {})
            avg_sentiment = stat.get('avg_sentiment', 0)
            total_count = stat.get('count', 0)
            
            # 마커 색상 결정
            marker_color = 'blue' if avg_sentiment > 0 else 'red' if avg_sentiment < 0 else 'gray'
            
            # 팝업 HTML 생성
            popup_html = self._create_popup_html(news_list, region)
            
            # IFrame으로 팝업 생성 (크기 조정 가능)
            iframe = IFrame(popup_html, width=450, height=400)
            popup = folium.Popup(iframe, max_width=450)
            
            # 마커 추가
            folium.Marker(
                location=coord,
                popup=popup,
                tooltip=f"{region} (뉴스 {total_count}개, 평균 감성: {avg_sentiment:.2f})",
                icon=folium.Icon(
                    color=marker_color,
                    icon=get_sentiment_icon(avg_sentiment),
                    prefix='glyphicon'
                )
            ).add_to(self.map)
            
            # 원형 마커도 추가 (시각적 효과)
            folium.CircleMarker(
                location=coord,
                radius=10 + (total_count / 2),  # 뉴스 개수에 비례
                color=get_region_color_by_avg(avg_sentiment),
                fill=True,
                fill_color=get_region_color_by_avg(avg_sentiment),
                fill_opacity=0.3,
                weight=2
            ).add_to(self.map)
    
    def add_legend(self):
        """범례 추가"""
        if self.map is None:
            return
        
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h4 style="margin: 0 0 10px 0; text-align: center; color: #333;">감성 분석 범례</h4>
            <p style="margin: 5px 0;"><span style="color: blue;">●</span> 긍정적 (> 0)</p>
            <p style="margin: 5px 0;"><span style="color: gray;">●</span> 중립 (= 0)</p>
            <p style="margin: 5px 0;"><span style="color: red;">●</span> 부정적 (< 0)</p>
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0; font-size: 10px; color: #666;">
                원 크기 = 뉴스 개수<br>
                마커 클릭 = 상세 정보
            </p>
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def generate(self, output_file: str = 'news_map.html', max_news: int = 10):
        """
        지도 생성 및 저장
        
        Args:
            output_file: 출력 HTML 파일명
            max_news: 지역당 최대 뉴스 개수
        
        Returns:
            folium.Map 객체
        """
        print(f"📊 뉴스 지도 생성 중...")
        
        # 지도 생성
        self.create_map()
        
        # 마커 추가
        print(f"📍 지역 마커 추가 중...")
        self.add_region_markers(max_news)
        
        # 범례 추가
        self.add_legend()
        
        # HTML 파일로 저장
        self.map.save(output_file)
        print(f"✅ 지도 저장 완료: {output_file}")
        
        return self.map


if __name__ == '__main__':
    # 지도 생성 테스트
    import os
    
    # 현재 폴더에 저장
    output_path = os.path.join(os.path.dirname(__file__), 'news_map.html')
    
    generator = NewsMapGenerator()
    generator.generate(output_path, max_news=10)
    
    print(f"\n🌐 브라우저에서 확인: {output_path}")
