# infra/adapters/outbound/openai_summary_adapter.py
from openai import AsyncOpenAI
import os
import json
from dotenv import load_dotenv
from app.board.application.ports.summary_port import SummaryPort
import logging
from typing import Optional, List
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
        """
        1차 필터: 게시물 본문을 간결하게 요약합니다.

        Parameters:
        - post: 요약할 Post 객체

        Returns:
        - Post: 요약된 Post 객체 (content_summary 필드 업데이트)
        """
        content_str = post.original_content
        
        # 0자면 내용이 없다고 반환
        if not content_str or len(content_str.strip()) == 0:
            logger.warning("게시물 본문 요약할 내용이 없습니다.")
            post.content_summary = "내용 없음"
            return post
        
        # 50자 이하면 그대로 반환 (요약할 필요 없음)
        if len(content_str.strip()) <= 30:
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
                    기타: (있을 때만)

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
        
    async def summarize_ocr_content(self, post_picture: PostPicture) -> PostPicture:
        """
        OCR로 추출된 텍스트를 요약하여 PostPicture 객체를 업데이트합니다.
        
        Parameters:
        - post_picture: 요약할 PostPicture 객체 (original_ocr_text 필드에 OCR 텍스트가 있어야 함)

        Returns:
        - PostPicture: 요약된 PostPicture 객체 (picture_summary 필드 업데이트)
        """
        
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
    
    

    async def extract_structured_location_info(self, summary_content: str) -> Optional[List[dict]]:
        """2차 필터: 요약된 내용에서 날짜, 장소 정보를 추출하여 딕셔너리 리스트로 반환"""
        if not summary_content or not summary_content.strip():
            return None
        
        # 상명대학교 건물 목록 (알파벳 제외)
        SANGMYUNG_BUILDINGS = {
            "사범대학관", "미술관", "가정관", "생활예술관", "학군단", "체육관",
            "제1공학관", "학생회관", "제2교수회관", "대학본부", "제2공학관",
            "학술정보관", "월해관", "자하관", "제1교수회관", "미래백년관",
            "중앙교수회관", "경영경제대학관", "문화예술관"
        }
        
        # 사전 검증: 상명대 건물명이 포함되어 있는지 확인
        if not self._contains_sangmyung_building(summary_content, SANGMYUNG_BUILDINGS):
            logger.info(f"상명대 건물명이 포함되지 않아 GPT 요청을 건너뜁니다: {summary_content[:50]}...")
            return None
        
        try:
            messages = [
                {
                "role": "system",
                "content": "너는 공지문에서 날짜, 장소 정보를 구조화해서 JSON 배열로 추출하는 정보 정리 전문가야. 장소는 반드시 주어진 건물 목록의 정확한 건물명만 추출해야 하고, 다른 부가 정보는 절대 포함하지 마."
            },
            {
                "role": "user",
                "content": f"""다음 요약된 공지 내용에서 아래 항목들을 찾아 JSON 배열 형식으로 추출해줘.

            **장소 추출 규칙 (매우 중요):**
            - 아래 건물 목록에 정확히 일치하는 건물명만 추출
            - 건물명에 추가 정보를 붙이지 마 (예: "학생회관 3층" → "학생회관")
            - 호실, 층수, 방향 등은 절대 포함하지 마
            - 여러 건물이 언급되면 각각을 별도 이벤트로 분리

            **상명대학교 건물 목록 (이 이름 그대로만 사용):**
            사범대학관, 미술관, 가정관, 생활예술관, 학군단, 체육관, 제1공학관, 학생회관, 제2교수회관, 대학본부, 제2공학관, 학술정보관, 월해관, 자하관, 제1교수회관, 미래백년관, 중앙교수회관, 경영경제대학관, 문화예술관

            **추출할 정보:**
            - 장소: 위 건물 목록의 정확한 건물명만 (예: "학생회관", "제1공학관")
            - 시작 날짜: YYYY-MM-DD 형식
            - 종료 날짜: YYYY-MM-DD 형식

            **절대 추출하지 말 것:**
            - 위 목록에 없는 모든 장소
            - 건물명 + 부가정보 (예: "학생회관 3층", "도서관 열람실")
            - 온라인, 인터넷, 웹사이트 등 비물리적 공간
            - 외부 장소 (카페, 식당, 다른 대학 등)
            - 일반적인 지역명 (서울, 강남 등)
            - "A동", "B동" 같은 알파벳 건물 코드

            **잘못된 예시:**
            - "학생회관 3층" → 잘못됨
            - "도서관 2층 열람실" → 잘못됨  
            - "미술관 전시실" → 잘못됨

            **올바른 예시:**
            - "학생회관" → 올바름
            - "학술정보관" → 올바름
            - "미술관" → 올바름

            JSON 배열 형식:
            [
                {{
                    "장소": "정확한 건물명만 또는 없음",
                    "시작_날짜": "YYYY-MM-DD 또는 없음",
                    "종료_날짜": "YYYY-MM-DD 또는 없음"
                }}
            ]

            **예시 처리:**
            입력: "12월 15일 학생회관 3층에서 행사가 있습니다"
            출력: [{{"장소": "학생회관", "시작_날짜": "2024-12-15"}}]

            입력: "도서관 2층과 미술관에서 전시회"
            출력: [{{"장소": "학술정보관"}}, {{"장소": "미술관"}}]

            공지 요약 내용:
            {summary_content}"""
            }
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
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
            
            structured_info_list = json.loads(result_text)
            
            # 단일 딕셔너리가 반환된 경우 리스트로 변환
            if isinstance(structured_info_list, dict):
                structured_info_list = [structured_info_list]
            
            # 각 이벤트를 검증하고 유효한 것들만 필터링
            valid_events = []
            for event in structured_info_list:
                location = event.get("장소", "")
                if location and location != "없음" and location.strip() != "":
                    # 건물명 정확성 재검증
                    clean_location = location.strip()
                    
                    # 건물 목록에 정확히 일치하는지 확인
                    if clean_location in SANGMYUNG_BUILDINGS:
                        valid_events.append({
                            "location": clean_location,
                            "start_date": event.get("시작_날짜", ""),
                            "end_date": event.get("종료_날짜", "")
                        })
                        logger.debug(f"유효한 건물명 확인: {clean_location}")
                    else:
                        # 건물명이 목록에 없으면 부분 매칭 시도
                        matched_building = self._find_building_match(clean_location, SANGMYUNG_BUILDINGS)
                        if matched_building:
                            valid_events.append({
                                "location": matched_building,
                                "start_date": event.get("시작_날짜", ""),
                                "end_date": event.get("종료_날짜", "")
                            })
                            logger.info(f"건물명 매칭: '{clean_location}' → '{matched_building}'")
                        else:
                            logger.warning(f"유효하지 않은 건물명 무시: '{clean_location}'")
            
            # 유효한 이벤트가 없으면 None 반환
            if not valid_events:
                logger.info("장소 정보가 있는 이벤트가 없어서 None을 반환합니다.")
                return None
            
            logger.info(f"{len(valid_events)}개의 이벤트를 추출했습니다.")
            return valid_events
                
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 실패. 원본 응답: {result_text}")
            return None
            
        except Exception as e:
            logger.error(f"구조화된 정보 추출 중 오류 발생: {e}")
        return None

    def _contains_sangmyung_building(self, text: str, building_set: set) -> bool:
        """
        텍스트에 상명대학교 건물명이 포함되어 있는지 확인 (정확한 명칭만)
        
        Args:
            text: 검사할 텍스트
            building_set: 상명대학교 건물명 세트
        
        Returns:
            bool: 정확한 건물명이 포함되어 있으면 True
        """
        # 정확한 건물명만 매칭
        for building in building_set:
            if building in text:
                return True
        
        return False

    def _find_building_match(self, location_text: str, building_set: set) -> Optional[str]:
        """
        건물명 부분 매칭을 통해 정확한 건물명 찾기 (정확한 명칭만)
        예: "학생회관 3층" → "학생회관"
        """
        location_text = location_text.strip()
        
        # 1. 정확히 일치하는 경우
        if location_text in building_set:
            return location_text
        
        # 2. 건물명이 포함된 경우 찾기 (정확한 건물명만)
        for building in building_set:
            if building in location_text:
                return building
        
        return None