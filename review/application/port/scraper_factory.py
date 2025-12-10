from review.application.port.scraper_port import ScraperPort
from review.infrastructure.external.elevenSt_scraper import ElevenStScraperAdapter
from review.infrastructure.external.lotteon_scraper import LotteonScraper
from review.domain.entity.review import ReviewPlatform

def get_scraper_adapter(platform: str) -> ScraperPort:
    # ⭐️ Enum인 경우 .value로 문자열 추출
    if isinstance(platform, ReviewPlatform):
        platform_str = platform.value
    else:
        platform_str = str(platform)

    # 소문자로 비교
    platform_lower = platform_str.lower()

    if platform_lower == "elevenst":
        return ElevenStScraperAdapter()
    elif platform_lower == "lotteon":
        return LotteonScraper()
    else:
        raise ValueError(f"지원하지 않는 플랫폼: {platform}")