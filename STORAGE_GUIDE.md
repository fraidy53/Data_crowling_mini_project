# 사용 가이드: 크롤링 결과 저장

## 🎯 3가지 저장 방식

크롤링된 뉴스는 자동으로 3가지 형식으로 저장됩니다:

1. **CSV 파일** - 데이터 분석용
2. **SQLite 데이터베이스** - 구조화된 쿼리용
3. **텍스트 파일** - 원본 뉴스 보관용

---

## 🚀 빠른 시작

### 1. 전체 저장 (기본)

```bash
cd src/crawlers
python run_crawlers.py --mode all --articles 50
```

**결과:**
- ✅ CSV: `data/regional_news.csv`
- ✅ DB: `data/news.db`
- ✅ 텍스트: `data/articles/[지역]/*.txt`

### 2. 특정 지역만

```bash
python run_crawlers.py --mode region --region 서울 --articles 30
```

### 3. 저장 옵션 선택

```bash
# CSV만 저장 (데이터베이스, 텍스트 파일 제외)
python run_crawlers.py --mode all --no-save-db --no-save-text

# 데이터베이스만 저장
python run_crawlers.py --mode all --save-db
```

---

## 📊 저장된 데이터 확인

### CSV 파일 보기
```bash
# PowerShell에서
Import-Csv data/regional_news.csv | Select-Object -First 10 | Format-Table
```

### 데이터베이스 조회
```bash
# SQLite 설치 필요
sqlite3 data/news.db

# SQL 쿼리
SELECT region, COUNT(*) FROM news GROUP BY region;
SELECT title, source FROM news WHERE region='서울' LIMIT 5;
.quit
```

### 텍스트 파일 보기
```bash
# 인덱스 파일 확인
cat data/articles/index.txt

# 특정 기사 읽기
cat data/articles/서울/20260223_*.txt
```

---

## 🔍 Python에서 데이터 접근

### CSV 읽기
```python
import pandas as pd

df = pd.read_csv('data/regional_news.csv')
print(df.head())
print(df.groupby('region').size())
```

### 데이터베이스 읽기
```python
import sqlite3

conn = sqlite3.connect('data/news.db')

# 서울 지역 뉴스
df = pd.read_sql_query(
    "SELECT * FROM news WHERE region='서울'", 
    conn
)
print(df)

conn.close()
```

### 텍스트 파일 읽기
```python
import os

# 서울 지역 텍스트 파일들
seoul_dir = 'data/articles/서울'
for filename in os.listdir(seoul_dir):
    filepath = os.path.join(seoul_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content[:200])  # 처음 200자
```

---

## 📁 저장 구조

```
data/
├── regional_news.csv          # CSV 파일
├── news.db                    # SQLite 데이터베이스
├── articles/                  # 텍스트 파일들
│   ├── index.txt             # 전체 인덱스
│   ├── 서울/
│   │   ├── 20260223_143022_기사제목1.txt
│   │   └── 20260223_143023_기사제목2.txt
│   ├── 경기도/
│   │   └── ...
│   └── 강원도/
│       └── ...
└── DATABASE_GUIDE.md         # 데이터베이스 가이드
```

---

## 💡 활용 예시

### 1. 지역별 감성 분석
```python
# 1. 데이터베이스에서 지역별로 읽기
# 2. KoBERT로 감성 분석
# 3. 결과를 다시 데이터베이스에 저장
```

### 2. 키워드 추출
```python
# 1. 텍스트 파일 읽기
# 2. TF-IDF로 키워드 추출
# 3. 지역별 TOP 10 키워드 생성
```

### 3. 시계열 분석
```python
# 1. CSV 또는 DB에서 날짜별 데이터 로드
# 2. 시간대별 뉴스 감성 변화 분석
# 3. Plotly로 시각화
```

---

## ⚠️ 주의사항

1. **용량 관리**: 텍스트 파일은 용량이 클 수 있으므로 필요시 `--no-save-text` 옵션 사용
2. **중복 방지**: 데이터베이스는 URL 기준으로 중복을 자동 제거
3. **백업**: 정기적으로 `data/` 폴더를 백업하세요

---

**Happy Analyzing! 📊**
