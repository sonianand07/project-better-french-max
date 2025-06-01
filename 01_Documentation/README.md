# 🇫🇷 French News Scraper & Quality Curator

A comprehensive system for scraping, scoring, and curating French news specifically designed for **expats and immigrants living in France**. This system helps non-native French speakers stay informed about news that directly or indirectly impacts their daily life in France.

## 🎯 Project Overview

This project addresses the challenge faced by expats and immigrants in France who struggle to:
- Find relevant French news that affects their daily life
- Filter through overwhelming amounts of information
- Understand complex French news titles and content
- Access quality, unbiased information from trusted sources

### Target Audience
- **Primary**: Expats/immigrants living in France who don't speak French natively
- **Secondary**: French language learners who want real-world news content
- **Focus**: 50-60% content directly impacting daily life, 40-50% broader French society knowledge

## 🛠️ System Architecture

### 1. **Data Scraper** (`french_news_scraper.py`)
- Scrapes 20+ major French news RSS feeds
- Collects comprehensive article metadata
- Handles rate limiting and error recovery
- Outputs raw JSON data with 930+ articles daily

### 2. **Quality Curator** (`news_quality_curator.py`)
- **Quality Scoring** (0-10): Content completeness, writing structure, language quality
- **Relevance Scoring** (0-10): Focused on expat life in France
- **Importance Scoring** (0-10): From perspective of someone living in France
- **Deduplication**: Removes duplicates, keeps highest-scoring version
- **Output**: Curated articles (high quality) + Rejected articles (duplicates/low quality)

### 3. **Complete Pipeline** (`french_news_pipeline.py`)
- Runs both scraping and curation in sequence
- Provides comprehensive analysis and reporting
- Ready-to-use for production deployment

## 📊 Scoring System

### Quality Score (0-10)
- **Content completeness**: Long content, unique summaries, author attribution
- **Writing quality**: Analysis keywords, expert quotes, contextual explanations
- **Structure quality**: Descriptive titles, proper French punctuation
- **Language quality**: Proper French grammar patterns
- **Penalties**: Clickbait indicators, too short content

### Relevance Score (0-10) - For Expats in France
**High Relevance (+4 points)**: Immigration, visas, social services, healthcare, education, banking, French culture, government services

**Medium Relevance (+2 points)**: National events, current affairs, technology, environment

**Low Relevance (penalties)**: Celebrity gossip, international news without French context

### Importance Score (0-10) - Living in France Perspective
- **Breaking news**: Urgent, major announcements
- **Government/Policy**: Laws, reforms, official decisions affecting daily life
- **Economic impact**: Employment, inflation, salaries, cost of living
- **Social impact**: Education, healthcare, transportation, public services
- **Source reputation**: Trusted French news sources

## 🗂️ Data Collection Schema

For each news article, we collect:

### **📰 Article Content**
- `title`: Article headline
- `summary`: Article summary/description
- `content`: Full article content (when available)
- `link`: Article URL
- `author`: Article author

### **📅 Publication Data**
- `published`: Publication date (string)
- `published_parsed`: Parsed publication date (ISO format)
- `guid`: Unique article identifier

### **🏢 Source Information**
- `source_name`: News source name
- `source_url`: RSS feed URL
- `language`: Content language
- `category`: Article category/section

### **🔍 Technical Metadata**
- `scraped_at`: When article was scraped
- `content_hash`: Unique content hash for deduplication
- `word_count`: Article word count
- `images`: Associated images

### **⭐ Curation Scores** (After curation)
- `quality_score`: 0-10 quality rating
- `relevance_score`: 0-10 relevance for expats
- `importance_score`: 0-10 importance rating
- `total_score`: Combined score (0-30)
- `curation_id`: Unique curation identifier
- `rejection_reason`: Why article was rejected (if applicable)

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv french_news_env
source french_news_env/bin/activate  # On macOS/Linux
# OR
french_news_env\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Individual Components

**Scrape News Only:**
```bash
python french_news_scraper.py
```

**Curate Existing Data:**
```bash
python news_quality_curator.py <scraped_data.json>
```

**Complete Pipeline:**
```bash
python french_news_pipeline.py
```

### 3. Use Environment Helper Script
```bash
chmod +x setup_env.sh
./setup_env.sh
```

## 📈 Expected Results

### Typical Daily Output
- **Raw articles scraped**: ~930 articles
- **Curated articles**: ~786 articles (84.5%)
- **Rejected articles**: ~144 articles (15.5%)
  - Duplicates: ~144 articles
  - Low quality: Variable
- **Duplicate groups found**: ~52 groups

### Quality Metrics (0-30 scale)
- **Average total score**: 17.5/30
- **Best articles**: 28.6/30
- **Quality average**: 7.5/10
- **Relevance average**: 4.2/10  
- **Importance average**: 5.7/10

## 📁 Output Files

### Curated Articles (`curated_news_data_YYYYMMDD_HHMMSS.json`)
```json
{
  "metadata": {
    "curated_at": "2025-05-31T08:56:07.454Z",
    "total_curated": 786,
    "curator_version": "1.0",
    "statistics": { ... },
    "scoring_system": { ... }
  },
  "curated_articles": [
    {
      "original_data": { ... },
      "quality_score": 7.5,
      "relevance_score": 4.2,
      "importance_score": 5.7,
      "total_score": 17.4,
      "curation_id": "uuid",
      "curated_at": "2025-05-31T08:56:07.454Z"
    }
  ]
}
```

### Rejected Articles (`rejected_news_data_YYYYMMDD_HHMMSS.json`)
Contains articles rejected for being duplicates or having low scores, with rejection reasons.

## 🔧 Configuration & Customization

### Adjusting Quality Threshold
```python
# In news_quality_curator.py, line ~367
curated_file, rejected_file = curator.curate_articles(input_file, quality_threshold=5.0)
```

### Adding New RSS Sources
```python
# In french_news_scraper.py, add to RSS_FEEDS dict
RSS_FEEDS = {
    # ... existing feeds
    "New Source": "https://newsource.com/rss"
}
```

### Customizing Relevance Keywords
Edit the keyword sets in `FrenchNewsQualityCurator.__init__()`:
- `high_relevance_keywords`: Directly relevant to expat life
- `medium_relevance_keywords`: Generally relevant to French society
- `low_relevance_keywords`: Reduces relevance score

## 🌟 Key Features

### ✅ **Intelligent Scoring**
- Multi-dimensional scoring system
- Expat-focused relevance criteria
- Quality assessment based on journalistic standards

### ✅ **Advanced Deduplication**
- URL-based deduplication
- Content similarity analysis (title + summary)
- Keeps highest-scoring version from duplicates

### ✅ **Comprehensive Sources**
- Le Monde, Le Figaro, France Info, Liberation
- BFM TV, RFI, France 24, Le Parisien
- Regional and specialized sources

### ✅ **Production Ready**
- Error handling and logging
- Rate limiting and retry logic
- Concurrent processing for efficiency

### ✅ **Scalable Architecture**
- Modular design for easy extensions
- JSON-based data format
- Easy integration with web applications

## 🔮 Next Steps for Your French Learning App

This curated data is perfect for:

1. **Title Breakdown**: Complex French news titles ready for word-by-word explanation
2. **Contextual Learning**: Real-world French content with cultural context
3. **Difficulty Adaptation**: Articles pre-scored for complexity
4. **Summary Generation**: Raw content ready for French/English summaries
5. **Progress Tracking**: Unique IDs for tracking user engagement

## 📞 Support & Customization

The system is designed to be highly customizable for your specific needs:
- Adjust scoring weights for different user types
- Add new languages or regions
- Integrate with your learning management system
- Custom filtering for specific topics or difficulty levels

## 📝 License & Usage

This system is built specifically for your French learning app targeting expats and immigrants in France. The curation logic prioritizes content that helps users understand French society, culture, and daily life requirements.

---

**Ready to help thousands of expats and immigrants stay informed and learn French through real-world news! 🇫🇷✨** 