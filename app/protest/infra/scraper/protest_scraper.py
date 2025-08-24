# protest_event.py

import io
import re
import logging
from datetime import date, time, datetime, timedelta
from typing import List, Dict, Tuple

import requests
import pdfplumber      
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

from urllib.parse import urljoin
import os

# ProtestEvent 도메인 객체 import
from app.protest.domain.protest_event import ProtestEvent

logger = logging.getLogger(__name__)

# 위치 저장 때 양방향 화살표, 단방향 화살표 등 모두 - 로 처리
_ARROW_PATTERN = re.compile(r"[→←↔⇄⟶⟵➔➝➞➟➠➥➦➧]")


class ProtestScraper:
    """종로경찰청 시위 정보 스크래퍼"""
    
    def __init__(self):
        self.list_url = os.getenv("LIST_URL", "https://www.smpa.go.kr/user/nd54882.do")
        self.download_url = os.getenv("DOWNLOAD_URL", "https://www.smpa.go.kr/common/attachfile/attachfileDownload.do")
        
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        """요청 세션 생성 (유저 세팅)"""
        s = requests.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Referer": self.list_url,
        })
        return s

    def _collect_board_no(self) -> List[str]:
        """종로경찰청 게시판을 순회하면서 게시글들의 번호를 추출하는 역할 담당"""
        params = {
            "page": 1,               # 첫 페이지(종로경찰청 기준 게시글 10개)만 순회
            "dmlType": "SELECT",
            "pageST": "SUBJECT",
            "pageSV": "",
            "imsi": "imsi",
            "pageSC": "SORT_ORDER",
            "pageSO": "DESC",
        }
        
        resp = self.session.get(self.list_url, params=params)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        board_nos: List[str] = []
        for a in soup.select("td.subject a"):   # 게시글 목록들 순회
            href = a.get("href", "")
            m = re.search(r"goBoardView\('[^']+','[^']+','([^']+)'\)", href)    # 게시물 번호들만 추출
            if m:
                board_nos.append(m.group(1))

        logger.info("게시글 수집 완료")
        return board_nos

    def _collect_attachments(self, board_nos: List[str]) -> List[Tuple[str, str, str]]:
        """앞서 추출된 게시글들의 첨부파일(PDF)의 다운로드 링크 식별자, 날짜(파일명), 상세게시물 주소를 모음"""
        attach_list: List[Tuple[str, str, str]] = []

        for no in board_nos:
            detail_url = f"{self.list_url}?View&boardNo={no}"    # 추출했던 게시물 번호 조합으로 상세 게시물 링크 이용
            r = self.session.get(detail_url)
            r.raise_for_status()
            s2 = BeautifulSoup(r.text, "html.parser")

            for a in s2.select("a.doc_link"):   # 파일들 중 .pdf로 끝나는지 확인
                fn = a.get_text(strip=True)
                if not fn.lower().endswith(".pdf"):
                    continue
                onclick = a.get("onclick", "")
                m = re.search(r"attachfileDownload\('[^']+','([^']+)'\)", onclick) # 두번째 인자로 attachNo(첨부파일 번호) 가져옴
                if not m:
                    continue
                attach_no = m.group(1)
                attach_list.append((attach_no, fn, detail_url))

        logger.info("다운로드 대상 PDF 확인 완료")
        return attach_list

    def _download_pdf(self, attach_no: str, referer: str) -> bytes | None:
        """첨부파일 번호로 PDF를 찾아 바이트로 메모리에 저장"""
        r = self.session.get(
            self.download_url,
            params={"attachNo": attach_no},
            headers={"Referer": referer},
            stream=True,
        )

        ct = r.headers.get("Content-Type", "")  # 타입이 pdf인지 확인
        if r.status_code != 200 or (("pdf" not in ct) and ("octet-stream" not in ct)):
            logger.warning("PDF가 아닌 응답 혹은 실패한 응답 (%s / %s)", r.status_code, ct)
            return None

        return r.content

    def _extract_events(self, pdf_bytes: bytes, filename: str) -> List[ProtestEvent]:
        """PDF에서 표를 읽어 필요한 이벤트 추출"""
        events: List[ProtestEvent] = []

        # 파일명에서  YY / MM / DD 끊어서 찾기
        m = re.match(r"(\d{2})(\d{2})(\d{2})", filename)
        if not m:
            logger.warning("파일명에서 날짜 파싱 실패: %s", filename)
            return events
        
        yy, mm, dd = m.groups()

        try:
            pd_date = date(2000 + int(yy), int(mm), int(dd))   # 파일명으로 시위일 생성
        except ValueError:
            logger.warning("올바르지 않은 날짜: %s", filename)
            return events

        # pdf에서 표 추출
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                table = pdf.pages[0].extract_table({
                    "vertical_strategy":   "lines",
                    "horizontal_strategy": "lines",
                })
        except Exception as e:
            logger.exception("PDF 파싱 실패: %s (%s)", filename, e)
            return events

        if not table or len(table) < 2:
            logger.warning("표를 찾지 못함: %s", filename)
            return events

        # 행 순회
        for row in table[1:]:
            time_cell   = row[0] if len(row) > 0 else None  # 집회 일시
            place_cell  = row[1] if len(row) > 1 else None  # 집회 장소(행진로)
            station_cell= row[3] if len(row) > 3 else None  # 관할서

            if not time_cell or not station_cell:
                continue

            # "종 로" 포함 행만 사용
            if not re.search(r"종\s*로", str(station_cell)):
                continue

            # 시위 시간 파싱
            try:
                s = str(time_cell).replace("~\n", "~").replace("\n", " ").strip()
                m2 = re.match(r"(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})", s)  
                if m2:
                    start_s, end_s = m2.group(1), m2.group(2)   # 시작시간 / 종료 시간 처리
                else:
                    m3 = re.match(r"(\d{1,2}:\d{2})\s*~", s)    # 시작 시간만 있는 경우 시작 시간 = 종료 시간 동일하게 처리
                    if not m3:
                        logger.warning("시간 파싱 실패: %r (%s)", time_cell, filename)
                        continue
                    start_s = end_s = m3.group(1)

                sh, sm = map(int, start_s.split(":", 1))
                eh, em = map(int, end_s.split(":", 1))
                start_t = time(sh, sm)
                end_t = time(eh, em)

            except Exception:
                logger.warning("시간 파싱 실패: %r (%s)", time_cell, filename)
                continue

            # 장소 문자열 정리
            place = ("" if place_cell is None else str(place_cell)).replace("\n", " ").strip()
            place = re.sub(r"<[^>]*>", "", place)          # 불필요 태그 제거
            place = _ARROW_PATTERN.sub("-", place)         # 화살표류 → '-'
            place = re.sub(r"\s*-\s*", " - ", place)       # 하이픈 주변 공백 표준화
            place = re.sub(r"\s{2,}", " ", place).strip()   # 중복 공백 축소

            # ProtestEvent 도메인 객체 생성
            events.append(ProtestEvent(
                location=place,
                protest_date=pd_date,
                start_time=start_t,
                end_time=end_t
            ))

        return events

    def scrape_protests(self) -> List[ProtestEvent]:
        """전체적으로 모든 함수 실행해 결과적으로 메모리에 시위 목록 반환"""
        board_nos = self._collect_board_no()    
        attachments = self._collect_attachments(board_nos)  

        # 내일자 파일명으로 필터링하기
        target_date = (datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(days=1)).date()
        prefix = target_date.strftime("%y%m%d")

        attachments = [(no, fn, ref) for (no, fn, ref) in attachments if str(fn).startswith(prefix)]

        all_events: List[ProtestEvent] = []
        for attach_no, filename, referer in attachments:    
            pdf_bytes = self._download_pdf(attach_no, referer)   
            if not pdf_bytes:
                continue
            all_events.extend(self._extract_events(pdf_bytes, filename))    

        logger.info("추출된 내일의 시위 정보 %d건", len(all_events))
        return all_events

    def run(self) -> List[ProtestEvent]:
        """메인 실행 함수"""
        try:
            events = self.scrape_protests()

            for e in events[:10]: 
                logger.info("시위 일정: %s", e)
                print(f"시위 일정: {e}") 
                
            logger.info("시위 정보 수집 완료: %d건", len(events))
            return events

        except Exception:
            logger.exception("시위 정보 수집 실패")
            return []


def main():
    """시작 함수"""
    print("시위 정보 수집을 시작합니다...")
    scraper = ProtestScraper()
    events = scraper.run()
    print(f"총 {len(events)}건의 시위 정보가 수집되었습니다.")
    return events


if __name__ == "__main__":
    main()