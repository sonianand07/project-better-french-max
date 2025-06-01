#!/usr/bin/env python3
"""
French News Quality Curator & Deduplication System
Scores articles on Quality, Relevance, and Importance for French learners/expats in France
"""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScoredArticle:
    """Article with quality scores"""
    # Original article data
    original_data: Dict[str, Any]
    
    # Scoring
    quality_score: float
    relevance_score: float
    importance_score: float
    total_score: float
    
    # Curation metadata
    curation_id: str
    curated_at: str
    rejection_reason: str = ""

class FrenchNewsQualityCurator:
    """
    Curates French news for expats/immigrants living in France
    Focuses on content that helps them understand French society, culture, and daily life
    """
    
    def __init__(self):
        self.curated_articles = []
        self.rejected_articles = []
        
        # Keywords for relevance scoring - focused on expat/immigrant needs in France
        self.high_relevance_keywords = {
            # Immigration & Legal
            'immigration', 'visa', 'carte de séjour', 'naturalisation', 'préfecture', 
            'titre de séjour', 'étranger', 'expatrié', 'résidence', 'citoyenneté',
            
            # Daily Life & Services
            'sécurité sociale', 'caf', 'pôle emploi', 'impôts', 'logement', 'santé',
            'transport', 'sncf', 'ratp', 'école', 'université', 'formation',
            'banque', 'assurance', 'mutuelle', 'médecin', 'hôpital',
            
            # French Culture & Society
            'culture française', 'tradition', 'laïcité', 'république', 'marianne',
            'gastronomie', 'cuisine', 'vin', 'fromage', 'baguette', 'café',
            'festival', 'patrimoine', 'monument', 'musée', 'art français',
            
            # Government & Politics (affecting daily life)
            'gouvernement', 'président', 'assemblée nationale', 'sénat', 'maire',
            'conseil municipal', 'région', 'département', 'commune', 'élection',
            'réforme', 'loi', 'décret', 'politique sociale',
            
            # Economy & Work
            'emploi', 'chômage', 'smic', 'salaire', 'retraite', 'cotisation',
            'entreprise', 'startup', 'innovation', 'économie française', 'crise',
            'inflation', 'pouvoir d\'achat', 'marché du travail',
            
            # Education & Language
            'français langue étrangère', 'fle', 'apprentissage', 'intégration',
            'cours de français', 'alliance française', 'delf', 'dalf',
            
            # Regional Life
            'paris', 'région parisienne', 'province', 'métropole', 'banlieue',
            'quartier', 'arrondissement', 'ile-de-france'
        }
        
        self.medium_relevance_keywords = {
            # National Events & News
            'france', 'français', 'national', 'pays', 'état', 'société',
            'population', 'citoyen', 'public', 'social', 'communauté',
            
            # Current Affairs
            'actualité', 'information', 'débat', 'polémique', 'manifestation',
            'grève', 'syndical', 'droit', 'justice', 'tribunal',
            
            # Technology & Innovation
            'technologie', 'numérique', 'internet', 'intelligence artificielle',
            'startup française', 'innovation française',
            
            # Environment (affects daily life)
            'environnement', 'climat', 'pollution', 'transport public',
            'vélo', 'écologie', 'recyclage', 'énergie'
        }
        
        # Keywords that reduce relevance
        self.low_relevance_keywords = {
            'people', 'célébrité', 'star', 'télé-réalité', 'scandale',
            'paparazzi', 'instagram', 'tiktok', 'influenceur',
            'gossip', 'rumeur', 'vie privée'
        }
        
        # Importance indicators
        self.high_importance_indicators = {
            'breaking', 'urgent', 'alerte', 'important', 'majeur',
            'historique', 'exceptionnel', 'première fois', 'record',
            'crise', 'urgence', 'décision', 'annonce', 'officiel'
        }
        
        # Quality indicators
        self.quality_indicators = {
            'analysis': ['analyse', 'enquête', 'investigation', 'reportage', 'dossier'],
            'expertise': ['expert', 'spécialiste', 'professeur', 'chercheur', 'selon'],
            'sources': ['source', 'témoin', 'déclaration', 'interview', 'entretien'],
            'context': ['contexte', 'histoire', 'background', 'explication', 'pourquoi']
        }

    def score_quality(self, article: Dict[str, Any]) -> float:
        """Score article quality (0-10) based on writing, structure, completeness"""
        score = 5.0  # Base score
        
        title = (article.get('title') or '').lower()
        summary = (article.get('summary') or '').lower()
        content = (article.get('content') or '').lower()
        
        # Combine all text for analysis
        full_text = f"{title} {summary} {content}"
        
        # Quality factors
        
        # 1. Content completeness (+2)
        if content and len(content) > 200:
            score += 1.0
        if summary and len(summary) > 50:
            score += 0.5
        if article.get('author'):
            score += 0.5
        
        # 2. Writing quality indicators (+2)
        for category, keywords in self.quality_indicators.items():
            if any(keyword in full_text for keyword in keywords):
                score += 0.5
        
        # 3. Structure quality (+1)
        if len(title.split()) >= 5:  # Descriptive title
            score += 0.3
        if any(punct in title for punct in [':',  '«', '»']):  # French punctuation
            score += 0.2
        if summary and summary != title.lower():  # Unique summary
            score += 0.5
        
        # 4. Language quality (+1)
        # Check for proper French structure
        french_patterns = [
            r'\b(le|la|les|un|une|des)\b',  # Articles
            r'\b(est|sont|était|sera)\b',   # Common verbs
            r'\b(avec|dans|pour|sur|par)\b'  # Prepositions
        ]
        french_score = sum(1 for pattern in french_patterns if re.search(pattern, full_text))
        score += min(1.0, french_score * 0.2)
        
        # Quality penalties
        
        # Poor quality indicators (-2)
        poor_indicators = ['cliquez', 'buzz', 'choc', 'scandaleux', 'incroyable']
        if any(indicator in full_text for indicator in poor_indicators):
            score -= 1.0
            
        # Too short content (-1)
        if len(full_text) < 100:
            score -= 1.0
            
        # All caps title (clickbait) (-0.5)
        if title.isupper():
            score -= 0.5
        
        return max(0, min(10, score))

    def score_relevance(self, article: Dict[str, Any]) -> float:
        """Score relevance (0-10) for expats/immigrants living in France"""
        score = 3.0  # Base score for French news
        
        title = (article.get('title') or '').lower()
        summary = (article.get('summary') or '').lower()
        content = (article.get('content') or '').lower()
        category = (article.get('category') or '').lower()
        
        full_text = f"{title} {summary} {content} {category}"
        
        # High relevance for expat life (+4)
        high_matches = sum(1 for keyword in self.high_relevance_keywords 
                          if keyword in full_text)
        score += min(4.0, high_matches * 0.8)
        
        # Medium relevance for French society (+2)
        medium_matches = sum(1 for keyword in self.medium_relevance_keywords 
                           if keyword in full_text)
        score += min(2.0, medium_matches * 0.3)
        
        # Category-based relevance (+1)
        relevant_categories = [
            'politique', 'société', 'économie', 'france', 'national',
            'immigration', 'education', 'culture', 'santé', 'social'
        ]
        if any(cat in category for cat in relevant_categories):
            score += 1.0
        
        # Penalties for low relevance (-3)
        low_matches = sum(1 for keyword in self.low_relevance_keywords 
                         if keyword in full_text)
        score -= min(3.0, low_matches * 1.0)
        
        # International news penalty (unless affects France) (-1)
        international_indicators = ['états-unis', 'chine', 'russie', 'ukraine', 'gaza']
        france_context = ['france', 'français', 'hexagone', 'paris', 'gouvernement']
        
        if (any(indicator in full_text for indicator in international_indicators) and
            not any(context in full_text for context in france_context)):
            score -= 1.0
        
        return max(0, min(10, score))

    def score_importance(self, article: Dict[str, Any]) -> float:
        """Score importance (0-10) from perspective of someone living in France"""
        score = 4.0  # Base score
        
        title = (article.get('title') or '').lower()
        summary = (article.get('summary') or '').lower()
        content = (article.get('content') or '').lower()
        source = (article.get('source_name') or '').lower()
        
        full_text = f"{title} {summary} {content}"
        
        # Breaking news/urgent (+2)
        if any(indicator in full_text for indicator in self.high_importance_indicators):
            score += 2.0
        
        # Government/policy news (+2)
        policy_keywords = [
            'gouvernement', 'ministre', 'président', 'assemblée', 'sénat',
            'loi', 'décret', 'réforme', 'politique', 'décision officielle'
        ]
        if any(keyword in full_text for keyword in policy_keywords):
            score += 2.0
        
        # Economic impact (+1.5)
        economic_keywords = [
            'économie', 'emploi', 'chômage', 'inflation', 'prix', 'salaire',
            'impôt', 'budget', 'crise', 'marché', 'entreprise'
        ]
        if any(keyword in full_text for keyword in economic_keywords):
            score += 1.5
        
        # Social impact (+1.5)
        social_keywords = [
            'société', 'social', 'manifestation', 'grève', 'éducation',
            'santé', 'logement', 'transport', 'sécurité', 'justice'
        ]
        if any(keyword in full_text for keyword in social_keywords):
            score += 1.5
        
        # Source reputation (+1)
        reputable_sources = [
            'le monde', 'le figaro', 'france info', 'france 24', 'rfi',
            'libération', 'le parisien', 'afp'
        ]
        if any(source_name in source for source_name in reputable_sources):
            score += 1.0
        
        # Local/regional penalty (unless major city) (-1)
        local_indicators = ['commune', 'village', 'petit', 'local']
        major_cities = ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes']
        
        if (any(indicator in full_text for indicator in local_indicators) and
            not any(city in full_text for city in major_cities)):
            score -= 1.0
        
        return max(0, min(10, score))

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def find_duplicates(self, articles: List[Dict[str, Any]]) -> List[List[int]]:
        """Find groups of duplicate articles"""
        duplicate_groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if i in processed:
                continue
                
            current_group = [i]
            title1 = article1.get('title') or ''
            summary1 = article1.get('summary') or ''
            url1 = article1.get('link') or ''
            
            for j, article2 in enumerate(articles[i+1:], i+1):
                if j in processed:
                    continue
                    
                title2 = article2.get('title') or ''
                summary2 = article2.get('summary') or ''
                url2 = article2.get('link') or ''
                
                # Check for duplicates
                is_duplicate = False
                
                # Same URL
                if url1 and url2 and url1 == url2:
                    is_duplicate = True
                
                # High title similarity (>0.8)
                elif self.calculate_similarity(title1, title2) > 0.8:
                    is_duplicate = True
                
                # High summary similarity (>0.7) with some title similarity (>0.5)
                elif (self.calculate_similarity(summary1, summary2) > 0.7 and
                      self.calculate_similarity(title1, title2) > 0.5):
                    is_duplicate = True
                
                if is_duplicate:
                    current_group.append(j)
                    processed.add(j)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
            
            processed.add(i)
        
        return duplicate_groups

    def select_best_duplicate(self, articles: List[Dict[str, Any]], 
                            scores: List[float], indices: List[int]) -> int:
        """Select the best article from a group of duplicates"""
        best_idx = indices[0]
        best_score = scores[indices[0]]
        
        for idx in indices[1:]:
            # Primary: highest total score
            if scores[idx] > best_score:
                best_idx = idx
                best_score = scores[idx]
            # Tiebreaker: longer content
            elif (scores[idx] == best_score and
                  len(articles[idx].get('content') or '') > 
                  len(articles[best_idx].get('content') or '')):
                best_idx = idx
        
        return best_idx

    def curate_articles(self, input_file: str, quality_threshold: float = 5.0) -> Tuple[str, str]:
        """Main curation process"""
        logger.info(f"Starting curation process for {input_file}")
        
        # Load raw articles
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        articles = raw_data['articles']
        logger.info(f"Processing {len(articles)} articles")
        
        # Score all articles
        scored_articles = []
        for i, article in enumerate(articles):
            quality = self.score_quality(article)
            relevance = self.score_relevance(article)
            importance = self.score_importance(article)
            total = quality + relevance + importance
            
            scored_article = ScoredArticle(
                original_data=article,
                quality_score=quality,
                relevance_score=relevance,
                importance_score=importance,
                total_score=total,
                curation_id=str(uuid.uuid4()),
                curated_at=datetime.now(timezone.utc).isoformat()
            )
            
            scored_articles.append(scored_article)
            
            if i % 100 == 0:
                logger.info(f"Scored {i+1}/{len(articles)} articles")
        
        # Find and handle duplicates
        logger.info("Finding duplicates...")
        total_scores = [sa.total_score for sa in scored_articles]
        duplicate_groups = self.find_duplicates(articles)
        
        # Keep track of articles to remove
        to_remove = set()
        duplicate_info = []
        
        for group in duplicate_groups:
            best_idx = self.select_best_duplicate(articles, total_scores, group)
            removed_indices = [idx for idx in group if idx != best_idx]
            to_remove.update(removed_indices)
            
            duplicate_info.append({
                'kept': best_idx,
                'removed': removed_indices,
                'scores': [total_scores[idx] for idx in group]
            })
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups, removing {len(to_remove)} articles")
        
        # Separate curated vs rejected
        for i, scored_article in enumerate(scored_articles):
            if i in to_remove:
                scored_article.rejection_reason = "duplicate"
                self.rejected_articles.append(scored_article)
            elif scored_article.total_score < quality_threshold:
                scored_article.rejection_reason = f"low_score_{scored_article.total_score:.1f}"
                self.rejected_articles.append(scored_article)
            else:
                self.curated_articles.append(scored_article)
        
        # Sort curated articles by total score (descending)
        self.curated_articles.sort(key=lambda x: x.total_score, reverse=True)
        
        # Save results
        curated_file = self.save_curated_articles()
        rejected_file = self.save_rejected_articles()
        
        # Log results
        logger.info(f"Curation completed:")
        logger.info(f"  Curated articles: {len(self.curated_articles)}")
        logger.info(f"  Rejected articles: {len(self.rejected_articles)}")
        logger.info(f"  Duplicate groups found: {len(duplicate_groups)}")
        
        return curated_file, rejected_file

    def save_curated_articles(self, filename: str = None) -> str:
        """Save curated articles with metadata"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../04_Data_Output/Curated/curated_news_data_{timestamp}.json"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Calculate statistics
        if self.curated_articles:
            scores = {
                'quality': [a.quality_score for a in self.curated_articles],
                'relevance': [a.relevance_score for a in self.curated_articles],
                'importance': [a.importance_score for a in self.curated_articles],
                'total': [a.total_score for a in self.curated_articles]
            }
            
            stats = {}
            for score_type, values in scores.items():
                stats[score_type] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
        else:
            stats = {}
        
        data = {
            "metadata": {
                "curated_at": datetime.now(timezone.utc).isoformat(),
                "total_curated": len(self.curated_articles),
                "curator_version": "1.0",
                "statistics": stats,
                "scoring_system": {
                    "quality": "0-10 based on content completeness, writing quality, structure",
                    "relevance": "0-10 for expats/immigrants living in France",
                    "importance": "0-10 from perspective of someone living in France",
                    "total": "Sum of quality + relevance + importance (0-30)"
                }
            },
            "curated_articles": [asdict(article) for article in self.curated_articles]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Curated articles saved to {filename}")
        return filename

    def save_rejected_articles(self, filename: str = None) -> str:
        """Save rejected articles with rejection reasons"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../04_Data_Output/Rejected/rejected_news_data_{timestamp}.json"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Group rejections by reason
        rejection_stats = {}
        for article in self.rejected_articles:
            reason = article.rejection_reason
            rejection_stats[reason] = rejection_stats.get(reason, 0) + 1
        
        data = {
            "metadata": {
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "total_rejected": len(self.rejected_articles),
                "rejection_reasons": rejection_stats,
                "curator_version": "1.0"
            },
            "rejected_articles": [asdict(article) for article in self.rejected_articles]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Rejected articles saved to {filename}")
        return filename

def main():
    """Main function to run the curation process"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python news_quality_curator.py <input_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print("🎯 French News Quality Curator & Deduplication System")
    print("=" * 60)
    print("📍 Target Audience: Expats/Immigrants living in France")
    print("🔍 Focus: Quality + Relevance + Importance scoring")
    print()
    
    curator = FrenchNewsQualityCurator()
    
    try:
        curated_file, rejected_file = curator.curate_articles(input_file)
        
        print("\n" + "=" * 60)
        print("🎉 Curation Results:")
        print(f"✅ Curated articles: {len(curator.curated_articles)}")
        print(f"❌ Rejected articles: {len(curator.rejected_articles)}")
        print(f"📄 Curated file: {curated_file}")
        print(f"🗑️  Rejected file: {rejected_file}")
        
        if curator.curated_articles:
            avg_score = sum(a.total_score for a in curator.curated_articles) / len(curator.curated_articles)
            best_score = max(a.total_score for a in curator.curated_articles)
            print(f"📊 Average score: {avg_score:.1f}/30")
            print(f"🏆 Best score: {best_score:.1f}/30")
        
    except FileNotFoundError:
        print(f"❌ Error: File {input_file} not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 