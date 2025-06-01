#!/bin/bash

# French News Scraper Environment Setup Script
echo "🇫🇷 French News Scraper Environment Manager"
echo "============================================="

# Function to create environment
create_env() {
    echo "Creating virtual environment..."
    python3 -m venv 06_Environment/french_news_env
    echo "✅ Virtual environment created"
}

# Function to activate environment
activate_env() {
    echo "Activating virtual environment..."
    source 06_Environment/french_news_env/bin/activate
    echo "✅ Virtual environment activated"
}

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    pip install -r 03_Configuration/requirements.txt
    echo "✅ Dependencies installed"
}

# Function to run scraper
run_scraper() {
    echo "Running French news scraper..."
    cd 02_Scripts
    python french_news_scraper.py
    cd ..
}

# Function to run auto-cleanup pipeline
run_auto_cleanup() {
    echo "Running auto-cleanup pipeline (fresh 24h data)..."
    cd 02_Scripts
    python french_news_pipeline_auto_cleanup.py
    cd ..
}

# Check if environment exists
if [ ! -d "06_Environment/french_news_env" ]; then
    echo "❌ Virtual environment not found. Creating..."
    create_env
fi

# Main menu
echo ""
echo "Choose an option:"
echo "1) Activate environment and install dependencies"
echo "2) Run scraper only"
echo "3) Run complete pipeline (old - keeps raw data)"
echo "4) Run AUTO-CLEANUP pipeline (fresh 24h data) ⭐ RECOMMENDED"
echo "5) Setup everything (environment + dependencies)"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        activate_env
        install_deps
        echo "🎉 Ready to use! Now you can run python scripts."
        ;;
    2)
        activate_env
        run_scraper
        ;;
    3)
        activate_env
        echo "Running complete pipeline..."
        cd 02_Scripts
        python french_news_pipeline.py
        cd ..
        ;;
    4)
        activate_env
        echo "🔄 Running AUTO-CLEANUP pipeline for fresh content..."
        run_auto_cleanup
        ;;
    5)
        create_env
        activate_env
        install_deps
        echo "🎉 Complete setup finished!"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac 