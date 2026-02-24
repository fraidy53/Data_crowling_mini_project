# 재사용 가능한 크롤링 모듈 설계

## 📁 프로젝트 구조

```
src/crawlers/
├── utils/                      # 재사용 유틸리티
│   ├── __init__.py
│   ├── content_parser.py       # 본문 파싱
│   ├── date_parser.py          # 날짜/메타데이터 추출
│   └── text_cleaner.py         # 텍스트 정제
│
├── newspaper_factory.py        # 신문사 크롤러 팩토리
├── base_crawler.py             # 기본 크롤러 클래스
│
└── examples/                   # 사용 예시
    └── how_to_use_factory.py
```

---

## 🎯 주요 클래스

### 1. ContentParser (본문 파싱)
```python
from utils import ContentParser

# 방법 1: CSS 선택자로 추출
content = ContentParser.extract_from_selector(
    soup, 
    ['div.article-body', 'article.content']
)

# 방법 2: p 태그에서 추출
content = ContentParser.extract_from_paragraphs(
    soup,
    container_selector='div.article'
)

# 방법 3: 텍스트 라인으로 추출 (br 태그 구분)
content = ContentParser.extract_from_textlines(
    soup,
    container_selector='div.content'
)
```

### 2. DateParser (날짜/작성자 추출)
```python
from utils import DateParser

text = "승인 2026-02-23 15:30 | 홍길동 기자"

date = DateParser.extract_date(text)      # "2026-02-23"
writer = DateParser.extract_writer(text)  # "홍길동"
```

### 3. TextCleaner (텍스트 정제)
```python
from utils import TextCleaner

dirty = "뉴스   내용  https://example.com  hong@email.com"
clean = TextCleaner.clean_article_text(dirty)
# "뉴스 내용"

sentences = TextCleaner.extract_sentences("첫 문장. 두 번째! 세 번째?")
# ["첫 문장", "두 번째", "세 번째"]
```

---

## 🏭 NewspaperFactory (신문사 추가)

### 방법 1: 사전 정의된 신문사 사용
```python
from newspaper_factory import NewspaperFactory

# 서울신문 크롤러 자동 생성
crawler = NewspaperFactory.create('서울신문')
articles = crawler.crawl(max_articles=10)

# 사용 가능한 신문사 목록
print(NewspaperFactory.list_available())
# ['서울신문', '경기일보', '강원도민일보']
```

### 방법 2: 새 신문사 추가 (설정만으로!)
```python
from newspaper_factory import NewspaperFactory, NewspaperConfig

# 1. 설정 작성 (코드 5줄)
config = NewspaperConfig(
    newspaper_name='부산일보',
    region='부산',
    base_url='https://www.busan.com',
    list_url='https://www.busan.com/news/economy',
    article_link_selector='div.news-list a',
    content_selectors=['div.article-body', 'div.content'],
    parsing_method='paragraphs'
)

# 2. 크롤러 생성 및 실행 (코드 2줄)
crawler = NewspaperFactory.create_custom(config)
articles = crawler.crawl(max_articles=10)
```

---

## 📝 파싱 방법 선택 가이드

| 파싱 방법 | 언제 사용? | 예시 |
|---------|---------|------|
| `selector` | 명확한 본문 div가 있을 때 | `<div class="article-body">본문</div>` |
| `paragraphs` | p 태그로 구성될 때 | `<p>문단1</p><p>문단2</p>` |
| `textlines` | br 태그로 구분될 때 | `텍스트1<br>텍스트2<br>` |

---

## 🚀 실전 사용 예시

### 예시 1: 10개 지역 신문 한번에 추가
```python
regions = [
    ('충청일보', '충청도', 'https://www.ccdailynews.com'),
    ('전라일보', '전라도', 'https://www.jeollailbo.com'),
    ('제주일보', '제주도', 'https://www.jejuilbo.net'),
    # ... 7개 더
]

for name, region, base_url in regions:
    config = NewspaperConfig(
        newspaper_name=name,
        region=region,
        base_url=base_url,
        list_url=f'{base_url}/news/economy',
        article_link_selector='a.article',
        content_selectors=['div.article-body'],
        parsing_method='paragraphs'
    )
    
    crawler = NewspaperFactory.create_custom(config)
    articles = crawler.crawl(max_articles=10)
    print(f"{name}: {len(articles)}개 수집 완료")
```

### 예시 2: 크롤러 매니저에 통합
```python
from crawler_manager import CrawlerManager
from newspaper_factory import NewspaperFactory

manager = CrawlerManager()

# 기존 크롤러들
manager.register_crawler(NewspaperFactory.create('서울신문'))
manager.register_crawler(NewspaperFactory.create('경기일보'))

# 새로운 크롤러 쉽게 추가
busan_crawler = NewspaperFactory.create_custom(busan_config)
manager.register_crawler(busan_crawler)

manager.run_all_crawlers()
```

---

## ✨ 장점

1. **코드 재사용**: 공통 로직을 유틸리티로 분리
2. **쉬운 확장**: 설정만으로 새 신문사 추가 (5분 소요)
3. **일관된 품질**: 모든 크롤러가 동일한 정제 로직 사용
4. **유지보수 용이**: 한 곳 수정으로 모든 크롤러 개선

---

## 🔧 커스터마이징

### ContentParser 필터 추가
```python
# utils/content_parser.py

ContentParser.NOISE_KEYWORDS.extend([
    '추가키워드1',
    '추가키워드2'
])
```

### DateParser 패턴 추가
```python
# utils/date_parser.py

DateParser.DATE_PATTERNS.append(
    r'발행\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)'
)
```

---

## 📊 성능

- **기존 방식**: 신문사당 100줄 코드, 중복 많음
- **개선 방식**: 신문사당 5줄 설정, 중복 제거

**코드 감소율: 95% ↓**

---

## 🎓 다음 단계

1. ✅ 재사용 모듈 완성
2. 🔄 기존 크롤러를 Factory 방식으로 전환
3. 📈 새 지역 신문 10개 추가
4. 🤖 AI 기반 자동 선택자 탐지 (고급)

---

## 📞 문의

새로운 신문사 추가나 커스터마이징이 필요하면 `newspaper_factory.py`의 PRESETS에 추가하거나, 커스텀 설정을 사용하세요!
