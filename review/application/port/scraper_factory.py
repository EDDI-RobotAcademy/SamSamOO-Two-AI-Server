from review.application.port.scraper_port import ScraperPort
from review.infrastructure.external.elevenSt_scraper import ElevenStScraperAdapter
from review.infrastructure.external.gmarket_scraper import GmarketScraper

def get_scraper_adapter(platform: str) -> ScraperPort:
    if platform.lower() == "elevenst":
        return ElevenStScraperAdapter()
    elif platform.lower() == "gmarket":
        return GmarketScraper()
    else:
        raise ValueError(f"지원하지 않는 플랫폼: {platform}")