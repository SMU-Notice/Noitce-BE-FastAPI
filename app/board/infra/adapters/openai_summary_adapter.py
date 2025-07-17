# infra/adapters/outbound/openai_summary_adapter.py
from openai import AsyncOpenAI
import os
import json
from dotenv import load_dotenv
from app.board.application.ports.summary_port import SummaryPort
import logging
from app.board.application.dto.scraped_content import ScrapedContent
from app.board.domain.event_location_time import EventLocationTime
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SummarizedScrapedContent(BaseModel):
    """요약된 스크래핑 컨텐츠를 위한 Pydantic 모델"""
    original_content: str = Field(description="원본 스크래핑 내용")
    summary: str = Field(description="요약된 내용")
    is_successful: bool = Field(default=True, description="요약 성공 여부")
    error_message: Optional[str] = Field(default=None, description="요약 실패 시 오류 메시지")
    
    @classmethod
    def success(cls, original_content: str, summary: str) -> 'SummarizedScrapedContent':
        """성공적인 요약 결과 생성"""
        return cls(
            original_content=original_content,
            summary=summary,
            is_successful=True
        )
    
    @classmethod
    def failure(cls, original_content: str, error_message: str) -> 'SummarizedScrapedContent':
        """실패한 요약 결과 생성"""
        return cls(
            original_content=original_content,
            summary=f"요약 생성에 실패했습니다. 원본 텍스트: {original_content[:100]}...",
            is_successful=False,
            error_message=error_message
        )



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
    
    async def summarize_post_content(self, content: ScrapedContent) -> SummarizedScrapedContent:
        """1차 필터: 게시물 본문을 간결하게 요약합니다."""
        content_str = str(content.text)  # ScrapedContent를 문자열로 변환
        
        if not content_str or len(content_str.strip()) < 10:
            logger.warning("요약할 내용이 너무 짧습니다. 내용: %s", content_str)
            return SummarizedScrapedContent.failure(
                original_content=content_str,
                error_message="내용이 너무 짧아 요약할 수 없습니다."
            )
        
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "당신은 공지사항을 간결하고 핵심적으로 요약하는 전문가입니다."
                },
                {
                    "role": "user", 
                    "content": f"""다음 공지 내용을 핵심만 간결하게 요약해줘.
                    중요 일정, 수강신청 방법, 시스템 사용 방법, 유의사항을 항목 위주로 정리하고,
                    날짜와 시각이 포함된 내용은 최대한 명확하게 '날짜 + 시각'이 구조적으로 드러나도록 정리해줘.
                    문장은 짧고 단순하게 유지해줘.

                    공지 내용:
                    {content_str}"""
                }
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return SummarizedScrapedContent.success(
                original_content=content_str,
                summary=summary
            )
            
        except Exception as e:
            error_msg = f"OpenAI API 요약 생성 중 오류 발생: {e}"
            logger.error(error_msg)
            
            return SummarizedScrapedContent.failure(
                original_content=content_str,
                error_message=error_msg
            )
    
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

            - 장소 (구체적인 물리적 장소만, 예: 상명대학교 제1공학관 / A동 101호 등. 홈페이지나 URL은 제외)
            - 시작 날짜 (YYYY-MM-DD 형식)
            - 종료 날짜 (YYYY-MM-DD 형식)  
            - 시작 시각 (HH:MM 또는 HH시MM분 형식)
            - 종료 시각 (HH:MM 또는 HH시MM분 형식)

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
                print(f"날짜/시간 파싱 오류: {e}")
                # 파싱 오류가 있어도 location이 있으면 객체 생성
                return EventLocationTime(location=location)
                
            
        except json.JSONDecodeError:
            print(f"JSON 파싱 실패. 원본 응답: {result_text}")
            return None
            
        except Exception as e:
            print(f"구조화된 정보 추출 중 오류 발생: {e}")
            return None