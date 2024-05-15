from crewai.tools import SeleniumScrapingTool, tool


class WebTools:
    @tool("Scrape the provided URL using Selenium")
    @staticmethod
    def scrape_url(url):
        return SeleniumScrapingTool(url=url)
