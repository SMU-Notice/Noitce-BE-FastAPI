import requests
from bs4 import BeautifulSoup
import re

# 크롤링할 게시판 URL
base_url = "https://www.smu.ac.kr/kor/life/notice.do"
params = {"mode": "list", "articleLimit": 20, "article.offset": 0}

def fetch_notices():
    # 웹페이지 요청
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # 요청 실패 시 예외 발생

    # HTML 파싱
    soup = BeautifulSoup(response.text, "html.parser")

    # 게시글 목록 추출
    notices = {}

    for li in soup.select(".board-thumb-wrap > li"):
        # 🔍 `.noti` 클래스를 가진 요소가 있는 경우 무시
        if li.select_one(".noti"):
            continue

        # 📌 게시글 ID
        article_id_tag = li.select_one(".board-thumb-content-number")
        article_id = article_id_tag.get_text(strip=True) if article_id_tag else "N/A"
        article_id = re.sub(r"No\.", "", article_id).strip()  # "No." 제거

        # 🔗 게시글 URL
        article_link_tag = li.select_one(".board-thumb-content-title a")
        article_url = base_url + article_link_tag["href"] if article_link_tag else "N/A"

        # 📝 제목
        title_tag = li.select_one("td:nth-of-type(3) a")
        title = title_tag.text.strip() if title_tag else "N/A"

        # 📅 게시 날짜
        date_tag = li.select_one(".board-thumb-content-date")
        date = date_tag.text.strip() if date_tag else "N/A"
        date = re.sub(r"작성일", "", date).strip()

        # 🏷 카테고리 (일반, 학사 등)
        category_tag = li.select_one(".cate")
        category = category_tag.text.strip("[]") if category_tag else "N/A"

        # 🏫 캠퍼스 정보
        campus_tag = li.select_one(".cmp")
        if campus_tag:
            campus_class = campus_tag["class"]  # 클래스 목록 가져오기
            if "cheon" in campus_class:
                campus = "천안"
            elif "seoul" in campus_class:
                campus = "서울"
            elif "sang" in campus_class:
                campus = "상명"
            else:
                campus = "N/A"
        else:
            campus = "N/A"

        # 👀 조회수
        views_tag = li.select_one(".board-thumb-content-views")
        views = views_tag.text.strip() if views_tag else "0"
        views = re.sub(r"조회수", "", views).strip()  # "조회수" 제거

        # 🗂 해시 테이블에 저장
        notices[article_id] = {
            "id": article_id,
            "title": title,
            "date": date,
            "campus": campus,
            "category": category,
            "views": views,
            "url": article_url
        }

    return notices
