import logging
from app.board.application.ports.summary_port import SummaryPort
from app.board.infra.adapters.openai_summary_adapter import OpenAISummaryAdapter
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.event_location_time import EventLocationTime
from typing import Optional, List, Tuple

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
        extracted_locations = []

        logger.info("위치 정보 추출을 시작합니다.")

        try:
            # 3-1. 본문에서 위치 정보 추출
            content_locations = await self._extract_location_from_content(summary_processed_dto)
            if content_locations:
                for location in content_locations:
                    extracted_locations.append(("content", location))
                logger.info(f"본문에서 {len(content_locations)}개의 위치 정보 추출 성공")
            else:
                logger.debug("본문에서 위치 정보 추출 실패 또는 위치 정보 없음")

            # 3-2. 사진에서 위치 정보 추출
            picture_locations = await self._extract_location_from_picture(summary_processed_dto)
            if picture_locations:
                for location in picture_locations:
                    extracted_locations.append(("picture", location))
                logger.info(f"사진에서 {len(picture_locations)}개의 위치 정보 추출 성공")
            else:
                logger.debug("사진에서 위치 정보 추출 실패 또는 위치 정보 없음")

            # 3-3. 중복 장소 제거 및 최종 위치 리스트 생성
            final_locations = self._process_extracted_locations(extracted_locations)
            
            # DTO에 locations 설정
            summary_processed_dto.locations = final_locations

            if final_locations:
                logger.info(f"총 {len(final_locations)}개의 위치 정보가 추출되었습니다.")
                logger.debug(f"추출된 위치 정보: {[{'location': loc.location, 'original_post_id': loc.original_post_id} for loc in summary_processed_dto.locations]}")
                
            else:
                logger.info("위치 정보 추출 실패 또는 위치 정보 없음")
                
        except Exception as e:
            logger.error(f"위치 정보 추출 중 오류 발생: {e}")

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

    def _process_extracted_locations(self, extracted_locations: List[Tuple[str, EventLocationTime]]) -> List[EventLocationTime]:
        """
        추출된 위치 정보들을 처리하여 최종 위치 리스트 생성
        
        Args:
            extracted_locations: 추출된 위치 정보 리스트 [(source, location), ...]
            
        Returns:
            List[EventLocationTime]: 최종 처리된 위치 정보 리스트
        """
        final_locations = []
        
        if len(extracted_locations) == 1:
            # 하나만 있으면 그대로 추가
            final_locations.append(extracted_locations[0][1])
            logger.info(f"위치 정보 1개 확정: {extracted_locations[0][1].location}")
        
        elif len(extracted_locations) == 2:
            content_loc = extracted_locations[0][1] if extracted_locations[0][0] == "content" else extracted_locations[1][1]
            picture_loc = extracted_locations[0][1] if extracted_locations[0][0] == "picture" else extracted_locations[1][1]
            
            if self._are_same_locations(content_loc, picture_loc):
                # 같은 장소로 판단되면 본문 우선 (더 상세한 정보일 가능성이 높음)
                final_locations.append(content_loc)
                logger.info(f"동일 장소로 판단 - 본문 위치 정보 사용: {content_loc.location}")
            else:
                # 다른 장소면 둘 다 추가
                final_locations.extend([content_loc, picture_loc])
                logger.info(f"서로 다른 장소 - 모두 추가: {content_loc.location}, {picture_loc.location}")
        
        return final_locations

    def _are_same_locations(self, loc1: EventLocationTime, loc2: EventLocationTime) -> bool:
        """
        두 위치 정보가 같은 장소인지 판단하는 메서드
        
        Args:
            loc1: 첫 번째 위치 정보
            loc2: 두 번째 위치 정보
            
        Returns:
            bool: 같은 장소인지 여부
        """
        if not loc1 or not loc2:
            return False
        
        # 간단한 문자열 유사도 비교
        loc1_name = loc1.location.lower().strip()
        loc2_name = loc2.location.lower().strip()
        
        # 완전히 같거나, 하나가 다른 하나를 포함하는 경우
        if loc1_name == loc2_name:
            return True
        
        if loc1_name in loc2_name or loc2_name in loc1_name:
            return True
        
        return False