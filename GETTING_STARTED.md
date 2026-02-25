# 🕷️ 지역 경제 뉴스 크롤러 시작 가이드

## 📁 프로젝트 구조

```
Project_mini/
├── .github/
│   └── copilot-instructions.md
├── src/
│   └── crawlers/
│       ├── base_crawler.py              # 부모 클래스 (추상화)
│       ├── crawler_manager.py           # 통합 관리자
│       ├── run_crawlers.py              # 메인 실행 스크립트
│       └── regional/
│           ├── seoul/
│           │   └── seoul_shinmun.py     # 서울신문 크롤러
│           ├── gyeonggi/
│           │   └── gyeonggi_ilbo.py     # 경기일보 크롤러
│           └── gangwon/
│               └── gangwon_domin_ilbo.py # 강원도민일보 크롤러
├── data/
│   └── regional_news.csv                # 출력 파일 (생성됨)
├── requirements.txt
├── test_crawler.py
└── README.md
```

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 테스트 실행 (각 신문사 5개 기사)

```bash
python test_crawler.py
```

### 3. 전체 크롤링 실행

```bash
# 모든 지역 크롤링 (각 신문사 50개 기사)
cd src/crawlers
python run_crawlers.py --mode all --articles 50
```

### 4. 특정 지역만 크롤링

```bash
# 서울만 크롤링
python run_crawlers.py --mode region --region 서울 --articles 30

# 경기도만 크롤링
python run_crawlers.py --mode region --region 경기도 --articles 30

# 강원도만 크롤링
python run_crawlers.py --mode region --region 강원도 --articles 30
```

## 📊 출력 파일

크롤링된 데이터는 `data/regional_news.csv`에 저장됩니다.

**CSV 구조:**
- title: 기사 제목
- content: 기사 본문
- url: 기사 URL
- date: 발행 날짜
- writer: 기자명
- source: 신문사명
- newspaper: 신문사명 (동일)
- region: 지역명
- collected_at: 수집 시간

## 🔧 새로운 신문사 추가 방법

### 1. 새 크롤러 클래스 생성

예: 인천일보 추가하기

```python
# src/crawlers/regional/seoul/incheon_ilbo.py

from base_crawler import BaseCrawler
from typing import List, Dict, Optional
from datetime import datetime

class IncheonIlboCrawler(BaseCrawler):
    """인천일보 경제섹션 크롤러"""
    
    def __init__(self):
        config = {
            'article_selector': 'div.news-list',
            'title_selector': 'h3.title',
            'link_selector': 'a.link',
        }
        
        super().__init__(
            newspaper_name='인천일보',
            region='서울',  # 또는 '인천'
            base_url='https://www.incheon.com',
            config=config
        )
    
    def get_article_urls(self) -> List[str]:
        # URL 추출 로직
        pass
    
    def parse_article(self, url: str) -> Optional[Dict]:
        # 기사 파싱 로직
        pass
```

### 2. 크롤러 매니저에 등록

```python
# src/crawlers/crawler_manager.py

from regional.seoul.incheon_ilbo import IncheonIlboCrawler

def register_all_crawlers(self):
    crawlers_list = [
        SeoulShinmunCrawler(),
        GyeonggiIlboCrawler(),
        GangwonDominIlboCrawler(),
        IncheonIlboCrawler(),  # 추가!
    ]
```

**끝!** 🎉

## 💡 주의사항

1. **CSS 선택자 확인**: 각 신문사 사이트의 실제 HTML 구조에 맞게 선택자를 수정해야 합니다.
2. **크롤링 예의**: `time.sleep(0.3)`으로 서버 부하를 방지합니다.
3. **User-Agent**: 봇 차단 방지를 위해 User-Agent를 설정합니다.
4. **에러 처리**: 네트워크 오류, 타임아웃 등을 자동으로 처리합니다.

## 📚 추가 리소스

- BeautifulSoup 문서: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Selenium 문서: https://www.selenium.dev/documentation/
- CSS 선택자 가이드: https://www.w3schools.com/cssref/css_selectors.php

## ✨ 기능

- ✅ OOP 설계 (상속, 추상화)
- ✅ 재사용 가능한 Base 클래스
- ✅ 확장 가능한 구조
- ✅ 에러 처리 및 로깅
- ✅ CSV 출력
- ✅ CLI 인터페이스
- ✅ 지역별/전체 크롤링 선택 가능

---

**Happy Crawling! 🚀**
