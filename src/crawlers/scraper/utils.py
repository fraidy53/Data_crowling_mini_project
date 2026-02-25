import os
import logging
import pandas as pd
from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor
import urllib3

# SSL 경고 및 종속성 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['PYTHONWARNINGS'] = 'ignore:semaphore_tracker:UserWarning'

def ensure_dirs():
    """필요한 디렉토리 생성"""
    for d in ['logs', 'data']:
        os.makedirs(d, exist_ok=True)

def get_logger(name, level=logging.DEBUG): # 디버깅을 위해 기본 레벨을 DEBUG로 변경
    """실행 시간별 로그 파일 설정"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{name}_{timestamp}.log"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

def get_common_headers():
    """브라우저와 최대한 유사한 공통 HTTP 헤더"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1"
    }

def common_parse_date(date_str):
    """날짜 형식 정규화 (YYYY-MM-DD)"""
    now = datetime.now()
    date_str = date_str.strip().replace('\n', ' ')
    try:
        if '분 전' in date_str:
            minutes = int(re.findall(r'\d+', date_str)[0])
            target_date = now - timedelta(minutes=minutes)
        elif '시간 전' in date_str:
            hours = int(re.findall(r'\d+', date_str)[0])
            target_date = now - timedelta(hours=hours)
        elif '어제' in date_str:
            target_date = now - timedelta(days=1)
        else:
            match = re.search(r'(\d{4})[. -](\d{1,2})[. -](\d{1,2})', date_str)
            if match:
                y, m, d = match.groups()
                target_date = datetime(int(y), int(m), int(d))
            else:
                match = re.search(r'(\d{1,2})[. -](\d{1,2})\s*(\d{4})', date_str)
                if match:
                    m, d, y = match.groups()
                    target_date = datetime(int(y), int(m), int(d))
                else:
                    target_date = now
    except:
        target_date = now
    return target_date.strftime('%Y-%m-%d')

def clean_text(text):
    """본문 텍스트 정제 (노이즈 제거)"""
    if not text: return ""
    text = re.split(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)[0]
    noise_keywords = ["저작권자", "다른기사 보기", "좋아요 0", "훈훈해요 0", "슬퍼요 0", "화나요 0", "관련기사", "재배포 금지", "무단 전재", "기자 ="]
    for kw in noise_keywords:
        if kw in text: text = text.split(kw)[0]
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'/[가-힣]{2,4}\s*기자.*$', '', text, flags=re.MULTILINE)
    return text.strip()

def fetch_url(url, headers, logger, session=None, retries=3, backoff_factor=1.5):
    """재시도 로직이 포함된 URL 요청 함수"""
    fetcher = session if session else requests
    
    for i in range(retries):
        try:
            # 타임아웃 20초, SSL 검증 무시
            response = fetcher.get(url, headers=headers, timeout=20, verify=False)
            if response.status_code == 200:
                # UTF-8 강제 지정 후 즉시 반환
                response.encoding = 'utf-8'
                return response
            elif response.status_code in [403, 401, 429]:
                print(f"[DEBUG] HTTP {response.status_code} Error: {url}")
                logger.warning(f"Status {response.status_code} for {url}. ({i+1}/{retries})")
                time.sleep(backoff_factor ** i)
            else:
                print(f"[DEBUG] HTTP Error {response.status_code}: {url}")
                logger.error(f"Failed to fetch {url}: Status {response.status_code}")
                return None
        except Exception as e:
            # 에러의 실체를 콘솔에 즉시 출력
            print(f"\n[DEBUG] Error Fetching URL: {url}")
            print(f"[DEBUG] Exception Type: {type(e).__name__}")
            print(f"[DEBUG] Exception Message: {str(e)}")
            wait_time = backoff_factor ** i
            logger.error(f"Error fetching {url}: {str(e)} (Type: {type(e).__name__})")
            time.sleep(wait_time)
    
    logger.error(f"Max retries exceeded for {url}")
    return None

def fetch_article_details(url, selectors, headers, logger, session=None):
    """기사 상세 페이지에서 정보 추출 (재시도 로직 적용)"""
    details = {'sub_title': '', 'content': ''}
    if not url: return details
    try:
        response = fetch_url(url, headers, logger, session=session)
        if response and response.status_code == 200:
            # 인코딩 오류 방지: ISO-8859-1로 잘못 감지되는 경우 utf-8 강제 시도
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            # BeautifulSoup에서 명시적으로 utf-8을 감지하도록 content 사용
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
            
            # Sub Title
            st_sel = selectors.get('sub_title')
            if st_sel:
                st_selectors = st_sel if isinstance(st_sel, list) else [st_sel]
                for s in st_selectors:
                    tag = soup.select_one(s)
                    if tag:
                        details['sub_title'] = tag.get_text(" ", strip=True)
                        break
            
            # Content
            c_sel = selectors.get('content')
            if c_sel:
                c_selectors = c_sel if isinstance(c_sel, list) else [c_sel]
                for s in c_selectors:
                    tag = soup.select_one(s)
                    if tag:
                        for noise in tag.select('script, style, iframe, ins, .quizContainer, .articleCopyright, figcaption, .byline, .article-copy, .banner_box, .account, .relation, .ad-template'):
                            noise.decompose()
                        details['content'] = clean_text(tag.get_text(" ", strip=True))
                        break
    except Exception as e:
        logger.debug(f"Error parsing details for {url}: {e}")
    return details

def save_to_csv(data, file_name, logger):
    """데이터 저장"""
    if not data:
        logger.warning(f"No data to save for {file_name}.")
        return False
    columns = ['date', 'press', 'region', 'title', 'sub_title', 'description', 'content', 'article_url', 'image_url']
    try:
        df = pd.DataFrame(data)
        for col in columns:
            if col not in df.columns: df[col] = ""
        df = df[columns].drop_duplicates(subset=['article_url'])
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        logger.info(f"Successfully saved {len(df)} items to {file_name}.")
        return True
    except PermissionError:
        logger.error(f"Permission denied: Close '{file_name}' and retry.")
        return False
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False