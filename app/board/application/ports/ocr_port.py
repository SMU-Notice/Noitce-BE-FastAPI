from abc import ABC, abstractmethod

class OCRPort(ABC):
    """OCR 처리를 위한 포트 (인터페이스)"""
    
    @abstractmethod
    def extract_text_from_image_pipeline(self, image_path: str) -> str:
        """
        이미지에서 텍스트를 추출하는 메서드
        
        Args:
            image_url: 텍스트를 추출할 이미지 URL
            
        Returns:
            str: 추출된 텍스트 (실패 시 빈 문자열)
        """
        pass