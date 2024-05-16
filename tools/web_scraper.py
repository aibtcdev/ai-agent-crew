from crewai_tools import SeleniumScrapingTool, tool


class WebTools:
    @staticmethod
    @tool
    def scrape_reddit_url(website_url: str):
        """Scrape the provided Reddit URL using Selenium."""
        scraping_tool = SeleniumScrapingTool(website_url=website_url, class_name="main")
        return scraping_tool._run()

    @staticmethod
    @tool
    def scrape_x_or_twitter_url(website_url: str):
        """Scrape the provided X (Twitter) URL using Selenium."""
        scraping_tool = SeleniumScrapingTool(
            website_url=website_url, class_name="css-175oi2r"
        )
        return scraping_tool._run()

    @staticmethod
    @tool
    def scrape_generic_url(website_url: str):
        """Scrape the provided URL using Selenium if it does not match any other tool."""
        scraping_tool = SeleniumScrapingTool(website_url=website_url)
        return scraping_tool._run()
