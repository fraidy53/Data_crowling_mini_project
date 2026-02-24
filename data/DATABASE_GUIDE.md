# 데이터베이스 가이드

## 📊 데이터베이스 구조

### **news 테이블** (뉴스 기사)
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    date TEXT,
    writer TEXT,
    source TEXT,
    newspaper TEXT,
    region TEXT,
    collected_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### **region_stats 테이블** (지역별 통계)
```sql
CREATE TABLE region_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT,
    newspaper TEXT,
    article_count INTEGER,
    last_crawled TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 💾 저장 위치
- **파일**: `data/news.db`
- **도구**: SQLite3

## 🔍 데이터 조회 방법

### Python으로 조회
```python
import sqlite3

conn = sqlite3.connect('data/news.db')
cursor = conn.cursor()

# 전체 기사 수
cursor.execute('SELECT COUNT(*) FROM news')
print(f"전체 기사: {cursor.fetchone()[0]}개")

# 지역별 기사 수
cursor.execute('SELECT region, COUNT(*) FROM news GROUP BY region')
for region, count in cursor.fetchall():
    print(f"{region}: {count}개")

conn.close()
```

### SQLite CLI로 조회
```bash
# 데이터베이스 열기
sqlite3 data/news.db

# 테이블 목록
.tables

# 전체 기사 수
SELECT COUNT(*) FROM news;

# 서울 지역 기사
SELECT title, source, date FROM news WHERE region='서울' LIMIT 10;

# 종료
.quit
```

## 📁 텍스트 파일 구조

```
data/articles/
├── index.txt              # 전체 인덱스 파일
├── 서울/
│   ├── 20260223_143022_기사제목1.txt
│   └── 20260223_143023_기사제목2.txt
├── 경기도/
│   ├── 20260223_143024_기사제목3.txt
│   └── 20260223_143025_기사제목4.txt
└── 강원도/
    ├── 20260223_143026_기사제목5.txt
    └── 20260223_143027_기사제목6.txt
```

### 텍스트 파일 형식
```
======================================================================
제목: 부산항 컨테이너 물동량 47% 증가
======================================================================

신문사: 부산일보
지역: 경상도
발행일: 2026-02-23
기자: 홍길동
URL: https://www.busan.com/article/12345
수집일시: 2026-02-23 14:30:22

----------------------------------------------------------------------

본문:

부산항의 컨테이너 물동량이 전년 대비 47% 증가하며...
(뉴스 본문 전체)

======================================================================
```
