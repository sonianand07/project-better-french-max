# 🇫🇷 Project Better French Max

A sophisticated **French language learning system** designed for expats and immigrants living in France. This project automatically scrapes, curates, and processes French news articles to create an interactive learning experience with AI-enhanced content.

## 🎯 What This Project Does

**Better French Max** transforms daily French news into a powerful language learning tool by:

- 📰 **Scraping** 24+ major French news sources (Le Monde, Le Figaro, BFM TV, etc.)
- 🎯 **Curating** articles specifically relevant to expats/immigrants in France
- 🤖 **AI Processing** to generate simplified summaries and word-by-word explanations
- 🌐 **Beautiful Website** with interactive tooltips and dual-mode learning

## ✨ Features

### 🔍 **Intelligent News Curation**
- Scrapes **24+ French news sources** in real-time
- Filters for **expat/immigrant relevance** (immigration, daily life, French culture)
- **Quality scoring** system (0-30 scale) for learning effectiveness
- **Automatic deduplication** and cleanup

### 🤖 **AI-Enhanced Learning**
- **Simplified English/French titles** for easier comprehension
- **Detailed bilingual summaries** 
- **Interactive word explanations** with cultural context
- **Contextual tooltips** on every French word

### 🌐 **Beautiful Learning Interface**
- **Dual Mode**: Toggle between Learner (English) and Native (French) modes
- **Interactive tooltips** on hover for French words
- **Real-time search** and filtering
- **Responsive design** (desktop, tablet, mobile)
- **Steve Jobs-inspired** minimalist UI

## 🚀 Quick Start

### 1️⃣ **Clone & Setup**
```bash
git clone https://github.com/yourusername/project-better-french-max.git
cd project-better-french-max
```

### 2️⃣ **Configure API Key**
```bash
# Copy the config template
cp 02_Scripts/config_template.py 02_Scripts/config.py

# Edit config.py and add your OpenRouter API key
# Get your key from: https://openrouter.ai/keys
```

### 3️⃣ **Install Dependencies**
```bash
pip install feedparser requests python-dateutil openai
```

### 4️⃣ **Run the Website** (with existing data)
```bash
cd better-french-website
python3 -m http.server 8000
# Visit: http://localhost:8000
```

### 5️⃣ **Scrape Fresh News** (optional)
```bash
cd 02_Scripts
python3 french_news_pipeline_auto_cleanup.py
```

## 📁 Project Structure

```
project-better-french-max/
├── 📂 better-french-website/     # 🌐 Interactive learning website
│   ├── index.html               # Main page
│   ├── styles.css               # Beautiful styling
│   ├── script.js                # Interactive features
│   └── README.md                # Website documentation
├── 📂 02_Scripts/               # 🤖 Data processing pipeline
│   ├── french_news_scraper.py   # News scraping
│   ├── news_quality_curator.py  # Article curation
│   ├── ai_processor.py          # AI enhancement
│   ├── french_news_pipeline_auto_cleanup.py # Full pipeline
│   └── config_template.py       # API configuration template
├── 📂 01_Documentation/         # 📖 Project docs
├── 📂 03_Configuration/         # ⚙️ Settings
├── 📂 06_Environment/           # 🔧 Environment setup
└── 📂 07_System_Files/         # 🗂️ System utilities
```

## 🔧 Data Pipeline

### **1. 📰 News Scraping**
- Scrapes **24+ French news sources** concurrently
- **Real-time 24-hour filtering** (only fresh articles)
- Saves to `04_Data_Output/Raw/`

### **2. 🎯 Quality Curation** 
- **Relevance scoring** for expat/immigrant needs
- **Quality assessment** (writing, sources, completeness)
- **Importance ranking** (breaking news, major events)
- **Deduplication** of similar articles

### **3. 🤖 AI Enhancement**
- **Simplified titles** in English and French
- **Comprehensive summaries** in both languages
- **Word-by-word explanations** with cultural context
- **Interactive tooltips** for every French word

### **4. 🌐 Web Display**
- **Automatic loading** of processed articles
- **Dual-mode interface** (Learner/Native)
- **Search and filtering** capabilities
- **Responsive design** for all devices

## 🎓 Learning Features

### **📚 For French Learners**
- **Simplified vocabulary** and explanations
- **Cultural context** for French expressions
- **Grammar insights** embedded in tooltips
- **Progressive difficulty** based on article complexity

### **🏡 For Expats in France**
- **Immigration and legal updates**
- **Daily life services** (healthcare, banking, education)
- **Cultural understanding** and social norms
- **Regional and local news** relevant to residents

## 🔐 Security & Privacy

- ✅ **API keys protected** (never committed to git)
- ✅ **No personal data** stored or transmitted
- ✅ **Local processing** (runs entirely on your machine)
- ✅ **Open source** and transparent

## 🛠️ Technical Requirements

### **System Requirements**
- **Python 3.8+**
- **Internet connection** (for news scraping and AI processing)
- **Modern web browser** (Chrome 80+, Firefox 75+, Safari 13+)

### **Python Dependencies**
```bash
pip install feedparser requests python-dateutil openai
```

### **API Requirements**
- **OpenRouter API key** (for AI processing)
- Get yours at: [https://openrouter.ai/keys](https://openrouter.ai/keys)

## 📊 News Sources

**Major Newspapers**: Le Monde, Le Figaro, Libération, Le Parisien, L'Express, Le Point, L'Obs, La Croix

**TV/Radio**: BFM TV, France Info, France Inter, Europe 1, France 24, RFI

**Regional**: Ouest France, 20 Minutes, AFP

**Specialized**: Mediapart, Brief.me, Le Monde (Politics, International, Economy, Culture, Sports, Sciences)

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

## 🙏 Acknowledgments

- **French news sources** for providing RSS feeds
- **OpenRouter** for AI processing capabilities
- **French language learners** and expats for inspiration

## 🆘 Support

If you encounter any issues:

1. **Check** the logs in `05_Logs/`
2. **Verify** your API key in `02_Scripts/config.py`
3. **Ensure** all dependencies are installed
4. **Open an issue** on GitHub with detailed error information

---

**🎉 Ready to enhance your French with real news?** Start with the Quick Start guide above!

**Last Updated**: June 2025 - Fully functional with 30 curated French articles ready for learning! 