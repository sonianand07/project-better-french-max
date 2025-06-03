#!/usr/bin/env python3
"""
Better French Max - Live Website Updater
Handles real-time website data updates and live content delivery
Integrates with existing proven website frontend
"""

import os
import sys
import json
import shutil
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from automation import AUTOMATION_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

class LiveWebsiteUpdater:
    """
    Handles live updates to the website with curated and AI-enhanced articles
    Builds on the proven website architecture
    """
    
    def __init__(self):
        self.website_config = AUTOMATION_CONFIG['website']
        
        # Paths
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'live')
        self.website_dir = os.path.join(os.path.dirname(__file__), '..', 'website')
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        
        # Current state
        self.current_articles = []
        self.last_update = None
        self.update_queue = []
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize website if needed
        self._initialize_website()
        
        logger.info("🌐 Live Website Updater initialized")
        logger.info(f"📁 Website directory: {self.website_dir}")
        logger.info(f"📊 Max articles displayed: {self.website_config['max_articles_displayed']}")
    
    def _initialize_website(self):
        """Initialize the website with the proven frontend if not exists"""
        if not os.path.exists(self.website_dir):
            logger.info("🚧 Initializing website from proven frontend...")
            
            # Copy from proven website
            proven_website = AUTOMATION_CONFIG['integration']['original_website_path']
            if os.path.exists(proven_website):
                shutil.copytree(proven_website, self.website_dir)
                logger.info("✅ Website initialized from proven frontend")
            else:
                # Create basic website structure if original not found
                os.makedirs(self.website_dir, exist_ok=True)
                self._create_basic_website()
                logger.info("✅ Basic website structure created")
    
    def _create_basic_website(self):
        """Create basic website structure if proven frontend not available"""
        # Create a minimal index.html
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Better French Max - Automated</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .article { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
        .title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .source { color: #666; font-size: 0.9em; }
        .score { background: #e8f5e8; padding: 3px 8px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🇫🇷 Better French Max - Automated System</h1>
    <div id="articles-container">
        <p>Loading articles...</p>
    </div>
    <script>
        async function loadArticles() {
            try {
                const response = await fetch('current_articles.json');
                const data = await response.json();
                displayArticles(data.articles || []);
            } catch (error) {
                document.getElementById('articles-container').innerHTML = 
                    '<p>No articles available yet. System starting up...</p>';
            }
        }
        
        function displayArticles(articles) {
            const container = document.getElementById('articles-container');
            if (!articles.length) {
                container.innerHTML = '<p>No articles available.</p>';
                return;
            }
            
            container.innerHTML = articles.map(article => `
                <div class="article">
                    <div class="title">${article.title}</div>
                    <div class="source">${article.source_name} | Score: 
                        <span class="score">${article.total_score?.toFixed(1) || 'N/A'}/30</span>
                    </div>
                    <div style="margin-top: 10px;">${article.summary}</div>
                </div>
            `).join('');
        }
        
        // Load articles on page load
        loadArticles();
        
        // Auto-refresh every 5 minutes
        setInterval(loadArticles, 5 * 60 * 1000);
    </script>
</body>
</html>"""
        
        with open(os.path.join(self.website_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _prepare_article_for_website(self, scored_article) -> Dict[str, Any]:
        """Prepare a scored article for website display"""
        if hasattr(scored_article, '__dict__'):
            article_data = scored_article.__dict__
            original = article_data.get('original_data', {})
        else:
            article_data = scored_article
            original = article_data.get('original_data', article_data)
        
        return {
            'title': original.get('title', ''),
            'summary': original.get('summary', ''),
            'link': original.get('link', ''),
            'source_name': original.get('source_name', ''),
            'published': original.get('published', ''),
            'author': original.get('author', ''),
            'image_url': original.get('image_url', ''),
            'quality_score': article_data.get('quality_score', 0),
            'relevance_score': article_data.get('relevance_score', 0),
            'importance_score': article_data.get('importance_score', 0),
            'total_score': article_data.get('total_score', 0),
            'breaking_news': original.get('breaking_news', False),
            'urgency_score': original.get('urgency_score', 0),
            'fast_tracked': article_data.get('fast_tracked', False),
            'curated_at': article_data.get('curated_at', ''),
            'curation_id': article_data.get('curation_id', '')
        }
    
    def _backup_current_data(self):
        """Backup current website data"""
        current_file = os.path.join(self.website_dir, 'current_articles.json')
        if os.path.exists(current_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.json")
            shutil.copy2(current_file, backup_file)
            logger.debug(f"📦 Backed up current data to {backup_file}")
    
    def _save_website_data(self, articles: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """Save article data for website consumption"""
        data = {
            'metadata': {
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'total_articles': len(articles),
                'automation_system': 'Better French Max Automated System',
                'website_version': '1.0',
                **metadata
            },
            'articles': articles
        }
        
        # Save to website directory
        website_file = os.path.join(self.website_dir, 'current_articles.json')
        with open(website_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Also save to data directory for monitoring
        data_file = os.path.join(self.data_dir, 'website_data.json')
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.last_update = datetime.now(timezone.utc)
        logger.info(f"💾 Website data updated: {len(articles)} articles available")
    
    def add_breaking_news(self, breaking_articles: List[Any]):
        """Add breaking news articles with high priority"""
        logger.info("🚨 Adding breaking news to website...")
        
        # Backup current data
        self._backup_current_data()
        
        # Prepare breaking news articles
        breaking_data = []
        for article in breaking_articles:
            article_data = self._prepare_article_for_website(article)
            article_data['breaking_news'] = True
            article_data['added_at'] = datetime.now(timezone.utc).isoformat()
            breaking_data.append(article_data)
        
        # Load existing articles
        try:
            current_file = os.path.join(self.website_dir, 'current_articles.json')
            if os.path.exists(current_file):
                with open(current_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                existing_articles = existing_data.get('articles', [])
            else:
                existing_articles = []
        except:
            existing_articles = []
        
        # Merge breaking news at the top
        all_articles = breaking_data + existing_articles
        
        # Limit total articles
        max_articles = self.website_config['max_articles_displayed']
        all_articles = all_articles[:max_articles]
        
        # Save updated data
        metadata = {
            'breaking_news_added': len(breaking_data),
            'update_type': 'breaking_news'
        }
        self._save_website_data(all_articles, metadata)
        
        logger.info(f"🚨 Added {len(breaking_data)} breaking news articles to website")
    
    def update_with_curated_articles(self, curated_articles: List[Any]):
        """Update website with curated articles (regular update)"""
        logger.info(f"🔄 Updating website with {len(curated_articles)} curated articles...")
        
        # Backup current data
        self._backup_current_data()
        
        # Prepare articles for website
        website_articles = []
        for article in curated_articles:
            article_data = self._prepare_article_for_website(article)
            article_data['added_at'] = datetime.now(timezone.utc).isoformat()
            website_articles.append(article_data)
        
        # Sort by total score (highest first)
        website_articles.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Limit articles
        max_articles = self.website_config['max_articles_displayed']
        website_articles = website_articles[:max_articles]
        
        # Save data
        metadata = {
            'curated_articles_count': len(curated_articles),
            'update_type': 'curated_articles',
            'average_score': sum(a.get('total_score', 0) for a in website_articles) / len(website_articles) if website_articles else 0
        }
        self._save_website_data(website_articles, metadata)
        
        self.current_articles = website_articles
        logger.info(f"✅ Website updated with {len(website_articles)} curated articles")
    
    def update_with_ai_enhanced_articles(self, ai_articles: List[Dict[str, Any]]):
        """Update website with AI-enhanced articles (highest quality)"""
        logger.info(f"✨ Updating website with {len(ai_articles)} AI-enhanced articles...")
        
        # Backup current data
        self._backup_current_data()
        
        # Prepare AI-enhanced articles for website
        website_articles = []
        for article in ai_articles:
            # Convert contextual_title_explanations from list to dict for website
            explanations_list = article.get('contextual_title_explanations', [])
            explanations_dict = {}
            
            if isinstance(explanations_list, list):
                # Convert list to dictionary format expected by website
                for explanation in explanations_list:
                    if isinstance(explanation, dict) and 'original_word' in explanation:
                        word = explanation['original_word']
                        explanations_dict[word] = {
                            'display_format': explanation.get('display_format', ''),
                            'explanation': explanation.get('explanation', ''),
                            'cultural_note': explanation.get('cultural_note', '')
                        }
            
            # AI articles have different structure
            article_data = {
                'title': article.get('simplified_french_title', article.get('original_article_title', '')),
                'english_title': article.get('simplified_english_title', ''),
                'simplified_french_title': article.get('simplified_french_title', article.get('original_article_title', '')),
                'simplified_english_title': article.get('simplified_english_title', ''),
                'summary': article.get('french_summary', ''),
                'english_summary': article.get('english_summary', ''),
                'french_summary': article.get('french_summary', ''),
                'original_article_title': article.get('original_article_title', ''),
                'original_article_link': article.get('original_article_link', ''),
                'link': article.get('original_article_link', ''),
                'source_name': article.get('source_name', 'Unknown'),
                'published': article.get('original_article_published_date', ''),
                'published_date': article.get('original_article_published_date', ''),
                'explanations': explanations_dict,
                'contextual_title_explanations': explanations_dict,
                'key_vocabulary': article.get('key_vocabulary', []),
                'cultural_context': article.get('cultural_context', {}),
                'quality_scores': article.get('quality_scores', {}),
                'curation_metadata': article.get('curation_metadata', {}),
                'ai_enhanced': True,
                'added_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract scores from quality_scores if available
            quality_scores = article.get('quality_scores', {})
            article_data['quality_score'] = quality_scores.get('quality_score', 0)
            article_data['relevance_score'] = quality_scores.get('relevance_score', 0)
            article_data['importance_score'] = quality_scores.get('importance_score', 0)
            article_data['total_score'] = quality_scores.get('total_score', 0)
            
            website_articles.append(article_data)
        
        # Sort by total score
        website_articles.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Limit articles
        max_articles = self.website_config['max_articles_displayed']
        website_articles = website_articles[:max_articles]
        
        # Save data
        metadata = {
            'ai_enhanced_count': len(ai_articles),
            'update_type': 'ai_enhanced',
            'average_score': sum(a.get('total_score', 0) for a in website_articles) / len(website_articles) if website_articles else 0
        }
        self._save_website_data(website_articles, metadata)
        
        self.current_articles = website_articles
        logger.info(f"✨ Website updated with {len(website_articles)} AI-enhanced articles")
    
    def needs_update(self) -> bool:
        """Check if website needs updating"""
        if not self.last_update:
            return True
        
        # Check if last update was more than the configured interval ago
        update_interval = self.website_config['website_update_interval']
        time_since_update = datetime.now(timezone.utc) - self.last_update
        
        return time_since_update > timedelta(minutes=update_interval)
    
    def perform_incremental_update(self):
        """Perform incremental update if new content is available"""
        try:
            # Check for pending updates in queue
            if self.update_queue:
                logger.info("🔄 Processing pending website updates...")
                
                for update in self.update_queue:
                    if update['type'] == 'breaking_news':
                        self.add_breaking_news(update['articles'])
                    elif update['type'] == 'curated':
                        self.update_with_curated_articles(update['articles'])
                    elif update['type'] == 'ai_enhanced':
                        self.update_with_ai_enhanced_articles(update['articles'])
                
                self.update_queue.clear()
                logger.info("✅ Incremental update completed")
            
        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}")
    
    def load_from_manual_system(self):
        """Load data from manual system fallback"""
        logger.info("🔄 Loading data from manual system fallback...")
        
        try:
            # Look for latest processed data from manual system
            manual_data_path = AUTOMATION_CONFIG['integration']['original_data_path']
            processed_dir = os.path.join(manual_data_path, 'Processed_AI')
            
            if os.path.exists(processed_dir):
                # Find latest file
                files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
                if files:
                    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(processed_dir, x)))
                    manual_file = os.path.join(processed_dir, latest_file)
                    
                    with open(manual_file, 'r', encoding='utf-8') as f:
                        manual_data = json.load(f)
                    
                    # Convert manual system data to website format
                    articles = manual_data.get('processed_articles', [])
                    self.update_with_ai_enhanced_articles(articles)
                    
                    logger.info(f"✅ Loaded {len(articles)} articles from manual system: {latest_file}")
                    return True
            
            logger.warning("⚠️ No manual system data found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to load from manual system: {e}")
            return False
    
    def get_website_status(self) -> Dict[str, Any]:
        """Get current website status for monitoring"""
        try:
            website_file = os.path.join(self.website_dir, 'current_articles.json')
            if os.path.exists(website_file):
                with open(website_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get('metadata', {})
                articles = data.get('articles', [])
                
                return {
                    'status': 'active',
                    'last_update': metadata.get('updated_at'),
                    'total_articles': len(articles),
                    'breaking_news_count': len([a for a in articles if a.get('breaking_news', False)]),
                    'ai_enhanced_count': len([a for a in articles if a.get('ai_enhanced', False)]),
                    'average_score': metadata.get('average_score', 0),
                    'update_type': metadata.get('update_type', 'unknown'),
                    'website_url': "http://localhost:8003"  # Use web server URL instead of file://
                }
            else:
                return {
                    'status': 'no_data',
                    'last_update': None,
                    'total_articles': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Test function for development
def test_website_updater():
    """Test the website updater functionality"""
    print("🧪 Testing Website Updater...")
    
    updater = LiveWebsiteUpdater()
    
    # Test article data structure
    test_article = {
        'original_data': {
            'title': 'Test Article for Website',
            'summary': 'This is a test article summary.',
            'source_name': 'Test Source',
            'link': 'https://example.com',
            'published': '2024-01-01T10:00:00Z'
        },
        'quality_score': 8.0,
        'relevance_score': 7.5,
        'importance_score': 6.0,
        'total_score': 21.5,
        'curation_id': 'test-123',
        'curated_at': '2024-01-01T10:00:00Z'
    }
    
    # Test curated articles update
    updater.update_with_curated_articles([test_article])
    
    # Check status
    status = updater.get_website_status()
    print(f"📊 Website Status: {status['status']}")
    print(f"📄 Total Articles: {status['total_articles']}")
    print(f"🔗 Website URL: {status.get('website_url', 'N/A')}")
    
    print("✅ Website Updater test completed")

if __name__ == "__main__":
    test_website_updater() 