from crewai_tools import SeleniumScrapingTool, tool


class WebTools:
    @tool("Scrape the provided URL using Selenium")
    @staticmethod
    def scrape_url(website_url: str):
        """Scrape the provided URL using Selenium."""
        scraping_tool = SeleniumScrapingTool(website_url=website_url)
        result = scraping_tool._run(website_url=website_url)
        return result
