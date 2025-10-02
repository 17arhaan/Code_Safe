#!/usr/bin/env python3
"""
Advanced Web Scraping Framework
Comprehensive web scraping toolkit with multiple engines and data extraction capabilities.
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import lxml
import html5lib
import json
import csv
import sqlite3
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import time
import random
import hashlib
import re
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import signal
import sys
from datetime import datetime, timedelta
import pickle
import gzip
import os
import ssl
import certifi
from fake_useragent import UserAgent
import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    max_concurrent_requests: int = 10
    request_delay: float = 1.0
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    respect_robots_txt: bool = True
    user_agent_rotation: bool = True
    proxy_rotation: bool = False
    javascript_rendering: bool = False
    headless_browser: bool = True
    output_format: str = 'json'  # json, csv, sqlite, xml
    output_file: str = 'scraped_data'
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    max_pages: int = 1000
    follow_redirects: bool = True
    verify_ssl: bool = True

@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    url: str
    status_code: int
    content: str
    data: Dict[str, Any]
    timestamp: datetime
    processing_time: float
    success: bool
    error: Optional[str] = None

class RateLimiter:
    """Rate limiter to control request frequency."""
    
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        """Acquire permission to make a request."""
        with self.lock:
            now = time.time()
            
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Calculate how long to wait before next request."""
        with self.lock:
            if not self.requests:
                return 0
            
            oldest_request = min(self.requests)
            wait_time = self.time_window - (time.time() - oldest_request)
            return max(0, wait_time)

class ProxyManager:
    """Manages proxy rotation for web scraping."""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_list = proxy_list or []
        self.current_index = 0
        self.lock = threading.Lock()
    
    def get_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation."""
        if not self.proxy_list:
            return None
        
        with self.lock:
            proxy = self.proxy_list[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxy_list)
            return proxy
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the list."""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the list."""
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)

class UserAgentManager:
    """Manages user agent rotation."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.user_agents = []
        self.current_index = 0
        self.lock = threading.Lock()
        self._load_user_agents()
    
    def _load_user_agents(self):
        """Load a variety of user agents."""
        try:
            # Common user agents
            self.user_agents = [
                self.ua.chrome,
                self.ua.firefox,
                self.ua.safari,
                self.ua.opera,
                self.ua.edge
            ]
        except Exception as e:
            logger.warning(f"Failed to load user agents: {e}")
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
    
    def get_user_agent(self) -> str:
        """Get a random user agent."""
        with self.lock:
            if not self.user_agents:
                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            
            user_agent = self.user_agents[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.user_agents)
            return user_agent

class WebScraper:
    """Main web scraping class with multiple engines."""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.rate_limiter = RateLimiter(
            self.config.max_concurrent_requests, 
            self.config.request_delay
        )
        self.proxy_manager = ProxyManager()
        self.ua_manager = UserAgentManager()
        self.session = None
        self.cache = {}
        self.results = []
        self.robots_cache = {}
        
        # Setup session
        self._setup_session()
    
    def _setup_session(self):
        """Setup the requests session with proper configuration."""
        self.session = requests.Session()
        
        # Configure SSL
        if not self.config.verify_ssl:
            self.session.verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Configure headers
        self.session.headers.update({
            'User-Agent': self.ua_manager.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configure timeouts
        self.session.timeout = self.config.request_timeout
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if not self.config.respect_robots_txt:
            return True
        
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            if robots_url in self.robots_cache:
                rp = self.robots_cache[robots_url]
            else:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[robots_url] = rp
            
            return rp.can_fetch('*', url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True
    
    def _get_proxy_config(self) -> Dict[str, str]:
        """Get proxy configuration for requests."""
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            return {
                'http': proxy,
                'https': proxy
            }
        return {}
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Make a single HTTP request with retry logic."""
        for attempt in range(self.config.max_retries + 1):
            try:
                # Rate limiting
                if not self.rate_limiter.acquire():
                    wait_time = self.rate_limiter.wait_time()
                    logger.info(f"Rate limited, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                    continue
                
                # Check robots.txt
                if not self._check_robots_txt(url):
                    logger.warning(f"URL {url} blocked by robots.txt")
                    raise Exception("Blocked by robots.txt")
                
                # Prepare request
                headers = kwargs.get('headers', {})
                if self.config.user_agent_rotation:
                    headers['User-Agent'] = self.ua_manager.get_user_agent()
                
                # Add proxy
                proxies = self._get_proxy_config()
                
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    allow_redirects=self.config.follow_redirects,
                    timeout=self.config.request_timeout,
                    **kwargs
                )
                
                # Check response
                response.raise_for_status()
                return response
                
            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise
    
    def scrape_url(self, url: str, extractors: List[Callable] = None) -> ScrapingResult:
        """Scrape a single URL."""
        start_time = time.time()
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Make request
            response = self._make_request(url)
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            data = {}
            if extractors:
                for extractor in extractors:
                    try:
                        extracted_data = extractor(soup, url)
                        data.update(extracted_data)
                    except Exception as e:
                        logger.warning(f"Extractor failed: {e}")
            
            processing_time = time.time() - start_time
            
            result = ScrapingResult(
                url=url,
                status_code=response.status_code,
                content=response.text,
                data=data,
                timestamp=datetime.now(),
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"Successfully scraped {url} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to scrape {url}: {e}")
            
            return ScrapingResult(
                url=url,
                status_code=0,
                content="",
                data={},
                timestamp=datetime.now(),
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
    
    def scrape_urls(self, urls: List[str], extractors: List[Callable] = None) -> List[ScrapingResult]:
        """Scrape multiple URLs concurrently."""
        logger.info(f"Starting to scrape {len(urls)} URLs")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_requests) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.scrape_url, url, extractors): url 
                for url in urls[:self.config.max_pages]
            }
            
            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
        
        logger.info(f"Completed scraping {len(results)} URLs")
        return results
    
    async def scrape_url_async(self, session: aiohttp.ClientSession, url: str, 
                              extractors: List[Callable] = None) -> ScrapingResult:
        """Asynchronously scrape a single URL."""
        start_time = time.time()
        
        try:
            logger.info(f"Async scraping URL: {url}")
            
            # Check robots.txt
            if not self._check_robots_txt(url):
                raise Exception("Blocked by robots.txt")
            
            # Prepare headers
            headers = {}
            if self.config.user_agent_rotation:
                headers['User-Agent'] = self.ua_manager.get_user_agent()
            
            # Make async request
            async with session.get(url, headers=headers, timeout=self.config.request_timeout) as response:
                content = await response.text()
                
                # Parse content
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract data
                data = {}
                if extractors:
                    for extractor in extractors:
                        try:
                            extracted_data = extractor(soup, url)
                            data.update(extracted_data)
                        except Exception as e:
                            logger.warning(f"Extractor failed: {e}")
                
                processing_time = time.time() - start_time
                
                result = ScrapingResult(
                    url=url,
                    status_code=response.status,
                    content=content,
                    data=data,
                    timestamp=datetime.now(),
                    processing_time=processing_time,
                    success=True
                )
                
                logger.info(f"Successfully async scraped {url} in {processing_time:.2f}s")
                return result
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to async scrape {url}: {e}")
            
            return ScrapingResult(
                url=url,
                status_code=0,
                content="",
                data={},
                timestamp=datetime.now(),
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
    
    async def scrape_urls_async(self, urls: List[str], extractors: List[Callable] = None) -> List[ScrapingResult]:
        """Asynchronously scrape multiple URLs."""
        logger.info(f"Starting async scraping of {len(urls)} URLs")
        
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [
                self.scrape_url_async(session, url, extractors) 
                for url in urls[:self.config.max_pages]
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in results if isinstance(r, ScrapingResult)]
            
            logger.info(f"Completed async scraping {len(valid_results)} URLs")
            return valid_results
    
    def save_results(self, results: List[ScrapingResult] = None, filename: str = None):
        """Save scraping results to file."""
        results = results or self.results
        filename = filename or self.config.output_file
        
        if not results:
            logger.warning("No results to save")
            return
        
        logger.info(f"Saving {len(results)} results to {filename}")
        
        if self.config.output_format == 'json':
            self._save_json(results, filename)
        elif self.config.output_format == 'csv':
            self._save_csv(results, filename)
        elif self.config.output_format == 'sqlite':
            self._save_sqlite(results, filename)
        else:
            self._save_json(results, filename)
    
    def _save_json(self, results: List[ScrapingResult], filename: str):
        """Save results as JSON."""
        data = []
        for result in results:
            data.append({
                'url': result.url,
                'status_code': result.status_code,
                'data': result.data,
                'timestamp': result.timestamp.isoformat(),
                'processing_time': result.processing_time,
                'success': result.success,
                'error': result.error
            })
        
        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, results: List[ScrapingResult], filename: str):
        """Save results as CSV."""
        with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'status_code', 'data', 'timestamp', 'processing_time', 'success', 'error'])
            
            for result in results:
                writer.writerow([
                    result.url,
                    result.status_code,
                    json.dumps(result.data),
                    result.timestamp.isoformat(),
                    result.processing_time,
                    result.success,
                    result.error
                ])
    
    def _save_sqlite(self, results: List[ScrapingResult], filename: str):
        """Save results to SQLite database."""
        conn = sqlite3.connect(f"{filename}.db")
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                status_code INTEGER,
                data TEXT,
                timestamp TEXT,
                processing_time REAL,
                success BOOLEAN,
                error TEXT
            )
        ''')
        
        # Insert data
        for result in results:
            cursor.execute('''
                INSERT INTO scraping_results 
                (url, status_code, data, timestamp, processing_time, success, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.url,
                result.status_code,
                json.dumps(result.data),
                result.timestamp.isoformat(),
                result.processing_time,
                result.success,
                result.error
            ))
        
        conn.commit()
        conn.close()

# Common extractors
def extract_links(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract all links from a page."""
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(url, href)
        links.append({
            'text': link.get_text(strip=True),
            'url': absolute_url,
            'title': link.get('title', '')
        })
    
    return {'links': links}

def extract_text(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract text content from a page."""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return {
        'text': text,
        'word_count': len(text.split()),
        'char_count': len(text)
    }

def extract_images(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract all images from a page."""
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            absolute_url = urljoin(url, src)
            images.append({
                'src': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width'),
                'height': img.get('height')
            })
    
    return {'images': images}

def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract metadata from a page."""
    metadata = {}
    
    # Title
    title = soup.find('title')
    if title:
        metadata['title'] = title.get_text(strip=True)
    
    # Meta tags
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            metadata[name] = content
    
    # Headings
    headings = {}
    for i in range(1, 7):
        heading_tags = soup.find_all(f'h{i}')
        headings[f'h{i}'] = [h.get_text(strip=True) for h in heading_tags]
    metadata['headings'] = headings
    
    return {'metadata': metadata}

def main():
    """Main function to demonstrate the web scraper."""
    logger.info("Starting Web Scraper Framework Demo")
    
    # Configuration
    config = ScrapingConfig(
        max_concurrent_requests=5,
        request_delay=1.0,
        max_pages=10,
        output_format='json',
        output_file='scraping_results'
    )
    
    # Create scraper
    scraper = WebScraper(config)
    
    # Sample URLs to scrape
    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://example.com',
        'https://httpbin.org/robots.txt',
        'https://httpbin.org/user-agent'
    ]
    
    # Define extractors
    extractors = [
        extract_links,
        extract_text,
        extract_images,
        extract_metadata
    ]
    
    # Scrape URLs
    logger.info("Starting synchronous scraping")
    results = scraper.scrape_urls(urls, extractors)
    
    # Save results
    scraper.save_results()
    
    # Print summary
    successful = sum(1 for r in results if r.success)
    logger.info(f"Scraping completed: {successful}/{len(results)} successful")
    
    # Demonstrate async scraping
    logger.info("Starting asynchronous scraping")
    async_results = asyncio.run(scraper.scrape_urls_async(urls, extractors))
    
    logger.info(f"Async scraping completed: {len(async_results)} results")
    
    logger.info("Web Scraper Framework Demo completed!")

if __name__ == "__main__":
    main()
