// Better French - Main JavaScript File

class BetterFrenchApp {
    constructor() {
        this.currentMode = 'learner';
        this.articles = [];
        this.filteredArticles = [];
        this.displayedArticles = 0;
        this.articlesPerPage = 10;
        this.currentTooltip = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadLatestData();
        this.renderArticles();
    }

    setupEventListeners() {
        // Mode toggle - Desktop buttons
        const modeButtons = document.querySelectorAll('.mode-option');
        modeButtons.forEach(button => {
            button.addEventListener('click', (e) => this.switchMode(e.target.dataset.mode));
        });

        // Mode toggle - Mobile switcher
        const modeSwitcher = document.querySelector('.mode-switcher');
        if (modeSwitcher) {
            modeSwitcher.addEventListener('click', () => this.toggleMobileMode());
        }

        // Search functionality
        const searchInput = document.querySelector('.search-input');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));

        // Mobile collapsible search
        const searchIcon = document.querySelector('.search-icon');
        if (searchIcon) {
            searchIcon.addEventListener('click', () => this.toggleMobileSearch());
        }

        // Close search when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.closeMobileSearch();
            }
        });

        // Load more button
        const loadMoreBtn = document.getElementById('load-more');
        loadMoreBtn.addEventListener('click', () => this.loadMoreArticles());

        // Retry button
        const retryBtn = document.getElementById('retry-btn');
        retryBtn.addEventListener('click', () => this.init());

        // Summary toggles - Toggle behavior (open if closed, close if open)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.summary-toggle')) {
                const toggle = e.target.closest('.summary-toggle');
                const summaryId = toggle.getAttribute('aria-controls');
                const summaryContent = document.getElementById(summaryId);
                if (summaryContent) {
                    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
                    
                    if (isExpanded) {
                        // Currently open - close it
                        this.closeSummary(toggle, summaryContent);
                    } else {
                        // Currently closed - open it
                        this.openSummary(toggle, summaryContent);
                    }
                }
            }
        });
    }

    async loadLatestData() {
        try {
            this.showLoading(true);
            this.hideError();
            
            console.log('Starting to load data...');

            // Get the latest file from the processed_AI directory
            const latestFile = await this.getLatestProcessedFile();
            console.log('Latest file path:', latestFile);
            
            const response = await fetch(latestFile);
            console.log('Fetch response status:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`Failed to load data: ${response.status}`);
            }

            const data = await response.json();
            console.log('Data loaded successfully:', data);
            
            // Handle both automated system format (data.articles) and manual system format (data.processed_articles)
            let articles = [];
            if (data.articles) {
                // Automated system format - AI-enhanced article data
                console.log('📰 Using automated system data format');
                console.log('Raw automated articles:', data.articles);
                articles = data.articles;
                
                // Convert automated format to display format - using proper AI-enhanced fields
                articles = articles.map(article => ({
                    // Use the AI-enhanced fields correctly
                    original_article_title: article.title,
                    simplified_english_title: article.english_title || article.title,
                    simplified_french_title: article.title,
                    english_summary: article.english_summary || article.summary, // ✅ FIXED: Use proper english_summary field
                    french_summary: article.summary,  // ✅ FIXED: Use original French summary
                    original_article_link: article.link,
                    source_name: article.source_name,
                    published_date: article.published || article.added_at,  // ✅ FIXED: Use added_at if published is empty
                    image_url: article.image_url || '',
                    quality_score: article.quality_score || 7.0,
                    relevance_score: article.relevance_score || 6.0,
                    importance_score: article.importance_score || 7.0,
                    total_score: article.total_score || 20.0,
                    breaking_news: article.breaking_news || false,
                    urgency_score: article.urgency_score || 0.0,
                    explanations: article.explanations || [],  // ✅ KEEP: For any additional use
                    contextual_title_explanations: article.explanations || [],  // ✅ FIXED: Map to correct source field
                    key_vocabulary: article.key_vocabulary || [],
                    cultural_context: article.cultural_context || {}
                }));
            } else if (data.processed_articles) {
                // Manual system format - AI-enhanced data
                console.log('🤖 Using manual system AI-enhanced data format');
                console.log('Processed articles array:', data.processed_articles);
                articles = data.processed_articles;
            }
            
            console.log('Number of articles:', articles.length);
            
            this.articles = articles || [];
            this.filteredArticles = [...this.articles];
            
            console.log(`✅ Loaded ${this.articles.length} articles from ${latestFile}`);
            
            this.renderArticles();
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            console.error('Error stack:', error.stack);
            this.showError();
        } finally {
            this.showLoading(false);
        }
    }

    async getLatestProcessedFile() {
        // Use the fresh automated system data first
        const automatedDataFile = 'current_articles.json';
        
        // Check if the automated data exists first
        try {
            const response = await fetch(automatedDataFile, { method: 'HEAD' });
            if (response.ok) {
                console.log('✅ Using fresh automated system data:', automatedDataFile);
                return automatedDataFile;
            }
        } catch (error) {
            console.warn(`❌ Automated data ${automatedDataFile} not found, falling back to manual system`);
        }
        
        // Fallback to the original manual system file if automated data isn't available
        const fallbackFile = '04_Data_Output/Processed_AI/ai_processed_curated_news_data_20250531_095437_20250531_150551.json';
        console.log('⚠️ Using fallback manual system data:', fallbackFile);
        return fallbackFile;
    }

    toggleMobileMode() {
        const currentMode = this.currentMode;
        const newMode = currentMode === 'learner' ? 'native' : 'learner';
        this.switchMode(newMode);
    }

    switchMode(mode) {
        if (mode === this.currentMode) return;

        const oldMode = this.currentMode;
        this.currentMode = mode;

        // Update desktop button states
        document.querySelectorAll('.mode-option').forEach(btn => {
            const isActive = btn.dataset.mode === mode;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-checked', isActive.toString());
        });

        // Update mobile switcher
        this.updateMobileSwitcher(mode);

        // Animate mode switch
        this.animateModeSwitch(oldMode, mode);
    }

    updateMobileSwitcher(mode) {
        const modeSwitcher = document.querySelector('.mode-switcher');
        const modeIcon = modeSwitcher?.querySelector('.mode-icon');
        const modeText = modeSwitcher?.querySelector('.mode-text');
        
        if (modeSwitcher && modeIcon && modeText) {
            modeSwitcher.setAttribute('data-current-mode', mode);
            
            // Smooth transition with flip effect
            modeSwitcher.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                if (mode === 'learner') {
                    modeIcon.textContent = '🎓';
                    modeText.textContent = 'Learner';
                } else {
                    modeIcon.textContent = '🇫🇷';
                    modeText.textContent = 'Native';
                }
                
                modeSwitcher.style.transform = 'scale(1.0)';
            }, 150);
        }
    }

    animateModeSwitch(oldMode, newMode) {
        const secondaryTitles = document.querySelectorAll('.secondary-title');
        const summaryToggles = document.querySelectorAll('.summary-toggle');
        const summaryContents = document.querySelectorAll('.summary-content');

        // Collapse all expanded summaries first
        summaryContents.forEach(content => {
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                content.style.height = '0';
                content.setAttribute('aria-hidden', 'true');
            }
        });

        // Update toggle button states
        summaryToggles.forEach(toggle => {
            toggle.setAttribute('aria-expanded', 'false');
            const chevron = toggle.querySelector('.chevron');
            if (chevron) {
                chevron.classList.remove('expanded');
            }
        });

        // Fade out current content
        secondaryTitles.forEach(title => {
            title.style.opacity = '0';
        });

        summaryToggles.forEach(toggle => {
            toggle.style.opacity = '0';
        });

        // Update content after fade out
        setTimeout(() => {
            secondaryTitles.forEach((title, index) => {
                const article = this.filteredArticles[index];
                if (article) {
                    title.textContent = newMode === 'learner' 
                        ? article.simplified_english_title 
                        : article.simplified_french_title;
                }
            });

            summaryToggles.forEach((toggle, index) => {
                const article = this.filteredArticles[index];
                const summaryText = newMode === 'learner' ? 'English Summary' : 'Résumé français';
                const textLabel = toggle.querySelector('.summary-text-label');
                if (textLabel) {
                    textLabel.textContent = summaryText;
                }

                // Update the summary content for the new mode
                const summaryId = toggle.getAttribute('aria-controls');
                const summaryContent = document.getElementById(summaryId);
                if (summaryContent && article) {
                    const summaryTextContent = newMode === 'learner' 
                        ? article.english_summary 
                        : article.french_summary;
                    const summaryTextElement = summaryContent.querySelector('.summary-text');
                    if (summaryTextElement) {
                        summaryTextElement.textContent = summaryTextContent;
                    }
                }
            });

            // Fade in new content
            secondaryTitles.forEach(title => {
                title.style.opacity = '1';
            });

            summaryToggles.forEach(toggle => {
                toggle.style.opacity = '1';
            });
        }, 150);
    }

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (searchTerm === '') {
            this.filteredArticles = [...this.articles];
        } else {
            this.filteredArticles = this.articles.filter(article => 
                article.original_article_title.toLowerCase().includes(searchTerm) ||
                article.simplified_english_title.toLowerCase().includes(searchTerm) ||
                article.simplified_french_title.toLowerCase().includes(searchTerm)
            );
        }

        this.displayedArticles = 0;
        this.renderArticles();
    }

    renderArticles() {
        console.log('renderArticles called');
        console.log('this.articles.length:', this.articles.length);
        console.log('this.filteredArticles.length:', this.filteredArticles.length);
        
        const featuredContainer = document.getElementById('featured-article');
        const articlesContainer = document.getElementById('articles-container');
        const loadMoreBtn = document.getElementById('load-more');

        console.log('DOM elements found:', {
            featuredContainer: !!featuredContainer,
            articlesContainer: !!articlesContainer,
            loadMoreBtn: !!loadMoreBtn
        });

        // Clear existing content
        featuredContainer.innerHTML = '';
        articlesContainer.innerHTML = '';

        if (this.filteredArticles.length === 0) {
            console.log('No filtered articles, showing "no articles" message');
            featuredContainer.innerHTML = '<p>No articles found matching your search.</p>';
            loadMoreBtn.style.display = 'none';
            return;
        }

        console.log('Rendering articles...');
        
        // Render featured article (first article)
        const featuredArticle = this.filteredArticles[0];
        console.log('Featured article:', featuredArticle);
        featuredContainer.innerHTML = this.createArticleHTML(featuredArticle, true);

        // Render regular articles
        const articlesToShow = Math.min(this.articlesPerPage, this.filteredArticles.length - 1);
        this.displayedArticles = articlesToShow + 1; // +1 for featured
        
        console.log('Articles to show:', articlesToShow);

        for (let i = 1; i <= articlesToShow; i++) {
            const article = this.filteredArticles[i];
            const articleElement = document.createElement('article');
            articleElement.className = 'article-card';
            articleElement.innerHTML = this.createArticleHTML(article, false);
            articlesContainer.appendChild(articleElement);
        }

        // Show/hide load more button
        loadMoreBtn.style.display = this.displayedArticles < this.filteredArticles.length ? 'block' : 'none';

        // Setup article interactions
        this.setupArticleInteractions();
    }

    loadMoreArticles() {
        const articlesContainer = document.getElementById('articles-container');
        const loadMoreBtn = document.getElementById('load-more');
        
        const startIndex = this.displayedArticles;
        const endIndex = Math.min(startIndex + this.articlesPerPage, this.filteredArticles.length);

        for (let i = startIndex; i < endIndex; i++) {
            const article = this.filteredArticles[i];
            const articleElement = document.createElement('article');
            articleElement.className = 'article-card';
            articleElement.style.opacity = '0';
            articleElement.innerHTML = this.createArticleHTML(article, false);
            articlesContainer.appendChild(articleElement);

            // Fade in animation
            setTimeout(() => {
                articleElement.style.transition = 'opacity 200ms ease-in';
                articleElement.style.opacity = '1';
            }, 50);
        }

        this.displayedArticles = endIndex;
        
        // Hide load more button if all articles are displayed
        if (this.displayedArticles >= this.filteredArticles.length) {
            loadMoreBtn.style.display = 'none';
        }

        this.setupArticleInteractions();
    }

    createArticleHTML(article, isFeatured = false) {
        const secondaryTitle = this.currentMode === 'learner' 
            ? article.simplified_english_title 
            : article.simplified_french_title;
        
        const summaryText = this.currentMode === 'learner' 
            ? article.english_summary 
            : article.french_summary;
        
        const summaryLabel = this.currentMode === 'learner' 
            ? 'English Summary' 
            : 'Résumé français';

        // Extract source from the article link or use a default
        const source = this.extractSource(article.original_article_link);
        const publishedDate = this.formatDate(article.published_date);
        
        // Generate unique IDs for accessibility
        const summaryId = this.generateId();
        const collapseId = this.generateId();

        return `
            <h2 class="article-title">
                ${this.createInteractiveTitle(article.original_article_title, article.contextual_title_explanations)}
            </h2>
            <h3 class="secondary-title">${secondaryTitle}</h3>
            <button class="summary-toggle" aria-expanded="false" aria-controls="${summaryId}">
                <span class="summary-text-label">${summaryLabel}</span>
            </button>
            <div class="summary-content" id="${summaryId}" aria-hidden="true">
                <p class="summary-text">${summaryText}</p>
            </div>
            <div class="article-meta">${source} | ${publishedDate}</div>
            <button class="collapse-button" id="${collapseId}" aria-label="Close summary" style="display: none;">—</button>
        `;
    }

    extractSource(url) {
        if (!url) return 'Unknown Source';
        
        try {
            const urlObj = new URL(url);
            const hostname = urlObj.hostname.toLowerCase();
            
            // Map common domains to readable names
            const sourceMap = {
                'www.lexpress.fr': 'L\'Express',
                'lexpress.fr': 'L\'Express',
                'www.lemonde.fr': 'Le Monde',
                'lemonde.fr': 'Le Monde',
                'www.france24.com': 'France 24',
                'france24.com': 'France 24',
                'www.rfi.fr': 'RFI',
                'rfi.fr': 'RFI',
                'www.liberation.fr': 'Libération',
                'liberation.fr': 'Libération'
            };
            
            return sourceMap[hostname] || hostname.replace('www.', '').split('.')[0];
        } catch (error) {
            return 'Unknown Source';
        }
    }

    createInteractiveTitle(title, explanations) {
        if (!explanations || explanations.length === 0) {
            return title;
        }

        // Sort explanations by word length (longest first) to match phrases before individual words
        const sortedExplanations = explanations.slice().sort((a, b) => 
            b.original_word.length - a.original_word.length
        );

        // Track all matches with their positions
        let matches = [];
        
        // Find all potential matches
        sortedExplanations.forEach(exp => {
            const originalWord = exp.original_word;
            
            // Create regex to find the word/phrase (case insensitive, whole word boundaries)
            const isMultiWord = originalWord.includes(' ');
            let regexPattern;
            
            if (isMultiWord) {
                // For phrases like "sur la table", match the exact sequence
                regexPattern = originalWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            } else {
                // For single words, use word boundaries
                regexPattern = '\\b' + originalWord.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b';
            }
            
            const regex = new RegExp(regexPattern, 'gi');
            let match;
            
            // Find all matches for this explanation
            while ((match = regex.exec(title)) !== null) {
                matches.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    text: match[0],
                    explanation: exp,
                    length: match[0].length
                });
            }
        });

        // Sort matches by position (earliest first)
        matches.sort((a, b) => a.start - b.start);

        // Remove overlapping matches (keep longer/earlier ones)
        let filteredMatches = [];
        for (let i = 0; i < matches.length; i++) {
            const currentMatch = matches[i];
            let hasOverlap = false;
            
            // Check if this match overlaps with any already accepted match
            for (let j = 0; j < filteredMatches.length; j++) {
                const existingMatch = filteredMatches[j];
                
                // Check for overlap: if current match starts before existing ends and ends after existing starts
                if (currentMatch.start < existingMatch.end && currentMatch.end > existingMatch.start) {
                    hasOverlap = true;
                    break;
                }
            }
            
            // Only add if no overlap
            if (!hasOverlap) {
                filteredMatches.push(currentMatch);
            }
        }

        // Sort filtered matches by position (latest first for replacement)
        filteredMatches.sort((a, b) => b.start - a.start);

        // Apply matches from end to beginning to preserve positions
        let result = title;
        filteredMatches.forEach(match => {
            const beforeMatch = result.substring(0, match.start);
            const afterMatch = result.substring(match.end);
            const wrappedMatch = `<span class="french-word" data-word="${encodeURIComponent(JSON.stringify(match.explanation))}">${match.text}</span>`;
            
            result = beforeMatch + wrappedMatch + afterMatch;
        });

        return result;
    }

    // Advanced word normalization for better matching
    normalizeWord(word) {
        if (!word) return '';
        
        return word
            .toLowerCase()
            // Remove all punctuation and special characters
            .replace(/[^\w\s\u00C0-\u017F]/g, '')
            // Normalize accented characters
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            // Remove extra whitespace
            .trim();
    }

    setupArticleInteractions() {
        // Article card hover to open summaries
        document.querySelectorAll('.article-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                const summaryToggle = card.querySelector('.summary-toggle');
                const summaryContent = card.querySelector('.summary-content');
                if (summaryToggle && summaryContent) {
                    this.openSummary(summaryToggle, summaryContent);
                }
            });
        });

        // Collapse button - Click to close
        document.addEventListener('click', (e) => {
            if (e.target.closest('.collapse-button')) {
                const card = e.target.closest('.article-card');
                const summaryToggle = card.querySelector('.summary-toggle');
                const summaryContent = card.querySelector('.summary-content');
                if (summaryToggle && summaryContent) {
                    this.closeSummary(summaryToggle, summaryContent);
                }
            }
        });

        // Enhanced French word interactions with focus management
        this.setupFrenchWordInteractions();
    }

    setupFrenchWordInteractions() {
        document.querySelectorAll('.french-word').forEach(word => {
            word.setAttribute('tabindex', '0');
            word.setAttribute('role', 'button');
            
            // Desktop: hover events
            word.addEventListener('mouseenter', (e) => {
                this.setActiveWord(e.target);
            });
            
            word.addEventListener('mouseleave', (e) => {
                this.clearActiveWord(e.target);
            });
            
            // Mobile: touch/click events
            word.addEventListener('touchstart', (e) => {
                e.preventDefault(); // Prevent mouse events on mobile
                this.setActiveWord(e.target);
            });
            
            word.addEventListener('click', (e) => {
                // Toggle active state on click (useful for mobile)
                if (e.target.classList.contains('active')) {
                    this.clearActiveWord(e.target);
                } else {
                    this.setActiveWord(e.target);
                }
            });
            
            // Keyboard navigation
            word.addEventListener('focus', (e) => {
                this.setActiveWord(e.target);
            });
            
            word.addEventListener('blur', (e) => {
                this.clearActiveWord(e.target);
            });
        });
        
        // Clear active word when clicking outside
        document.addEventListener('touchstart', (e) => {
            if (!e.target.closest('.french-word')) {
                this.clearAllActiveWords();
            }
        });
        
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.french-word')) {
                this.clearAllActiveWords();
            }
        });
    }

    setActiveWord(wordElement) {
        // Clear any other active words in the same title
        const titleContainer = wordElement.closest('.article-title');
        if (titleContainer) {
            titleContainer.querySelectorAll('.french-word').forEach(w => {
                w.classList.remove('active');
            });
            
            // Set the new active word
            wordElement.classList.add('active');
            
            // Add fallback class for browsers without :has() support
            titleContainer.classList.add('has-active-word');
        }
    }

    clearActiveWord(wordElement) {
        const titleContainer = wordElement.closest('.article-title');
        if (titleContainer) {
            wordElement.classList.remove('active');
            
            // Check if any other words are still active
            const hasActiveWords = titleContainer.querySelectorAll('.french-word.active').length > 0;
            if (!hasActiveWords) {
                titleContainer.classList.remove('has-active-word');
            }
        }
    }

    clearAllActiveWords() {
        document.querySelectorAll('.french-word.active').forEach(word => {
            word.classList.remove('active');
        });
        document.querySelectorAll('.article-title.has-active-word').forEach(title => {
            title.classList.remove('has-active-word');
        });
    }

    openSummary(toggleButton, summaryContent) {
        const chevron = toggleButton.querySelector('.chevron');
        const collapseButton = toggleButton.closest('.article-card').querySelector('.collapse-button');
        const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
        
        // Only open if not already expanded
        if (isExpanded) return;

        // Update attributes to expanded state
        toggleButton.setAttribute('aria-expanded', 'true');
        summaryContent.setAttribute('aria-hidden', 'false');

        // Toggle classes and animations
        if (chevron) chevron.classList.add('expanded');
        summaryContent.classList.add('expanded');

        // Show collapse button
        if (collapseButton) {
            collapseButton.style.display = 'flex';
        }

        // Handle height animation for opening
        summaryContent.style.height = 'auto';
        const height = summaryContent.scrollHeight;
        summaryContent.style.height = '0';
        summaryContent.offsetHeight; // Force reflow
        summaryContent.style.height = height + 'px';
        
        // Set back to auto after animation
        setTimeout(() => {
            if (summaryContent.classList.contains('expanded')) {
                summaryContent.style.height = 'auto';
            }
        }, 200);
    }

    closeSummary(toggleButton, summaryContent) {
        const chevron = toggleButton.querySelector('.chevron');
        const collapseButton = toggleButton.closest('.article-card').querySelector('.collapse-button');
        const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
        
        // Only close if currently expanded
        if (!isExpanded) return;

        // Update attributes to collapsed state
        toggleButton.setAttribute('aria-expanded', 'false');
        summaryContent.setAttribute('aria-hidden', 'true');

        // Toggle classes and animations
        if (chevron) chevron.classList.remove('expanded');
        summaryContent.classList.remove('expanded');

        // Hide collapse button
        if (collapseButton) {
            collapseButton.style.display = 'none';
        }

        // Handle height animation for closing
        const height = summaryContent.scrollHeight;
        summaryContent.style.height = height + 'px';
        summaryContent.offsetHeight; // Force reflow
        summaryContent.style.height = '0';
    }

    formatDate(dateString) {
        if (!dateString || dateString.trim() === '') {
            return 'May 31, 2025'; // Default to the date in the filename since published dates are empty
        }
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'May 31, 2025';
            }
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            return 'May 31, 2025';
        }
    }

    generateId() {
        return 'summary-' + Math.random().toString(36).substr(2, 9);
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.setAttribute('aria-hidden', (!show).toString());
        loading.style.display = show ? 'flex' : 'none';
    }

    showError() {
        const error = document.getElementById('error-message');
        error.setAttribute('aria-hidden', 'false');
        error.style.display = 'flex';
    }

    hideError() {
        const error = document.getElementById('error-message');
        error.setAttribute('aria-hidden', 'true');
        error.style.display = 'none';
    }

    toggleMobileSearch() {
        const searchInput = document.querySelector('.search-input');
        const searchIcon = document.querySelector('.search-icon');
        
        if (searchInput.classList.contains('expanded')) {
            this.closeMobileSearch();
        } else {
            this.openMobileSearch();
        }
    }

    openMobileSearch() {
        const searchInput = document.querySelector('.search-input');
        const searchIcon = document.querySelector('.search-icon');
        
        searchInput.classList.add('expanded');
        searchIcon.classList.add('active');
        
        // Focus the input after animation
        setTimeout(() => {
            searchInput.focus();
        }, 200);
    }

    closeMobileSearch() {
        const searchInput = document.querySelector('.search-input');
        const searchIcon = document.querySelector('.search-icon');
        
        if (searchInput && searchIcon) {
            searchInput.classList.remove('expanded');
            searchIcon.classList.remove('active');
            searchInput.blur();
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BetterFrenchApp();
}); 