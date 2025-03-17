# app/scrapers/spider.py
import os
import scrapy
import csv
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
from typing import Optional, List

class KnowledgeSpider(scrapy.Spider):
    name = "knowledgeSpider"

    def __init__(self, start_url: Optional[str] = None, webhook_url: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not start_url:
            raise ValueError("Error: A start_url is required to run the spider.")

        self.start_urls = [start_url]  
        self.webhook_url = webhook_url if webhook_url else None
        self.extracted_urls = set()

        # Get the absolute path for the extracted links file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.link_file = os.path.join(current_dir, "extracted_links.csv")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.link_file), exist_ok=True)
        
        # Open CSV file for writing
        self.csv_file = open(self.link_file, "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Links"])

    @staticmethod
    def extract_company_name(url: str) -> str:
        return urlparse(url).netloc

    def parse(self, response):
        for link in LinkExtractor().extract_links(response):
            if self.extract_company_name(link.url) == urlparse(self.start_urls[0]).netloc and link.url not in self.extracted_urls:
                self.extracted_urls.add(link.url)
                self.csv_writer.writerow([link.url])
                yield scrapy.Request(link.url, callback=self.parse)

    def close(self, reason):
        self.csv_file.close()
        self.logger.info(f"Spider closed: {reason}")