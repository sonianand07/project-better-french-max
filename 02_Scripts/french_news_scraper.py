#!/usr/bin/env python3
"""
French News RSS Scraper with Real-Time 24-Hour Filtering
Efficiently collects only fresh French news articles from the last 24 hours.
"""

import feedparser
import requests
import json
import csv
import time
import hashlib
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import logging
import os
from dateutil import parser as date_parser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../05_Logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Calculate 24-hour cutoff time at startup
TWENTY_FOUR_HOURS_AGO = datetime.now(timezone.utc) - timedelta(hours=24)

@dataclass
class NewsArticle:
    """Data structure for a news article"""
    # Basic article info
    title: str
    summary: str
    link: str
    published: str
    published_parsed: Optional[str]
    
    # Source information
    source_name: str
    source_url: str
    feed_url: str
    
    # Content details
    author: Optional[str]
    category: Optional[str]
    tags: List[str]
    content: Optional[str]
    
    # Media
    image_url: Optional[str]
    image_title: Optional[str]
    
    # Technical details
    guid: Optional[str]
    language: Optional[str]
    
    # Scraping metadata
    scraped_at: str
    article_hash: str

class FrenchNewsRSScraper:
    """French News RSS Feed Scraper"""
    
    def __init__(self):
        # Major French News RSS Feeds
        self.feed_urls = {
            # Major French Newspapers
            "Le Monde": "http://www.lemonde.fr/rss/une.xml",
            "Le Figaro": "http://www.lefigaro.fr/rss/figaro_actualites.xml",
            "Liberation": "https://www.liberation.fr/rss/",
            "Le Parisien": "https://feeds.leparisien.fr/leparisien/rss",
            "L'Express": "https://www.lexpress.fr/arc/outboundfeeds/rss/alaune.xml",
            "Le Point": "http://www.lepoint.fr/rss.xml",
            "L'Obs": "http://tempsreel.nouvelobs.com/rss.xml",
            "La Croix": "https://www.la-croix.com/RSS",
            
            # TV/Radio News
            "BFM TV": "https://www.bfmtv.com/rss/news-24-7/",
            "France Info": "https://www.francetvinfo.fr/titres.rss",
            "France Inter": "https://www.franceinter.fr/rss",
            "Europe 1": "https://www.europe1.fr/rss.xml",
            "France 24": "https://www.france24.com/fr/rss",
            "RFI": "https://rfi.fr/fr/rss",
            
            # Regional/Specialized
            "Ouest France": "https://www.ouest-france.fr/rss/une",
            "20 Minutes": "https://partner-feeds.20min.ch/rss/20minutes",
            "AFP": "https://www.afp.com/fr/actus/afp_actualite/792,31,9,7,33/feed",
            
            # Alternative/Independent
            "Mediapart": "https://www.mediapart.fr/articles/feed",
            "Brief.me": "https://brief.me/rss",
            
            # Categories from Le Monde
            "Le Monde Politique": "https://www.lemonde.fr/politique/rss_full.xml",
            "Le Monde International": "https://www.lemonde.fr/international/rss_full.xml",
            "Le Monde Economie": "https://www.lemonde.fr/economie/rss_full.xml",
            "Le Monde Culture": "https://www.lemonde.fr/culture/rss_full.xml",
            "Le Monde Sport": "https://www.lemonde.fr/sport/rss_full.xml",
            "Le Monde Sciences": "https://www.lemonde.fr/sciences/rss_full.xml",
        }
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Storage
        self.articles = []
        self.failed_feeds = []
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_image_from_entry(self, entry) -> tuple:
        """Extract image URL and title from RSS entry"""
        image_url = None
        image_title = None
        
        # Check various image fields
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'image' in media.get('type', ''):
                    image_url = media.get('url')
                    break
        
        elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get('url') if entry.media_thumbnail else None
        
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'image' in enclosure.get('type', ''):
                    image_url = enclosure.get('href')
                    break
        
        # Try to extract from description/summary
        if not image_url and hasattr(entry, 'summary'):
            img_match = re.search(r'<img[^>]*src=["\']([^"\']*)["\']', entry.summary)
            if img_match:
                image_url = img_match.group(1)
        
        return image_url, image_title
    
    def parse_feed_entry(self, entry, source_name: str, feed_url: str) -> NewsArticle:
        """Parse a single RSS feed entry into NewsArticle"""
        
        # Extract basic info
        title = self.clean_text(entry.get('title', ''))
        summary = self.clean_text(entry.get('summary', '') or entry.get('description', ''))
        link = entry.get('link', '')
        
        # Handle publication date
        published = entry.get('published', '')
        published_parsed = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_parsed = datetime(*entry.published_parsed[:6]).isoformat()
            except:
                published_parsed = None
        
        # Extract author
        author = None
        if hasattr(entry, 'author'):
            author = self.clean_text(entry.author)
        elif hasattr(entry, 'authors') and entry.authors:
            author = self.clean_text(entry.authors[0].get('name', ''))
        
        # Extract category/tags
        category = None
        tags = []
        if hasattr(entry, 'category'):
            category = self.clean_text(entry.category)
        
        if hasattr(entry, 'tags') and entry.tags:
            tags = [self.clean_text(tag.get('term', '')) for tag in entry.tags]
        
        # Extract content
        content = None
        if hasattr(entry, 'content') and entry.content:
            content = self.clean_text(entry.content[0].get('value', ''))
        elif hasattr(entry, 'summary_detail'):
            content = self.clean_text(entry.summary_detail.get('value', ''))
        
        # Extract image
        image_url, image_title = self.extract_image_from_entry(entry)
        
        # Generate unique hash
        hash_content = f"{title}_{link}_{published}_{source_name}"
        article_hash = hashlib.md5(hash_content.encode()).hexdigest()
        
        # Current timestamp
        scraped_at = datetime.now(timezone.utc).isoformat()
        
        return NewsArticle(
            title=title,
            summary=summary,
            link=link,
            published=published,
            published_parsed=published_parsed,
            source_name=source_name,
            source_url=urlparse(link).netloc if link else "",
            feed_url=feed_url,
            author=author,
            category=category,
            tags=tags,
            content=content,
            image_url=image_url,
            image_title=image_title,
            guid=entry.get('id', entry.get('guid', '')),
            language=entry.get('language', 'fr'),
            scraped_at=scraped_at,
            article_hash=article_hash
        )
    
    def scrape_single_feed(self, source_name: str, feed_url: str) -> List[NewsArticle]:
        """Scrape a single RSS feed and filter for last 24 hours only"""
        articles = []
        total_found = 0
        
        try:
            logger.info(f"Scraping {source_name}: {feed_url}")
            
            # Get the feed with timeout
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {source_name}: {feed.bozo_exception}")
            
            # Process each entry with real-time date filtering
            for entry in feed.entries:
                total_found += 1
                try:
                    article = self.parse_feed_entry(entry, source_name, feed_url)
                    
                    # Real-time date filtering - only keep articles from last 24 hours
                    if article.published_parsed:
                        try:
                            article_date = date_parser.parse(article.published_parsed)
                            # Ensure timezone awareness
                            if article_date.tzinfo is None:
                                article_date = article_date.replace(tzinfo=timezone.utc)
                            
                            # Only add if article is within last 24 hours
                            if article_date >= TWENTY_FOUR_HOURS_AGO:
                                articles.append(article)
                                logger.debug(f"✅ Added article from {article_date.strftime('%Y-%m-%d %H:%M')}: {article.title[:50]}...")
                            else:
                                logger.debug(f"⏰ Skipped old article from {article_date.strftime('%Y-%m-%d %H:%M')}: {article.title[:50]}...")
                                
                        except Exception as date_error:
                            logger.warning(f"Date parsing error for {source_name}, including article anyway: {date_error}")
                            articles.append(article)  # Include if date parsing fails
                    else:
                        logger.debug(f"📅 No date found, including article: {article.title[:50]}...")
                        articles.append(article)  # Include if no date
                        
                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ {source_name}: {len(articles)} fresh articles (filtered from {total_found} total)")
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {source_name}: {e}")
            self.failed_feeds.append({"source": source_name, "url": feed_url, "error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error scraping {source_name}: {e}")
            self.failed_feeds.append({"source": source_name, "url": feed_url, "error": str(e)})
        
        return articles
    
    def scrape_all_feeds(self, max_workers: int = 10) -> None:
        """Scrape all RSS feeds concurrently"""
        logger.info(f"Starting to scrape {len(self.feed_urls)} RSS feeds")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(self.scrape_single_feed, source, url): source 
                for source, url in self.feed_urls.items()
            }
            
            # Process completed tasks
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    articles = future.result()
                    self.articles.extend(articles)
                except Exception as e:
                    logger.error(f"Thread failed for {source}: {e}")
        
        logger.info(f"Scraping completed. Total articles: {len(self.articles)}")
        logger.info(f"Failed feeds: {len(self.failed_feeds)}")
    
    def save_to_json(self, filename: str = None) -> str:
        """Save articles to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../04_Data_Output/Raw/french_news_data_{timestamp}.json"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert dataclasses to dictionaries
        data = {
            "metadata": {
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "total_articles": len(self.articles),
                "sources_scraped": len(self.feed_urls),
                "failed_feeds": self.failed_feeds,
                "scraper_version": "1.0"
            },
            "articles": [asdict(article) for article in self.articles]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to {filename}")
        return filename
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save articles to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../04_Data_Output/Raw/french_news_data_{timestamp}.csv"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.articles:
            logger.warning("No articles to save")
            return filename
        
        # Get all possible field names
        fieldnames = list(asdict(self.articles[0]).keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in self.articles:
                # Convert tags list to string
                article_dict = asdict(article)
                article_dict['tags'] = ', '.join(article_dict['tags']) if article_dict['tags'] else ''
                writer.writerow(article_dict)
        
        logger.info(f"CSV data saved to {filename}")
        return filename
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of scraped data"""
        if not self.articles:
            return {"error": "No articles scraped"}
        
        # Count by source
        source_counts = {}
        for article in self.articles:
            source_counts[article.source_name] = source_counts.get(article.source_name, 0) + 1
        
        # Get date range
        dates = [article.published_parsed for article in self.articles if article.published_parsed]
        
        stats = {
            "total_articles": len(self.articles),
            "unique_sources": len(source_counts),
            "articles_by_source": source_counts,
            "failed_feeds": len(self.failed_feeds),
            "date_range": {
                "earliest": min(dates) if dates else None,
                "latest": max(dates) if dates else None
            },
            "articles_with_images": len([a for a in self.articles if a.image_url]),
            "articles_with_authors": len([a for a in self.articles if a.author]),
            "articles_with_content": len([a for a in self.articles if a.content])
        }
        
        return stats

def main():
    """Main function to run the scraper with 24-hour filtering"""
    print("🇫🇷 French News RSS Scraper with 24-Hour Filtering")
    print("=" * 60)
    
    # Show filtering information
    cutoff_time = TWENTY_FOUR_HOURS_AGO.strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"⏰ Filtering for articles newer than: {cutoff_time}")
    print(f"🎯 Expected result: ~150-300 fresh articles (not 900+)")
    
    # Create scraper instance
    scraper = FrenchNewsRSScraper()
    
    # Show feeds to be scraped
    print(f"\n📰 Will scrape {len(scraper.feed_urls)} French news sources:")
    for source in scraper.feed_urls.keys():
        print(f"  • {source}")
    print()
    
    # Start scraping with real-time filtering
    print("🔄 Starting real-time filtered scraping...")
    start_time = time.time()
    scraper.scrape_all_feeds(max_workers=8)
    end_time = time.time()
    
    # Show results
    print("\n" + "=" * 60)
    print("🎯 Scraping Results (24-Hour Filtered):")
    print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
    
    stats = scraper.get_summary_stats()
    if "error" not in stats:
        print(f"📄 Fresh articles collected: {stats['total_articles']} (last 24h only)")
        print(f"🏢 Sources successful: {stats['unique_sources']}")
        print(f"❌ Failed feeds: {stats['failed_feeds']}")
        print(f"🖼️  Articles with images: {stats['articles_with_images']}")
        print(f"✍️  Articles with authors: {stats['articles_with_authors']}")
        print(f"📝 Articles with full content: {stats['articles_with_content']}")
        
        # Quality check
        if stats['total_articles'] > 500:
            print(f"⚠️  WARNING: {stats['total_articles']} articles seems high for 24h")
            print("🔍 Check if date filtering is working correctly")
        else:
            print(f"✅ Good! {stats['total_articles']} articles is realistic for 24h")
        
        print(f"\n📊 Fresh articles by source:")
        for source, count in sorted(stats['articles_by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {source}: {count}")
    
    # Save data
    print(f"\n💾 Saving filtered data...")
    json_file = scraper.save_to_json()
    csv_file = scraper.save_to_csv()
    
    print(f"✅ JSON saved: {json_file}")
    print(f"✅ CSV saved: {csv_file}")
    
    print(f"\n🎉 Efficient scraping completed! Only fresh articles collected.")
    return json_file

if __name__ == "__main__":
    main() 