#!/usr/bin/env python3
"""
Better French Max - Cost-Optimized AI Processor
Inherits exact AI processing logic from proven manual system
Enhanced with batch processing and cost optimization for automation
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from automation import AUTOMATION_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ProcessedArticle:
    """AI-processed article with enhanced learning content"""
    # Original article information
    original_article_title: str
    original_article_link: str
    original_article_published_date: str
    source_name: str
    
    # Quality scores (from curation)
    quality_scores: Dict[str, float]
    
    # AI-enhanced content for learning
    simplified_french_title: str
    simplified_english_title: str
    french_summary: str
    english_summary: str
    
    # Enhanced learning features
    contextual_title_explanations: List[Dict[str, str]]  # Detailed word-by-word explanations
    key_vocabulary: List[Dict[str, str]]                 # Important vocabulary from article
    cultural_context: Dict[str, str]                     # Cultural and practical context
    
    # Processing metadata
    processed_at: str
    processing_id: str
    curation_metadata: Dict[str, Any]
    
    # Cost tracking
    api_calls_used: int = 1
    processing_cost: float = 0.0

class CostOptimizedAIProcessor:
    """
    Cost-optimized AI processor for Better French Max
    Processes only top-quality articles in batches for maximum efficiency
    Inherits exact logic from proven manual system
    """
    
    def __init__(self):
        self.ai_config = AUTOMATION_CONFIG['ai_processing']
        self.cost_config = AUTOMATION_CONFIG['cost']
        
        # OpenRouter configuration (same as manual system)
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ OpenRouter API key not found in environment variables")
        
        self.api_base_url = "https://openrouter.ai/api/v1"
        self.model = self.ai_config['model']
        
        # Cost tracking
        self.daily_cost = 0.0
        self.daily_api_calls = 0
        self.batch_results = []
        
        # Processing statistics
        self.processing_stats = {
            'articles_processed_today': 0,
            'total_cost_today': 0.0,
            'average_processing_time': 0.0,
            'success_rate': 100.0,
            'failed_articles': []
        }
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://better-french-max.com',
            'X-Title': 'Better French Max - Automated AI Processing'
        })
        
        logger.info("🤖 Cost-Optimized AI Processor initialized")
        logger.info(f"📊 Model: {self.model}")
        logger.info(f"💰 Daily budget: ${self.cost_config['daily_cost_limit']}")
        logger.info(f"📄 Max articles per day: {self.cost_config['max_ai_articles_per_day']}")
    
    def check_cost_limits(self) -> Tuple[bool, str]:
        """Check if we're within cost limits before processing"""
        if self.daily_cost >= self.cost_config['daily_cost_limit']:
            return False, f"Daily cost limit reached: ${self.daily_cost:.2f}"
        
        if self.daily_api_calls >= self.cost_config['max_ai_calls_per_day']:
            return False, f"Daily API call limit reached: {self.daily_api_calls}"
        
        return True, "Within limits"
    
    def create_ai_prompt(self, article: Dict[str, Any]) -> str:
        """Create AI prompt using the exact proven approach from original script"""
        
        # Extract article data
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = article.get('content', '')
        
        # Use the exact few-shot examples from the proven system
        few_shot_examples = self._get_few_shot_examples()

        # EXACT Task 3 prompt from the original proven system
        explanation_prompt = f"""{few_shot_examples}
Analyze the following original French news title:
Original Title: {title}

Identify key French words, phrases, or entities that a non-native French speaker (intermediate level) might find difficult or that have specific cultural/contextual importance.
For each identified item, provide:
1.  `original_word`: The exact word or phrase from the title.
2.  `display_format`: A short, bolded translation or very brief definition (e.g., "**Customs Duties:** Taxes").
3.  `explanation`: A slightly more detailed explanation of the word/phrase in simple English.
4.  `cultural_note`: A brief cultural note in simple English if relevant, otherwise an empty string.

Return your response as a VALID JSON list of objects, where each object represents an explanation.
Example for a single item:
[
  {{
    "original_word": "Grève",
    "display_format": "**Strike:** (Industrial action)",
    "explanation": "A work stoppage caused by the mass refusal of employees to work, usually in response to employee grievances.",
    "cultural_note": "Strikes are a common form of protest in France and can significantly impact public services."
  }}
]

Ensure the output is ONLY the JSON list. Do not include any other text before or after the JSON.
Based on the title "{title}", provide the JSON list of contextual explanations:
"""
        
        return explanation_prompt

    def _get_few_shot_examples(self, num_examples=2):
        """Get comprehensive few-shot examples from the proven original system"""
        # COMPLETE pre_designed_data from the original proven system
        pre_designed_data = {
            "Droits de douane : ces options sur la table de Donald Trump après son revers judiciaire": {
                "contextual_title_explanations": [
                    {"original_word": "Droits de douane", "display_format": "**Customs Duties / Tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders. Governments usually impose customs duties to protect domestic industries, generate revenue, or regulate the flow of goods.", "cultural_note": "Trade tariffs are a significant tool in international economic policy and can become major points of contention between countries, as seen in various trade disputes involving the US, China, and the EU."},
                    {"original_word": "ces", "display_format": "**These:** (demonstrative adjective)", "explanation": "Used to point out specific items or options being discussed.", "cultural_note": ""},
                    {"original_word": "options", "display_format": "**Options:** Choices or alternatives.", "explanation": "Different courses of action that can be chosen.", "cultural_note": ""},
                    {"original_word": "sur la table", "display_format": "**On the table:** Under consideration; being discussed or negotiated.", "explanation": "An idiomatic expression meaning that something is available for discussion or is a possibility.", "cultural_note": "Similar to the English idiom 'on the table.'"},
                    {"original_word": "de", "display_format": "**Of / From:** (preposition)", "explanation": "Indicates possession, origin, or relationship.", "cultural_note": ""},
                    {"original_word": "Donald Trump", "display_format": "**Donald Trump:** 45th President of the United States.", "explanation": "A prominent American political figure and businessman.", "cultural_note": "His presidency was marked by significant changes to US trade policy, including the imposition of tariffs on goods from various countries."},
                    {"original_word": "après", "display_format": "**After:** (preposition)", "explanation": "Indicates something that follows in time.", "cultural_note": ""},
                    {"original_word": "son", "display_format": "**His / Her / Its:** (possessive adjective)", "explanation": "Indicates possession.", "cultural_note": ""},
                    {"original_word": "revers judiciaire", "display_format": "**Legal setback / Judicial defeat:** A loss or unfavorable outcome in a court case.", "explanation": "Refers to a situation where a legal case or argument has not been successful.", "cultural_note": "Such setbacks can force a re-evaluation of strategy, as discussed in the article regarding Trump's tariff policies."}
                ]
            },
            "EXCLUSIF. Des cadres des Verts plaident pour adhérer à BDS, mouvement controversé de boycott d'Israël": {
                "contextual_title_explanations": [
                    {"original_word": "EXCLUSIF", "display_format": "**EXCLUSIVE:** (adjective/noun)", "explanation": "Indicates that the information is being reported for the first time by this news outlet.", "cultural_note": "Commonly used in headlines to attract attention."},
                    {"original_word": "Des cadres", "display_format": "**Executives / Leading members / Cadres:** Senior or influential members of an organization.", "explanation": "'Cadre' refers to a manager, executive, or a key member of a political party or organization.", "cultural_note": "In French politics, 'cadres' are the backbone of a party's leadership and decision-making structure."},
                    {"original_word": "des Verts", "display_format": "**Of the Greens (French Green Party):** Refers to the French political party focused on environmental issues (Europe Écologie Les Verts - EELV).", "explanation": "'Les Verts' is the common name for the French Green Party.", "cultural_note": "Like Green parties in other countries, they advocate for ecological policies and often align with left-leaning social stances."},
                    {"original_word": "plaident pour", "display_format": "**Advocate for / Argue in favor of:** To publicly support or recommend a particular cause or policy.", "explanation": "'Plaider' means to plead or argue a case.", "cultural_note": ""},
                    {"original_word": "adhérer à", "display_format": "**To join / To adhere to:** To become a member of or to formally agree to support.", "explanation": "'Adhérer' means to stick to, or in a political context, to join or subscribe to a movement or party.", "cultural_note": ""},
                    {"original_word": "BDS", "display_format": "**BDS (Boycott, Divestment, Sanctions):** A Palestinian-led movement promoting boycotts, divestments, and economic sanctions against Israel.", "explanation": "The movement aims to pressure Israel to meet what it describes as Israel's obligations under international law.", "cultural_note": "BDS is a highly controversial movement, with strong opinions both for and against its methods and goals. Its potential adoption by political parties often sparks significant debate."},
                    {"original_word": "mouvement", "display_format": "**Movement:** A group of people working together to advance their shared political, social, or artistic ideas.", "explanation": "Refers to an organized effort or campaign.", "cultural_note": ""},
                    {"original_word": "controversé", "display_format": "**Controversial:** Giving rise or likely to give rise to public disagreement.", "explanation": "Indicates that the subject is a matter of dispute or strong opinions.", "cultural_note": ""},
                    {"original_word": "de boycott", "display_format": "**Of boycott:** Relating to the act of boycotting.", "explanation": "A boycott is a collective refusal to deal with a person, organization, or country as an expression of protest.", "cultural_note": ""},
                    {"original_word": "d'Israël", "display_format": "**Of Israel:** Relating to the state of Israel.", "explanation": "Referring to the country in the Middle East.", "cultural_note": ""}
                ]
            },
            "Présidentielle en Pologne : l'élection qui donne des sueurs froides à Bruxelles": {
                "contextual_title_explanations": [
                    {"original_word": "Présidentielle", "display_format": "**Presidential (election):** Relating to the election of a president.", "explanation": "Refers to the process of electing a head of state in a republic.", "cultural_note": ""},
                    {"original_word": "en Pologne", "display_format": "**In Poland:** Referring to the country of Poland.", "explanation": "A country in Central Europe.", "cultural_note": "Poland's political direction has significant implications for the European Union, given its size and strategic location."},
                    {"original_word": "l'élection", "display_format": "**The election:** The process of choosing someone for a public office by voting.", "explanation": "A formal and organized choice by vote of a person for a political office or other position.", "cultural_note": ""},
                    {"original_word": "qui donne des sueurs froides", "display_format": "**Which is causing cold sweats / Causing great anxiety:** An idiomatic expression.", "explanation": "Literally 'gives cold sweats,' it means something that causes extreme worry, fear, or anxiety.", "cultural_note": "A common French idiom to express strong apprehension."},
                    {"original_word": "à Bruxelles", "display_format": "**To Brussels (referring to the EU):** Brussels is the de facto capital of the European Union.", "explanation": "When French media mentions 'Bruxelles' in a political context, it often refers to the institutions and decision-making bodies of the European Union.", "cultural_note": "Similar to how 'Washington' is often used to refer to the US federal government."}
                ]
            },
            "Droits de douane : ces cinq petites entreprises qui ont mis un frein à la machine Trump": {
                "contextual_title_explanations": [
                    {"original_word": "Droits de douane", "display_format": "**Customs Duties / Tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders.", "cultural_note": "A recurring theme in trade policy discussions."},
                    {"original_word": "ces cinq petites entreprises", "display_format": "**These five small businesses:** Referring to specific small companies.", "explanation": "'Petites entreprises' are small to medium-sized enterprises (SMEs), often called PME in French.", "cultural_note": "Small businesses are often portrayed as being particularly vulnerable to broad economic policy shifts like tariffs."},
                    {"original_word": "qui ont mis un frein à", "display_format": "**That put a brake on / That slowed down:** An idiomatic expression.", "explanation": "Means to slow down or hinder the progress of something.", "cultural_note": "Similar to the English idiom 'put the brakes on.'"},
                    {"original_word": "la machine Trump", "display_format": "**The Trump machine:** Refers to the administrative and political apparatus of Donald Trump's presidency.", "explanation": "A metaphorical way to describe the functioning and policies of his government.", "cultural_note": "The term 'machine' often implies a powerful, relentless, and somewhat impersonal force."}
                ]
            },
            "Etats-Unis : la Cour d'appel maintient les droits de douane de Donald Trump": {
                "contextual_title_explanations": [
                    {"original_word": "Etats-Unis", "display_format": "**United States:** Referring to the United States of America.", "explanation": "Country in North America.", "cultural_note": ""},
                    {"original_word": "la Cour d'appel", "display_format": "**The Court of Appeal / Appeals Court:** A court that hears appeals from lower court decisions.", "explanation": "A higher court that reviews the decisions of trial courts or other lower courts.", "cultural_note": "An essential part of the judicial process, allowing for review and potential correction of legal errors."},
                    {"original_word": "maintient", "display_format": "**Maintains / Upholds:** To keep in an existing state; to preserve from failure or decline.", "explanation": "In a legal context, it means to affirm or keep a previous decision or state of affairs in place.", "cultural_note": ""},
                    {"original_word": "les droits de douane", "display_format": "**The customs duties / The tariffs:** Taxes on imported goods.", "explanation": "Taxes imposed on goods when they are transported across international borders.", "cultural_note": ""},
                    {"original_word": "de Donald Trump", "display_format": "**Of Donald Trump:** Belonging to or enacted by Donald Trump.", "explanation": "Refers to policies associated with his presidency.", "cultural_note": ""}
                ]
            },
            "Guerre à Gaza : Benyamin Netanyahou, le grand divorce avec les Israéliens": {
                "contextual_title_explanations": [
                    {"original_word": "Guerre à Gaza", "display_format": "**War in Gaza:** Referring to the conflict in the Gaza Strip.", "explanation": "The Gaza Strip is a Palestinian exclave on the eastern coast of the Mediterranean Sea.", "cultural_note": "This conflict is a long-standing and deeply divisive issue with significant international repercussions."},
                    {"original_word": "Benyamin Netanyahou", "display_format": "**Benjamin Netanyahu:** Current Prime Minister of Israel.", "explanation": "A prominent Israeli politician who has served multiple terms as Prime Minister.", "cultural_note": "A highly polarizing figure both within Israel and internationally."},
                    {"original_word": "le grand divorce", "display_format": "**The great divorce / The major split:** Signifies a significant separation or estrangement.", "explanation": "Implies a deep and serious disagreement or breakdown of a relationship.", "cultural_note": "Used metaphorically here to describe the relationship between Netanyahu and the Israeli public."},
                    {"original_word": "avec les Israéliens", "display_format": "**With the Israelis:** Referring to the people of Israel.", "explanation": "The citizens of the State of Israel.", "cultural_note": ""}
                ]
            },
            "Face à la Chine, l'Europe en quête d'une nouvelle stratégie industrielle": {
                "contextual_title_explanations": [
                    {"original_word": "Face à la Chine", "display_format": "**Facing China / In response to China:** Indicates a reaction or positioning relative to China.", "explanation": "Highlights the challenges or competition posed by China.", "cultural_note": "China's rise as a global economic power is a central theme in international relations and economic policy discussions in Europe."},
                    {"original_word": "l'Europe", "display_format": "**Europe (often referring to the EU):** The continent, but in policy contexts, usually means the European Union.", "explanation": "The European Union as a political and economic entity.", "cultural_note": ""},
                    {"original_word": "en quête d'une", "display_format": "**In search of a / Seeking a:** Looking for or trying to find something.", "explanation": "", "cultural_note": ""},
                    {"original_word": "nouvelle stratégie industrielle", "display_format": "**New industrial strategy:** A revised plan concerning a country's or region's manufacturing and industrial sectors.", "explanation": "Refers to policies aimed at promoting industrial growth, innovation, and competitiveness.", "cultural_note": "Industrial strategy is a key area of EU policy as it seeks to maintain its economic standing."}
                ]
            },
            "IA générative : pourquoi la France est en train de perdre la bataille face aux Etats-Unis": {
                "contextual_title_explanations": [
                    {"original_word": "IA générative", "display_format": "**Generative AI:** Artificial Intelligence that can create new content.", "explanation": "A subset of AI that can generate text, images, audio, and other media in response to prompts.", "cultural_note": "A rapidly advancing field with significant economic and societal implications, dominated by major US tech companies but with active research and development globally."},
                    {"original_word": "pourquoi la France est en train de perdre la bataille", "display_format": "**Why France is losing the battle:** Explores the reasons behind France's perceived disadvantage.", "explanation": "Suggests a competitive struggle where France is not succeeding.", "cultural_note": "There's often a public debate in France about its technological competitiveness, particularly vis-à-vis the US and China."},
                    {"original_word": "face aux Etats-Unis", "display_format": "**Against the United States / Compared to the United States:** Highlighting the US as the primary competitor or benchmark.", "explanation": "", "cultural_note": ""}
                ]
            },
            "Réforme des retraites : le gouvernement face au mur de la dette": {
                "contextual_title_explanations": [
                    {"original_word": "Réforme des retraites", "display_format": "**Pension Reform:** Changes to the national retirement system.", "explanation": "Refers to government policies aimed at modifying how pensions are funded, calculated, and when people can retire.", "cultural_note": "Pension reform is a highly sensitive and frequently debated political issue in France, often leading to widespread protests and strikes."},
                    {"original_word": "le gouvernement", "display_format": "**The government:** The ruling administration.", "explanation": "The executive branch of the French state.", "cultural_note": ""},
                    {"original_word": "face au mur de la dette", "display_format": "**Facing the debt wall:** Confronting a significant and challenging level of national debt.", "explanation": "The 'wall' metaphor emphasizes the difficulty and scale of the problem.", "cultural_note": "France, like many developed countries, has a substantial national debt, and its management is a constant concern for policymakers."}
                ]
            },
            "Inflation : les prix alimentaires vont-ils enfin baisser ?": {
                "contextual_title_explanations": [
                    {"original_word": "Inflation", "display_format": "**Inflation:** The rate at which the general level of prices for goods and services is rising.", "explanation": "A key economic indicator reflecting the erosion of purchasing power.", "cultural_note": "High inflation, especially for essential goods like food, is a major concern for the public and policymakers."},
                    {"original_word": "les prix alimentaires", "display_format": "**Food prices:** The cost of food items.", "explanation": "", "cultural_note": ""},
                    {"original_word": "vont-ils enfin baisser ?", "display_format": "**Will they finally decrease? / Are they finally going to go down?:** Expresses a sense of anticipation or hope for a reduction.", "explanation": "The word 'enfin' (finally) suggests a period of waiting or suffering high prices.", "cultural_note": ""}
                ]
            },
            "Climat : la France peut-elle atteindre ses objectifs de réduction d'émissions ?": {
                "contextual_title_explanations": [
                    {"original_word": "Climat", "display_format": "**Climate:** Referring to climate change.", "explanation": "The long-term alteration of temperature and typical weather patterns in a place.", "cultural_note": "Climate change is a major global concern, and countries have set targets to reduce their impact."},
                    {"original_word": "la France peut-elle atteindre", "display_format": "**Can France achieve / Can France reach:** Questions the feasibility of achieving a goal.", "explanation": "", "cultural_note": ""},
                    {"original_word": "ses objectifs de réduction d'émissions ?", "display_format": "**Its emission reduction targets?:** The specific goals set for lowering greenhouse gas output.", "explanation": "These targets are often part of national or international agreements like the Paris Agreement.", "cultural_note": "Meeting these targets requires significant policy changes and investments."}
                ]
            },
            "JO 2024 : à un an de l'événement, Paris est-elle prête ?": {
                "contextual_title_explanations": [
                    {"original_word": "JO 2024", "display_format": "**2024 Olympics (Jeux Olympiques):** Referring to the Olympic Games scheduled for 2024.", "explanation": "'JO' is the common French abbreviation for 'Jeux Olympiques'.", "cultural_note": "Hosting the Olympics is a major undertaking for any city, involving massive investment and global attention. Paris 2024 is a significant national project for France."},
                    {"original_word": "à un an de l'événement", "display_format": "**One year from the event / With one year to go:** Marking the one-year countdown.", "explanation": "", "cultural_note": ""},
                    {"original_word": "Paris est-elle prête ?", "display_format": "**Is Paris ready?:** Questions the city's state of preparedness.", "explanation": "", "cultural_note": "Media scrutiny of Olympic preparations typically intensifies as the event approaches."}
                ]
            }
        }
        
        # Select examples for few-shot prompting
        example_keys = list(pre_designed_data.keys())
        selected_examples = []
        for i in range(min(num_examples, len(example_keys))):
            key = example_keys[i]
            data = pre_designed_data[key]
            example_str = f"EXAMPLE {i+1}:\nOriginal Title: \"{key}\"\nContextual Title Explanations (JSON format):\n{json.dumps(data['contextual_title_explanations'], ensure_ascii=False, indent=2)}\n---\n"
            selected_examples.append(example_str)
        return "\n".join(selected_examples)
    
    def call_openrouter_api(self, prompt: str, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call OpenRouter API with the exact approach from original system"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant for 'Better French'. Your goal is to help non-native French speakers understand complex French news articles. Provide clear, concise, and accurate information. For contextual explanations, provide them in a valid JSON list format as specified in the examples."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            response = self.session.post(
                f"{self.api_base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract AI response
                ai_content = result['choices'][0]['message']['content'].strip()
                logger.info(f"🤖 AI raw response length: {len(ai_content)} characters")
                
                # Parse the contextual explanations (exact approach from original)
                try:
                    # Clean up the response to extract JSON
                    if ai_content.startswith('```json'):
                        ai_content = ai_content[7:]
                    if ai_content.endswith('```'):
                        ai_content = ai_content[:-3]
                    
                    ai_content = ai_content.strip()
                    
                    # Parse the JSON list of explanations
                    contextual_explanations = json.loads(ai_content)
                    
                    if isinstance(contextual_explanations, list):
                        logger.info(f"✅ Successfully parsed {len(contextual_explanations)} contextual explanations!")
                        
                        # Debug: Log explanations
                        for i, exp in enumerate(contextual_explanations[:3]):
                            if isinstance(exp, dict) and 'original_word' in exp:
                                logger.info(f"   {i+1}. {exp['original_word']} -> {exp.get('display_format', '')[:50]}...")
                        
                        # Return in the format expected by our system
                        return {
                            "simplified_french_title": f"Version simplifiée: {article.get('title', '')[:50]}...",
                            "simplified_english_title": f"Simplified: {article.get('title', '')[:50]}...",
                            "french_summary": "Résumé français simplifié généré par l'IA.",
                            "english_summary": "English summary generated by AI.",
                            "contextual_title_explanations": contextual_explanations,
                            "key_vocabulary": [],
                            "cultural_context": {}
                        }
                    else:
                        logger.warning(f"❌ AI returned non-list: {type(contextual_explanations)}")
                        return None
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Failed to parse AI JSON response: {e}")
                    logger.warning(f"Raw response: {ai_content[:200]}...")
                    return None
                
                # Track costs
                usage = result.get('usage', {})
                estimated_cost = (usage.get('total_tokens', 500) / 1000) * 0.01
                self.daily_cost += estimated_cost
                self.daily_api_calls += 1
                
            else:
                logger.error(f"❌ OpenRouter API error {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error calling OpenRouter API: {e}")
            return None
    
    def _extract_explanations_manually(self, ai_content: str) -> List[Dict[str, str]]:
        """Manually extract contextual explanations from malformed AI response"""
        explanations = []
        
        try:
            # Look for contextual_title_explanations section
            start_marker = '"contextual_title_explanations":'
            start_idx = ai_content.find(start_marker)
            if start_idx == -1:
                return []
            
            # Find the start of the array
            array_start = ai_content.find('[', start_idx)
            if array_start == -1:
                return []
            
            # Find the matching closing bracket
            bracket_count = 0
            array_end = array_start
            for i, char in enumerate(ai_content[array_start:]):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        array_end = array_start + i + 1
                        break
            
            # Extract just the explanations array
            explanations_text = ai_content[array_start:array_end]
            explanations = json.loads(explanations_text)
            
            logger.info(f"🔧 Successfully extracted {len(explanations)} explanations manually")
            return explanations
            
        except Exception as e:
            logger.error(f"❌ Manual extraction failed: {e}")
            return []
    
    def process_single_article(self, scored_article: Dict[str, Any]) -> Optional[ProcessedArticle]:
        """Process a single article with AI enhancement"""
        try:
            # Extract original article data
            if 'original_data' in scored_article:
                original_data = scored_article['original_data']
                quality_scores = {
                    'quality_score': scored_article.get('quality_score', 0),
                    'relevance_score': scored_article.get('relevance_score', 0),
                    'importance_score': scored_article.get('importance_score', 0),
                    'total_score': scored_article.get('total_score', 0)
                }
            else:
                original_data = scored_article
                quality_scores = {}
            
            # Create AI prompt
            prompt = self.create_ai_prompt(original_data)
            
            # Call OpenRouter API
            start_time = time.time()
            ai_result = self.call_openrouter_api(prompt, original_data)
            processing_time = time.time() - start_time
            
            if not ai_result:
                logger.warning(f"⚠️ AI processing failed for: {original_data.get('title', 'Unknown')[:50]}...")
                return None
            
            # Create processed article
            processed = ProcessedArticle(
                original_article_title=original_data.get('title', ''),
                original_article_link=original_data.get('link', ''),
                original_article_published_date=original_data.get('published', ''),
                source_name=original_data.get('source_name', ''),
                quality_scores=quality_scores,
                simplified_french_title=ai_result.get('simplified_french_title', ''),
                simplified_english_title=ai_result.get('simplified_english_title', ''),
                french_summary=ai_result.get('french_summary', ''),
                english_summary=ai_result.get('english_summary', ''),
                contextual_title_explanations=ai_result.get('contextual_title_explanations', []),
                key_vocabulary=ai_result.get('key_vocabulary', []),
                cultural_context=ai_result.get('cultural_context', {}),
                processed_at=datetime.now(timezone.utc).isoformat(),
                processing_id=f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(original_data.get('link', '')) % 10000}",
                curation_metadata={
                    'curation_id': scored_article.get('curation_id', ''),
                    'curated_at': scored_article.get('curated_at', ''),
                    'fast_tracked': scored_article.get('fast_tracked', False)
                },
                api_calls_used=1,
                processing_cost=self.daily_cost - (self.processing_stats['total_cost_today'])
            )
            
            # Update statistics
            self.processing_stats['articles_processed_today'] += 1
            self.processing_stats['total_cost_today'] = self.daily_cost
            self.processing_stats['average_processing_time'] = (
                (self.processing_stats['average_processing_time'] * (self.processing_stats['articles_processed_today'] - 1) + processing_time) /
                self.processing_stats['articles_processed_today']
            )
            
            logger.info(f"✨ AI processed: {processed.simplified_french_title[:50]}...")
            logger.debug(f"💰 Cost: ${processed.processing_cost:.4f}, Time: {processing_time:.2f}s")
            
            return processed
            
        except Exception as e:
            logger.error(f"❌ Failed to process article: {e}")
            self.processing_stats['failed_articles'].append({
                'title': original_data.get('title', 'Unknown')[:50],
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            return None
    
    def batch_process_articles(self, articles: List[Dict[str, Any]]) -> List[ProcessedArticle]:
        """Process articles in cost-optimized batches"""
        logger.info(f"🤖 Starting batch AI processing of {len(articles)} articles...")
        
        # Check cost limits
        can_process, limit_message = self.check_cost_limits()
        if not can_process:
            logger.warning(f"💰 {limit_message}")
            return []
        
        # Limit to max articles per day
        max_articles = self.cost_config['max_ai_articles_per_day']
        articles_to_process = articles[:max_articles]
        
        if len(articles) > max_articles:
            logger.info(f"📊 Processing top {max_articles} articles (limit applied)")
        
        processed_articles = []
        batch_start_time = time.time()
        
        # Process articles with rate limiting
        for i, article in enumerate(articles_to_process):
            # Check cost limits before each article
            can_continue, limit_message = self.check_cost_limits()
            if not can_continue:
                logger.warning(f"💰 Stopping batch processing: {limit_message}")
                break
            
            logger.info(f"🔄 Processing article {i+1}/{len(articles_to_process)}: {article.get('original_data', article).get('title', 'Unknown')[:50]}...")
            
            processed = self.process_single_article(article)
            if processed:
                processed_articles.append(processed)
            
            # Rate limiting - small delay between API calls
            if i < len(articles_to_process) - 1:  # Don't wait after the last article
                time.sleep(self.ai_config['rate_limit_delay'])
        
        # Calculate batch statistics
        batch_duration = time.time() - batch_start_time
        success_rate = (len(processed_articles) / len(articles_to_process)) * 100 if articles_to_process else 100
        
        self.processing_stats['success_rate'] = success_rate
        
        logger.info(f"🎉 Batch processing completed:")
        logger.info(f"   ✅ Successfully processed: {len(processed_articles)}/{len(articles_to_process)} articles")
        logger.info(f"   💰 Total cost: ${self.daily_cost:.4f}")
        logger.info(f"   ⏱️ Batch duration: {batch_duration:.2f}s")
        logger.info(f"   📊 Success rate: {success_rate:.1f}%")
        
        return processed_articles
    
    def save_processed_articles(self, processed_articles: List[ProcessedArticle], filename: str = None) -> str:
        """Save processed articles with metadata"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../data/live/ai_processed_articles_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Calculate statistics
        if processed_articles:
            scores = [a.quality_scores.get('total_score', 0) for a in processed_articles if a.quality_scores]
            avg_score = sum(scores) / len(scores) if scores else 0
        else:
            avg_score = 0
        
        data = {
            "metadata": {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "total_processed": len(processed_articles),
                "ai_processor_version": "Cost-Optimized AI Processor 1.0",
                "automation_system": "Better French Max Automated System",
                "model_used": self.model,
                "processing_statistics": self.processing_stats,
                "cost_efficiency": {
                    "daily_cost": self.daily_cost,
                    "cost_per_article": self.daily_cost / len(processed_articles) if processed_articles else 0,
                    "api_calls_used": self.daily_api_calls,
                    "articles_per_call_ratio": len(processed_articles) / self.daily_api_calls if self.daily_api_calls else 0
                },
                "quality_metrics": {
                    "average_total_score": avg_score,
                    "articles_from_top_sources": len([a for a in processed_articles if a.source_name in ['Le Monde', 'Le Figaro', 'France Info']])
                }
            },
            "processed_articles": [asdict(article) for article in processed_articles]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 AI processed articles saved: {filename}")
        return filename
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary for monitoring"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "active" if self.daily_api_calls < self.cost_config['max_ai_calls_per_day'] else "limit_reached",
            "daily_statistics": self.processing_stats,
            "cost_tracking": {
                "daily_cost": self.daily_cost,
                "daily_budget": self.cost_config['daily_cost_limit'],
                "remaining_budget": max(0, self.cost_config['daily_cost_limit'] - self.daily_cost),
                "api_calls_used": self.daily_api_calls,
                "api_calls_limit": self.cost_config['max_ai_calls_per_day']
            },
            "efficiency_metrics": {
                "cost_per_article": self.daily_cost / max(1, self.processing_stats['articles_processed_today']),
                "average_processing_time": self.processing_stats['average_processing_time'],
                "success_rate": self.processing_stats['success_rate']
            }
        }
    
    def reset_daily_counters(self):
        """Reset daily tracking counters (called at midnight)"""
        self.daily_cost = 0.0
        self.daily_api_calls = 0
        self.processing_stats = {
            'articles_processed_today': 0,
            'total_cost_today': 0.0,
            'average_processing_time': 0.0,
            'success_rate': 100.0,
            'failed_articles': []
        }
        logger.info("🔄 Daily AI processing counters reset")

# Test function for development
def test_ai_processor():
    """Test the AI processor functionality"""
    print("🧪 Testing Cost-Optimized AI Processor...")
    
    # Check if API key is available
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️ No OpenRouter API key found - creating mock test")
        
        # Create processor anyway for testing structure
        processor = CostOptimizedAIProcessor()
        
        # Test article structure
        test_article = {
            'original_data': {
                'title': 'Test: Nouvelle réforme de l\'immigration en France',
                'summary': 'Le gouvernement annonce des changements importants.',
                'content': 'Le ministre a présenté les nouvelles mesures...',
                'source_name': 'Test Source',
                'link': 'https://example.com',
                'published': '2024-01-01T10:00:00Z'
            },
            'quality_score': 8.0,
            'relevance_score': 9.0,
            'importance_score': 8.5,
            'total_score': 25.5,
            'curation_id': 'test-123'
        }
        
        print(f"🎯 Test article created with score: {test_article['total_score']}")
        print(f"💰 Daily cost limit: ${processor.cost_config['daily_cost_limit']}")
        print(f"📄 Max articles per day: {processor.cost_config['max_ai_articles_per_day']}")
        
        # Test cost limits
        can_process, message = processor.check_cost_limits()
        print(f"🚦 Cost check: {can_process} - {message}")
        
        # Get processing summary
        summary = processor.get_processing_summary()
        print(f"📊 Processing status: {summary['status']}")
        
        print("✅ AI Processor structure test completed (no API calls made)")
        return
    
    # Full test with API if key is available
    processor = CostOptimizedAIProcessor()
    
    # Create test article
    test_article = {
        'original_data': {
            'title': 'Nouvelle loi sur l\'immigration: ce qui va changer pour les étudiants étrangers',
            'summary': 'Le Parlement a adopté une nouvelle loi qui modifie les conditions de séjour pour les étudiants étrangers en France.',
            'content': 'La nouvelle législation, votée hier soir, prévoit des changements significatifs dans les procédures d\'obtention et de renouvellement des titres de séjour pour les étudiants internationaux.',
            'source_name': 'Le Monde',
            'link': 'https://example.com/test-article',
            'published': '2024-01-01T10:00:00Z'
        },
        'quality_score': 8.5,
        'relevance_score': 9.2,
        'importance_score': 8.8,
        'total_score': 26.5,
        'curation_id': 'test-456',
        'curated_at': '2024-01-01T10:00:00Z'
    }
    
    print(f"🎯 Test article: {test_article['original_data']['title'][:50]}...")
    print(f"📊 Quality score: {test_article['total_score']}/30")
    
    # Test single article processing
    try:
        processed = processor.process_single_article(test_article)
        if processed:
            print(f"✅ AI processing successful:")
            print(f"   🇫🇷 French title: {processed.simplified_french_title}")
            print(f"   🇬🇧 English title: {processed.simplified_english_title}")
            print(f"   💰 Cost: ${processed.processing_cost:.4f}")
        else:
            print("❌ AI processing failed")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test batch processing (with single article)
    try:
        batch_result = processor.batch_process_articles([test_article])
        print(f"📦 Batch processing result: {len(batch_result)} articles processed")
        
        if batch_result:
            # Save results
            saved_file = processor.save_processed_articles(batch_result)
            print(f"💾 Results saved: {saved_file}")
    except Exception as e:
        print(f"❌ Batch test error: {e}")
    
    # Get summary
    summary = processor.get_processing_summary()
    print(f"📈 Final summary: {summary['daily_statistics']['articles_processed_today']} articles, ${summary['cost_tracking']['daily_cost']:.4f} cost")
    
    print("✅ AI Processor test completed")

if __name__ == "__main__":
    test_ai_processor() 