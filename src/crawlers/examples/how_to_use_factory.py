"""
신문사 크롤러 팩토리 사용 예시
새로운 신문사를 쉽게 추가하는 방법
"""

from newspaper_factory import NewspaperFactory, NewspaperConfig

# ============================================================
# 방법 1: 사전 정의된 신문사 사용
# ============================================================

# 서울신문 크롤러 생성
seoul_crawler = NewspaperFactory.create('서울신문')
if seoul_crawler:
    articles = seoul_crawler.crawl(max_articles=10)
    print(f"수집된 기사: {len(articles)}개")

# 사용 가능한 신문사 목록 확인
available = NewspaperFactory.list_available()
print(f"사용 가능한 신문사: {available}")


# ============================================================
# 방법 2: 새로운 신문사 추가 (설정만으로!)
# ============================================================

# 예시: 부산일보 크롤러 추가
busan_config = NewspaperConfig(
    newspaper_name='부산일보',
    region='부산',
    base_url='https://www.busan.com',
    list_url='https://www.busan.com/news/economy',
    article_link_selector='div.news-list a',  # 실제 선택자로 변경 필요
    content_selectors=['div.article-body', 'div.content'],
    parsing_method='paragraphs'  # 'selector', 'paragraphs', 'textlines' 중 선택
)

# 크롤러 생성 및 실행
busan_crawler = NewspaperFactory.create_custom(busan_config)
articles = busan_crawler.crawl(max_articles=5)


# ============================================================
# 방법 3: 다양한 파싱 방법 비교
# ============================================================

# 1) selector 방법: CSS 선택자로 직접 추출
config_selector = NewspaperConfig(
    newspaper_name='테스트신문',
    region='테스트',
    base_url='https://example.com',
    list_url='https://example.com/news',
    article_link_selector='a.article',
    content_selectors=['div.article-content', 'article.main'],
    parsing_method='selector'
)

# 2) paragraphs 방법: p 태그들에서 추출
config_paragraphs = NewspaperConfig(
    newspaper_name='테스트신문2',
    region='테스트',
    base_url='https://example.com',
    list_url='https://example.com/news',
    article_link_selector='a.article',
    content_selectors=['article'],  # 컨테이너 선택자
    parsing_method='paragraphs'
)

# 3) textlines 방법: br 태그로 구분된 텍스트 추출
config_textlines = NewspaperConfig(
    newspaper_name='테스트신문3',
    region='테스트',
    base_url='https://example.com',
    list_url='https://example.com/news',
    article_link_selector='a.article',
    content_selectors=['div.content'],
    parsing_method='textlines'
)


# ============================================================
# 방법 4: 유틸리티 직접 사용
# ============================================================

from utils import ContentParser, DateParser, TextCleaner

# ContentParser 사용 예시
from bs4 import BeautifulSoup

html = """
<div class="article">
    <h1>제목</h1>
    <div class="content">
        <p>첫 번째 문단입니다.</p>
        <p>두 번째 문단입니다.</p>
        <script>광고 스크립트</script>
    </div>
</div>
"""

soup = BeautifulSoup(html, 'html.parser')

# 여러 선택자 시도
content = ContentParser.extract_from_selector(
    soup, 
    ['div.content', 'article.main', 'div.article-body']
)
print(f"추출된 본문: {content}")

# p 태그에서 추출
content = ContentParser.extract_from_paragraphs(soup, 'div.content')
print(f"문단 추출: {content}")


# DateParser 사용 예시
text = "승인 2026-02-23 15:30 | 홍길동 기자"

date = DateParser.extract_date(text)
print(f"날짜: {date}")

writer = DateParser.extract_writer(text)
print(f"작성자: {writer}")


# TextCleaner 사용 예시
dirty_text = "뉴스    기사   내용입니다.   https://example.com   홍길동@example.com"

clean_text = TextCleaner.clean_article_text(dirty_text)
print(f"정제된 텍스트: {clean_text}")

# 문장 분리
sentences = TextCleaner.extract_sentences("첫 문장입니다. 두 번째 문장! 세 번째 문장?")
print(f"문장들: {sentences}")


# ============================================================
# 실전 예시: 새 지역 신문 10개 추가하기
# ============================================================

# 충청일보, 전라일보, 제주일보 등을 쉽게 추가
new_newspapers = [
    NewspaperConfig(
        newspaper_name='충청일보',
        region='충청도',
        base_url='https://www.ccdailynews.com',
        list_url='https://www.ccdailynews.com/news/economy',
        article_link_selector='div.article-list a',
        content_selectors=['div.article-body'],
        parsing_method='paragraphs'
    ),
    # ... 더 많은 신문사 추가
]

# 일괄 크롤링
for config in new_newspapers:
    crawler = NewspaperFactory.create_custom(config)
    articles = crawler.crawl(max_articles=10)
    print(f"{config.newspaper_name}: {len(articles)}개 수집")
