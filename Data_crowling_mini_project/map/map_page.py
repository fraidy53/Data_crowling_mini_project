"""
Streamlit 지도 페이지
뉴스 지도를 Streamlit 앱으로 표시
"""

import streamlit as st
import streamlit.components.v1 as components
import os

from map_generator import NewsMapGenerator
from db_loader import NewsDBLoader


def render_map_page():
    """지도 페이지 렌더링"""
    
    st.title("📍 지역별 뉴스 지도")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        max_news = st.slider(
            "지역당 표시할 뉴스 개수",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )
        
        refresh_button = st.button("🔄 지도 새로고침", use_container_width=True)
    
    # 통계 표시
    loader = NewsDBLoader()
    stats = loader.get_region_stats()
    
    st.subheader("📊 지역별 통계")
    
    cols = st.columns(3)
    
    total_news = sum(stat['count'] for stat in stats.values())
    avg_sentiment = sum(stat['avg_sentiment'] * stat['count'] for stat in stats.values()) / total_news if total_news > 0 else 0
    
    with cols[0]:
        st.metric("총 뉴스", f"{total_news}개")
    with cols[1]:
        st.metric("평균 감성", f"{avg_sentiment:.2f}")
    with cols[2]:
        positive_ratio = sum(stat['positive_count'] for stat in stats.values()) / total_news * 100 if total_news > 0 else 0
        st.metric("긍정 비율", f"{positive_ratio:.1f}%")
    
    st.markdown("---")
    
    # 지역별 상세 통계
    with st.expander("📋 지역별 상세 통계"):
        for region in sorted(stats.keys()):
            stat = stats[region]
            st.markdown(f"**{region}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("뉴스", f"{stat['count']}개")
            col2.metric("평균 감성", f"{stat['avg_sentiment']:.2f}")
            col3.metric("긍정", f"{stat['positive_count']}개")
            col4.metric("부정", f"{stat['negative_count']}개")
            st.markdown("---")
    
    # 지도 생성
    with st.spinner('🗺️ 지도 생성 중...'):
        # 임시 HTML 파일 생성
        temp_map_file = os.path.join(os.path.dirname(__file__), 'temp_news_map.html')
        
        generator = NewsMapGenerator()
        generator.generate(temp_map_file, max_news=max_news)
        
        # HTML 읽기
        with open(temp_map_file, 'r', encoding='utf-8') as f:
            map_html = f.read()
        
        # Streamlit에 표시
        st.components.v1.html(map_html, height=600, scrolling=True)
    
    # 사용법 안내
    with st.expander("ℹ️ 사용법"):
        st.markdown("""
        ### 지도 사용법
        
        1. **마커 색상**:
           - 🔵 파란색: 긍정적인 뉴스가 많은 지역
           - 🔴 빨간색: 부정적인 뉴스가 많은 지역
           - ⚪ 회색: 중립적인 뉴스
        
        2. **원 크기**: 뉴스 개수에 비례
        
        3. **마커 클릭**: 해당 지역의 상세 뉴스 목록 표시
           - 제목, 키워드, 감성 점수, 발행일
           - 기사 링크 클릭 가능
        
        4. **설정**: 왼쪽 사이드바에서 표시할 뉴스 개수 조정
        """)


if __name__ == '__main__':
    # Streamlit 앱으로 실행
    st.set_page_config(
        page_title="뉴스 지도",
        page_icon="📍",
        layout="wide"
    )
    
    render_map_page()
