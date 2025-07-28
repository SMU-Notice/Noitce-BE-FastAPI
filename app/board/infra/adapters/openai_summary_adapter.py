# infra/adapters/outbound/openai_summary_adapter.py
from openai import AsyncOpenAI
import os
import json
from dotenv import load_dotenv
from app.board.application.ports.summary_port import SummaryPort
import logging
from app.board.domain.event_location_time import EventLocationTime
from typing import Optional
from datetime import datetime
from app.board.domain.post import Post
from app.board.domain.post_picture import PostPicture


# 로거 설정
logger = logging.getLogger(__name__)

class OpenAISummaryAdapter(SummaryPort):
    """OpenAI API를 사용한 비동기 요약 서비스 어댑터"""
    
    def __init__(self, api_key: str = None, organization: str = None, project: str = None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORGANIZATION")
        self.project = project or os.getenv("OPENAI_PROJECT")
        
        # AsyncOpenAI 클라이언트 사용
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            project=self.project
        )
    
    async def summarize_post_content(self, post: Post) -> Post:
        """1차 필터: 게시물 본문을 간결하게 요약합니다."""
        content_str = post.original_content
        
        # 0자면 내용이 없다고 반환
        if not content_str or len(content_str.strip()) == 0:
            logger.warning("게시물 본문 요약할 내용이 없습니다.")
            post.content_summary = "내용 없음"
            return post
        
        # 50자 이하면 그대로 반환 (요약할 필요 없음)
        if len(content_str.strip()) <= 50:
            logger.info("내용이 짧아서 그대로 반환합니다. 길이: %d자", len(content_str.strip()))
            post.content_summary = content_str.strip()
            return post
        
        try:
            messages = [
                {
                    "role": "user", 
                    "content": f"""다음 학교 공지사항을 정리해주세요.

                    **정리 방식:**
                    - 핵심 정보만 추출하여 항목별로 정리
                    - 각 항목은 줄바꿈으로 구분
                    - 있는 정보만 정리 (없는 정보는 생략)

                    **항목 예시:**
                    일정: (있을 때만)
                    장소: (있을 때만)
                    신청방법: (있을 때만)
                    주의사항: (있을 때만)

                    공지 내용: {content_str}"""
                }
            ]
                    
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            post.content_summary = summary
            
            return post
            
        except Exception as e:
            error_msg = f"OpenAI API 요약 생성 중 오류 발생: {e}"
            logger.error(error_msg)
            
            post.content_summary = "실패"
            return post
    
    
    async def extract_structured_location_info(self, summary_content: str) -> Optional[EventLocationTime]:
        """2차 필터: 요약된 내용에서 날짜, 시간, 장소 정보를 추출하여 EventLocationTime 객체로 반환"""
        if not summary_content or len(summary_content.strip()) < 10:
            return None
        
        try:
            messages = [
                {
                "role": "system",
                "content": "너는 공지문에서 날짜, 시각, 장소 정보를 구조화해서 JSON으로 추출하는 정보 정리 전문가야. 요청 형식과 요구사항을 엄격히 따라야 해."
            },
            {
                "role": "user",
                "content": f"""다음 요약된 공지 내용에서 아래 항목들을 찾아 JSON 형식으로 추출해줘.
            각 항목이 없으면 "없음"이라고 표기해줘.

            - 장소 (상명대학교 내부의 구체적인 물리적 장소만 해당. 예: 상명대학교 제1공학관, A동 101호, 중앙도서관, 학생회관 등)
            - 시작 날짜 (YYYY-MM-DD 형식)
            - 종료 날짜 (YYYY-MM-DD 형식)  
            - 시작 시각 (HH:MM 또는 HH시MM분 형식)
            - 종료 시각 (HH:MM 또는 HH시MM분 형식)

            **장소 판별 기준:**
            - 포함: 상명대학교 캠퍼스 내 건물명, 강의실, 실습실, 도서관, 학생회관, 체육관 등
            - 제외: 
            * 온라인, 인터넷, 홈페이지, 웹사이트, 시스템, URL 등 비물리적 공간
            * 상명대학교가 아닌 외부 장소 (다른 대학교, 회사, 기관, 카페, 식당 등)
            * 일반적인 지역명 (서울, 강남, 종로 등)

            다음과 같은 JSON 형식으로 응답해줘:

            {{
            "장소": "예: 상명대학교 제1공학관 또는 없음",
            "시작_날짜": "YYYY-MM-DD 또는 없음",
            "종료_날짜": "YYYY-MM-DD 또는 없음", 
            "시작_시각": "HH:MM 또는 없음",
            "종료_시각": "HH:MM 또는 없음"
            }}

            공지 요약 내용:
            {summary_content}"""
            }
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {e}")
            return None
        
        # JSON 파싱 시도
        try:
            # ```json 등의 마크다운 제거
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            structured_info = json.loads(result_text)
            
            # location이 없거나 "없음"이면 None 반환
            location = structured_info.get("장소", "")
            if not location or location == "없음" or location.strip() == "":
                return None
            
            # EventLocationTime 객체 생성 및 반환
            try:
                # 날짜 파싱
                start_date = None
                end_date = None
                start_time = None
                end_time = None
                
                # 시작 날짜 파싱
                start_date_str = structured_info.get("시작_날짜", "")
                if start_date_str and start_date_str != "없음":
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                
                # 종료 날짜 파싱
                end_date_str = structured_info.get("종료_날짜", "")
                if end_date_str and end_date_str != "없음":
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                
                # 시작 시각 파싱
                start_time_str = structured_info.get("시작_시각", "")
                if start_time_str and start_time_str != "없음":
                    if ":" in start_time_str:
                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    elif "시" in start_time_str and "분" in start_time_str:
                        time_str = start_time_str.replace("시", ":").replace("분", "")
                        start_time = datetime.strptime(time_str, "%H:%M").time()
                
                # 종료 시각 파싱
                end_time_str = structured_info.get("종료_시각", "")
                if end_time_str and end_time_str != "없음":
                    if ":" in end_time_str:
                        end_time = datetime.strptime(end_time_str, "%H:%M").time()
                    elif "시" in end_time_str and "분" in end_time_str:
                        time_str = end_time_str.replace("시", ":").replace("분", "")
                        end_time = datetime.strptime(time_str, "%H:%M").time()
                
                return EventLocationTime(
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time
                )
                
            except ValueError as e:
                logger.error(f"날짜/시간 파싱 오류: {e}")
                # 파싱 오류가 있어도 location이 있으면 객체 생성
                return EventLocationTime(location=location)
                
            
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 실패. 원본 응답: {result_text}")
            return None
            
        except Exception as e:
            logger.error(f"구조화된 정보 추출 중 오류 발생: {e}")
            return None
        
    async def summarize_ocr_content(self, post_picture: PostPicture) -> PostPicture:
        """OCR로 추출된 텍스트를 요약하여 PostPicture 객체를 업데이트합니다."""
        
        # OCR 텍스트 추출 (picture_summary에 OCR 원본이 들어있다고 가정)
        ocr_text = post_picture.original_ocr_text
        
        # 내용이 없으면 그대로 반환
        if not ocr_text or len(ocr_text.strip()) == 0:
            logger.warning("OCR 텍스트가 없습니다.")
            post_picture.picture_summary = "내용 없음"
            return post_picture
        
        # 50자 이하면 그대로 반환
        if len(ocr_text.strip()) <= 30:
            logger.info("OCR 텍스트가 짧아서 그대로 반환합니다. 길이: %d자", len(ocr_text.strip()))
            return post_picture
        
        try:
            messages = [
                {
                    "role": "user", 
                    "content": f"""다음 이미지에서 추출된 텍스트를 정리해주세요.
    각 섹션은 '---'로 구분되어 있습니다.

                    **정리 방식:**
                    - 핵심 정보만 추출하여 항목별로 정리
                    - 각 항목은 줄바꿈으로 구분
                    - 있는 정보만 정리 (없는 정보는 생략)
                    - 섹션별 내용을 통합하여 정리

                    **항목 예시:**
                    일정: (있을 때만)
                    장소: (있을 때만)
                    신청방법: (있을 때만)
                    주의사항: (있을 때만)
                    기타 정보: (있을 때만)

                    추출된 텍스트: {ocr_text}"""
                }
            ]
                    
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            post_picture.picture_summary = summary
            
            return post_picture
            
        except Exception as e:
            error_msg = f"OCR 텍스트 요약 중 오류 발생: {e}"
            logger.error(error_msg)
            
            # 오류 발생 시 "실패"로 마킹 - 이후 저장하지 않음
            post_picture.picture_summary = "실패"
            
            return post_picture