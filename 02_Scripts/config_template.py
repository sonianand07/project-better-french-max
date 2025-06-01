import os

# Configuration for the AI Processor
# 
# 🔑 SETUP INSTRUCTIONS:
# 1. Copy this file to 'config.py' in the same directory
# 2. Replace "your_openrouter_api_key_here" with your actual OpenRouter API key
# 3. Get your API key from: https://openrouter.ai/keys
#
# ⚠️  IMPORTANT: Never commit config.py to version control!
#     It's already in .gitignore to protect your API key.

# IMPORTANT: Replace with your actual OpenRouter API key
API_KEY = "your_openrouter_api_key_here"

# The chosen LLM model (you can change this if needed)
MODEL_NAME = "nousresearch/nous-hermes-2-mixtral-8x7b-dpo"

# OpenRouter API base URL (don't change this)
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# You can add other configurations here later if needed 