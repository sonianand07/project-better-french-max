#!/usr/bin/env python3
"""
French News Pipeline with Auto-Cleanup
Scrapes French news, curates it, and automatically deletes raw data after processing.
Perfect for hourly/daily automated runs.
"""

import subprocess
import sys
import os
import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Change to the scripts directory if running from elsewhere
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
os.chdir(script_dir)

def run_scraper():
    """Run the French news scraper"""
    print("🔄 Step 1: Scraping fresh French news (last 24 hours)...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'french_news_scraper.py'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Extract filename from output
        lines = result.stdout.split('\n')
        json_file = None
        for line in lines:
            if 'JSON saved:' in line:
                json_file = line.split('JSON saved: ')[1].strip()
                break
        
        return json_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraping failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def filter_last_24_hours(input_file):
    """Filter articles to only include those from last 24 hours"""
    print("🕐 Filtering articles to last 24 hours only...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Calculate 24 hours ago
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Filter articles
        original_count = len(data['articles'])
        filtered_articles = []
        
        for article in data['articles']:
            if article.get('published_parsed'):
                try:
                    # Parse the publication date
                    pub_date = datetime.fromisoformat(article['published_parsed'].replace('Z', '+00:00'))
                    if pub_date >= cutoff_time:
                        filtered_articles.append(article)
                except:
                    # If date parsing fails, include the article anyway
                    filtered_articles.append(article)
            else:
                # If no date, include it anyway
                filtered_articles.append(article)
        
        # Update data
        data['articles'] = filtered_articles
        data['metadata']['total_articles'] = len(filtered_articles)
        data['metadata']['filtered_to_24h'] = True
        data['metadata']['articles_removed'] = original_count - len(filtered_articles)
        
        # Save filtered data
        filtered_file = input_file.replace('.json', '_24h.json')
        with open(filtered_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Filtered: {original_count} → {len(filtered_articles)} articles (last 24h)")
        return filtered_file
        
    except Exception as e:
        print(f"❌ Filtering failed: {e}")
        return input_file  # Return original if filtering fails

def run_curator(input_file):
    """Run the news quality curator"""
    print("\n🔄 Step 2: Curating and deduplicating news...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'news_quality_curator.py', input_file], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Extract filenames from output
        lines = result.stdout.split('\n')
        curated_file = None
        rejected_file = None
        
        for line in lines:
            if 'Curated file:' in line:
                curated_file = line.split('Curated file: ')[1].strip()
            elif 'Rejected file:' in line:
                rejected_file = line.split('Rejected file: ')[1].strip()
        
        return curated_file, rejected_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Curation failed: {e}")
        print(f"Error output: {e.stderr}")
        return None, None

def cleanup_raw_data(processed_files):
    """Delete raw data files after successful processing"""
    print("\n🗑️ Step 3: Cleaning up processed raw data...")
    print("=" * 50)
    
    try:
        cleaned_files = []
        for file_path in processed_files:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / (1024*1024)  # MB
                os.remove(file_path)
                cleaned_files.append(f"{os.path.basename(file_path)} ({file_size:.1f}MB)")
                print(f"✅ Deleted: {os.path.basename(file_path)} ({file_size:.1f}MB)")
        
        print(f"🧹 Cleaned up {len(cleaned_files)} raw data files")
        return cleaned_files
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return []

def generate_summary(curated_file, rejected_file, cleaned_files):
    """Generate a summary report"""
    print("\n📊 Final Summary Report")
    print("=" * 50)
    
    try:
        # Load curated data
        with open(curated_file, 'r', encoding='utf-8') as f:
            curated_data = json.load(f)
        
        # Load rejected data  
        with open(rejected_file, 'r', encoding='utf-8') as f:
            rejected_data = json.load(f)
        
        total_curated = curated_data['metadata']['total_curated']
        total_rejected = rejected_data['metadata']['total_rejected']
        total_processed = total_curated + total_rejected
        
        stats = curated_data['metadata']['statistics']
        
        print(f"📈 Processing Results:")
        print(f"  Total articles processed: {total_processed}")
        print(f"  ✅ Curated (high quality): {total_curated} ({total_curated/total_processed*100:.1f}%)")
        print(f"  ❌ Rejected (duplicates/low quality): {total_rejected} ({total_rejected/total_processed*100:.1f}%)")
        
        print(f"\n🎯 Quality Scores (0-30 scale):")
        print(f"  Average total score: {stats['total']['avg']:.1f}/30")
        print(f"  Best article score: {stats['total']['max']:.1f}/30")
        print(f"  Quality average: {stats['quality']['avg']:.1f}/10")
        print(f"  Relevance average: {stats['relevance']['avg']:.1f}/10")
        print(f"  Importance average: {stats['importance']['avg']:.1f}/10")
        
        # Top articles
        articles = curated_data['curated_articles']
        top_articles = sorted(articles, key=lambda x: x['total_score'], reverse=True)[:3]
        
        print(f"\n🏆 Top 3 Articles for French Learners:")
        for i, article in enumerate(top_articles, 1):
            title = article['original_data']['title']
            score = article['total_score']
            source = article['original_data']['source_name']
            print(f"  {i}. [{score:.1f}/30] {title[:60]}... ({source})")
        
        print(f"\n📁 Output Files:")
        print(f"  📄 Curated articles: {curated_file}")
        print(f"  🗑️  Rejected articles: {rejected_file}")
        
        print(f"\n🧹 Raw Data Cleanup:")
        for cleaned_file in cleaned_files:
            print(f"  ✅ Deleted: {cleaned_file}")
        
        print(f"\n✨ Ready for your French learning app!")
        print(f"   Fresh content curated specifically for expats/immigrants in France")
        print(f"   Raw data cleaned up - no reprocessing needed!")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def check_for_existing_data():
    """Check if there's any existing raw data that needs processing"""
    raw_dir = Path("../04_Data_Output/Raw")
    raw_files = list(raw_dir.glob("*.json"))
    
    if raw_files:
        print(f"⚠️  Found {len(raw_files)} existing raw data files:")
        for file in raw_files:
            print(f"   • {file.name}")
        
        response = input("\nDo you want to process existing data first? (y/n): ").lower()
        if response == 'y':
            return str(raw_files[0])  # Process the first one
    
    return None

def main():
    """Main pipeline execution with auto-cleanup"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("🇫🇷 French News Auto-Cleanup Pipeline")
    print("=" * 60)
    print(f"🕐 Started at: {timestamp}")
    print("📍 Target: Fresh content for expats/immigrants in France")
    print("🎯 Goal: Scrape (24h filtered) → Curate → Clean up raw data")
    print("⚡ Efficiency: Only fresh articles processed from start!")
    print(f"📂 Working directory: {os.getcwd()}")
    print()
    
    # Keep track of ALL raw files for cleanup
    raw_files_to_cleanup = []
    
    # Check for existing raw data
    existing_raw = check_for_existing_data()
    
    if existing_raw:
        print("🔄 Processing existing raw data first...")
        input_file = existing_raw
        raw_files_to_cleanup.append(input_file)
    else:
        # Step 1: Scrape fresh news (now with built-in 24h filtering)
        json_file = run_scraper()
        if not json_file:
            print("❌ Pipeline failed at scraping step")
            return
        
        # Add original scraped files to cleanup list
        raw_files_to_cleanup.append(json_file)  # JSON file
        csv_file = json_file.replace('.json', '.csv')
        if os.path.exists(csv_file):
            raw_files_to_cleanup.append(csv_file)  # CSV file
        
        # No need for additional filtering - scraper already did it!
        input_file = json_file
    
    # Step 2: Curate news
    curated_file, rejected_file = run_curator(input_file)
    if not curated_file:
        print("❌ Pipeline failed at curation step")
        return
    
    # Step 3: Clean up ALL raw data
    cleaned_files = cleanup_raw_data(raw_files_to_cleanup)
    
    # Step 4: Generate summary
    generate_summary(curated_file, rejected_file, cleaned_files)
    
    end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🎉 Efficient auto-cleanup pipeline completed at {end_timestamp}")
    print("🔄 Ready for next hourly/daily run!")

if __name__ == "__main__":
    main() 