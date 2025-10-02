import logging
from app.board.application.ports.summary_port import SummaryPort
from app.board.infra.adapters.openai_summary_adapter import OpenAISummaryAdapter
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.event_location_time import EventLocationTime
from typing import Optional, List

logger = logging.getLogger(__name__)

class SummaryService:
    """요약 서비스 - 요약과 Location 정보 추출을 담당"""
    
    def __init__(self, summary_adapter: SummaryPort = None):
        self.summary_adapter = summary_adapter or OpenAISummaryAdapter()
    
    async def create_summary_processed_post(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        SummaryProcessedPostDTO를 받아서 요약 처리를 수행하고 반환합니다.
        
        Args:
            summary_processed_dto: 요약 처리할 SummaryProcessedPostDTO
            
        Returns:
            SummaryProcessedPostDTO: 요약 처리된 DTO
        """
        try:
            logger.info("Post 요약 시작합니다.")
            
            # 1. 본문 요약 처리
            await self._process_post_summary(summary_processed_dto)

            # 2. 사진 요약 처리
            await self._process_picture_summary(summary_processed_dto)

            # 3. Location 정보 추출
            await self._extract_and_process_locations(summary_processed_dto)
            
            # 4. ProcessedPostDTO 반환
            return summary_processed_dto
        
        except Exception as e:
            logger.error("Post 처리 중 예상치 못한 오류 발생: %s", str(e))
            return SummaryProcessedPostDTO(post=summary_processed_dto.post)

    async def _process_post_summary(self, summary_processed_dto: SummaryProcessedPostDTO) -> None:
        """
        본문 요약 처리
        
        Args:
            summary_processed_dto: 처리할 SummaryProcessedPostDTO
        """
        summary_processed_dto.post = await self.summary_adapter.summarize_post_content(summary_processed_dto.post)

        if summary_processed_dto.post.content_summary != "실패":
            content_summary_log = summary_processed_dto.post.content_summary[:10] + ("..." if len(summary_processed_dto.post.content_summary) > 10 else "")
            logger.info(f"Post 본문 요약이 완료되었습니다. content_summary: {content_summary_log}")
        else:
            logger.warning("Post 본문 요약에 실패했습니다: %s", summary_processed_dto.post.title)

    async def _process_picture_summary(self, summary_processed_dto: SummaryProcessedPostDTO) -> None:
        """
        사진 요약 처리
        
        Args:
            summary_processed_dto: 처리할 SummaryProcessedPostDTO
        """
        if not summary_processed_dto.has_post_picture():
            return
            
        logger.info("게시물에 사진이 존재합니다. 사진 요약을 시작합니다.")
        
        summary_processed_dto.post_picture = await self.summary_adapter.summarize_ocr_content(summary_processed_dto.post_picture)
        
        if summary_processed_dto.post_picture and summary_processed_dto.post_picture.picture_summary == "실패":
            logger.warning("사진 요약 실패 - PostPicture를 DTO에서 제거")
            summary_processed_dto.post_picture = None
        elif summary_processed_dto.post_picture:
            logger.info(f"사진 요약 성공: {summary_processed_dto.post_picture.picture_summary[:50]}...")

    async def _extract_and_process_locations(self, summary_processed_dto: SummaryProcessedPostDTO) -> None:
        """
        요약된 내용에서 위치 정보를 추출하고 처리하는 내부 메서드
        
        Args:
            summary_processed_dto: 처리할 SummaryProcessedPostDTO
        """
        all_locations = []

        logger.info("위치 정보 추출을 시작합니다.")

        try:
            # 3-1. 본문에서 위치 정보 추출
            content_locations = await self._extract_location_from_content(summary_processed_dto)
            if content_locations:
                all_locations.extend(content_locations)
                logger.info(f"본문에서 {len(content_locations)}개의 위치 정보 추출 성공")
            else:
                logger.debug("본문에서 위치 정보 추출 실패 또는 위치 정보 없음")

            # 3-2. 사진에서 위치 정보 추출
            picture_locations = await self._extract_location_from_picture(summary_processed_dto)
            if picture_locations:
                all_locations.extend(picture_locations)
                logger.info(f"사진에서 {len(picture_locations)}개의 위치 정보 추출 성공")
            else:
                logger.debug("사진에서 위치 정보 추출 실패 또는 위치 정보 없음")

            # 3-3. 중복 장소 제거 및 최종 위치 리스트 생성
            final_locations = self._remove_duplicate_locations(all_locations)
            
            # DTO에 locations 설정
            summary_processed_dto.locations = final_locations

            if final_locations:
                logger.info(f"총 {len(final_locations)}개의 위치 정보가 추출되었습니다.")
                logger.debug(f"추출된 위치 정보: {[{'location': loc.location, 'original_post_id': loc.original_post_id} for loc in summary_processed_dto.locations]}")
                
            else:
                logger.info("위치 정보 추출 실패 또는 위치 정보 없음")
                
        except Exception as e:
            logger.error(f"위치 정보 추출 중 오류 발생: {e}")

    def _remove_duplicate_locations(self, locations: List[EventLocationTime]) -> List[EventLocationTime]:
        """
        위치 리스트에서 중복된 위치 제거 (위치명 + 날짜 정보 기준)
        
        Args:
            locations: 위치 정보 리스트
            
        Returns:
            List[EventLocationTime]: 중복이 제거된 위치 정보 리스트
        """
        if not locations:
            return []
        
        final_locations = []
        seen_locations = set()
        
        for location in locations:
            if not location or not location.location:
                continue
                
            # 위치명과 날짜 정보를 조합한 고유 키 생성
            location_key = self._create_location_key(location)
            
            if location_key not in seen_locations:
                final_locations.append(location)
                seen_locations.add(location_key)
                logger.debug(f"위치 추가: {location.location}")
            else:
                logger.debug(f"중복 위치 제거: {location.location}")
        
        logger.info(f"중복 제거 완료: {len(locations)}개 → {len(final_locations)}개")
        return final_locations

    def _create_location_key(self, location: EventLocationTime) -> str:
        """
        위치 객체에서 중복 체크용 고유 키 생성
        
        Args:
            location: 위치 정보 객체
            
        Returns:
            str: 중복 체크용 고유 키
        """
        location_name = location.location.lower().strip() if location.location else ""
        
        # 날짜 정보 처리 (None 체크 포함)
        start_date = ""
        end_date = ""
        
        if hasattr(location, 'start_date') and location.start_date is not None:
            start_date = str(location.start_date)
        
        if hasattr(location, 'end_date') and location.end_date is not None:
            end_date = str(location.end_date)
        
        # 모든 날짜 정보가 없는 경우는 위치명만으로 키 생성
        if not start_date and not end_date:
            return location_name
        
        # 키 조합: "위치명|시작날짜|종료날짜"
        key = f"{location_name}|{start_date}|{end_date}"
        return key

    async def _extract_location_from_content(self, summary_processed_dto: SummaryProcessedPostDTO) -> Optional[List[EventLocationTime]]:
        """
        본문 요약에서 위치 정보 추출
        
        Args:
            summary_processed_dto: 처리할 SummaryProcessedPostDTO
            
        Returns:
            Optional[List[EventLocationTime]]: 추출된 위치 정보 리스트 또는 None
        """
        logger.info(f"본문에서 위치 정보 추출 시작: {summary_processed_dto.post.title}")
        
        if not (summary_processed_dto.post.content_summary and 
                summary_processed_dto.post.content_summary != "실패"):
            logger.debug("본문 요약이 없거나 실패 상태입니다.")
            return None
        
        logger.debug(f"본문 요약 내용: {summary_processed_dto.post.content_summary[:100]}...")
        
        content_location_dicts = await self.summary_adapter.extract_structured_location_info(
            summary_processed_dto.post.content_summary
        )
        
        if content_location_dicts:
            logger.debug(f"본문에서 {len(content_location_dicts)}개의 위치 정보 딕셔너리 추출됨")
            content_locations = self._convert_dicts_to_location_entities(
                content_location_dicts, 
                summary_processed_dto.post.original_post_id
            )
            logger.debug
            logger.debug(f"본문에서 최종 {len(content_locations)}개의 위치 엔티티 생성 완료")
            return content_locations
        else:
            logger.debug("본문에서 위치 정보를 찾지 못했습니다.")
            return None

    async def _extract_location_from_picture(self, summary_processed_dto: SummaryProcessedPostDTO) -> Optional[List[EventLocationTime]]:
        """
        사진 요약에서 위치 정보 추출
        
        Args:
            summary_processed_dto: 처리할 SummaryProcessedPostDTO
            
        Returns:
            Optional[List[EventLocationTime]]: 추출된 위치 정보 리스트 또는 None
        """
        logger.info(f"사진에서 위치 정보 추출 시작: {summary_processed_dto.post.title}")
        
        if not (summary_processed_dto.post_picture and 
                summary_processed_dto.post_picture.picture_summary and 
                summary_processed_dto.post_picture.picture_summary != "실패"):
            logger.debug("사진 요약이 없거나 실패 상태입니다.")
            return None
        
        logger.debug(f"사진 요약 내용: {summary_processed_dto.post_picture.picture_summary[:100]}...")
        
        picture_location_dicts = await self.summary_adapter.extract_structured_location_info(
            summary_processed_dto.post_picture.picture_summary
        )
        
        if picture_location_dicts:
            logger.debug(f"사진에서 {len(picture_location_dicts)}개의 위치 정보 딕셔너리 추출됨")
            picture_locations = self._convert_dicts_to_location_entities(
                picture_location_dicts, 
                summary_processed_dto.post.original_post_id
            )
            logger.debug(f"사진에서 최종 {len(picture_locations)}개의 위치 엔티티 생성 완료")
            return picture_locations
        else:
            logger.debug("사진에서 위치 정보를 찾지 못했습니다.")
            return None

    def _convert_dicts_to_location_entities(self, location_dicts: List[dict], original_post_id: int) -> List[EventLocationTime]:
        """
        위치 정보 딕셔너리 리스트를 EventLocationTime 엔티티 리스트로 변환
        
        Args:
            location_dicts: 위치 정보 딕셔너리 리스트
            original_post_id: 원본 게시물 ID
            
        Returns:
            List[EventLocationTime]: 변환된 위치 엔티티 리스트
        """
        logger.debug(f"딕셔너리를 도메인 객체로 변환 시작: {len(location_dicts)}개 항목, original_post_id={original_post_id}")
        
        location_entities = []
        
        for i, location_dict in enumerate(location_dicts):
            try:
                # original_post_id 추가
                location_dict_copy = location_dict.copy()  # 원본 딕셔너리 보존
                location_dict_copy["original_post_id"] = original_post_id
                
                # 딕셔너리를 도메인 객체로 변환
                location_entity = EventLocationTime.from_dict(location_dict_copy)
                location_entities.append(location_entity)
                
                logger.debug(f"위치 엔티티 {i+1} 생성 성공: {location_entity.location} (original_post_id: {location_entity.original_post_id})")
                
            except Exception as e:
                logger.error(f"위치 엔티티 {i+1} 생성 실패: {location_dict} - {e}")
                continue
        
        logger.info(f"총 {len(location_entities)}개의 위치 엔티티 변환 완료")
        return location_entities
