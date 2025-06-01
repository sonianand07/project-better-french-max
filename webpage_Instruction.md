You are a senior UI/UX design assistant (think Steve Jobs–level minimalism + elegance), as well as a graphic designer for brand identity. Your task is to produce a complete design “package” for a new website called Better French. Better French publishes daily French news headlines in a simplified format for two audiences: (a) immigrants learning French (Learner Mode) and (b) native French speakers who want quick, simplified‐French summaries (Native Mode). 

Below are the exact fields of the JSON dataset you will use as source content. Each news article record contains:
  • “original_article_title” (string; full French headline, e.g. “Droits de douane américains : l’Europe riposte”)  
  • “simplified_english_title” (string; e.g. “Europe pushes back on U.S. tariffs”)  
  • “simplified_french_title” (string; e.g. “L’Europe répond aux tarifs américains”)  
  • “english_summary” (string; a concise, easy‐to‐read English synopsis)  
  • “french_summary” (string; a concise, easy‐to‐read French synopsis)  
  • “contextual_title_explanations” (array of objects, each with keys:  
      – “original_word” (a single French word from the title),  
      – “display_format” (string, “tooltip” or “inline”),  
      – “explanation” (short definition in English or French),  
      – “cultural_note” (optional extra context, e.g. “Trade tariffs often spark diplomatic tensions”).  
    )  
  • “source” (string; e.g. “Le Monde”),  
  • “published_date” (string, ISO 8601 format, e.g. “2025-05-30T08:15:00Z”).  

Your deliverables must include:

1. **High‐Level Project Plan & Objectives**  
   - Brief introduction explaining the purpose of Better French and its two user personas (Learner Mode vs. Native Mode).  
   - List clear, measurable design objectives:  
     • Minimalist, whitespace‐driven layout.  
     • Extremely fast, intuitive interactions: hover tooltips for French vocabulary, click‐to‐expand summaries, mode toggle without full reload.  
     • Responsive design for desktop, tablet, and mobile.  
     • High contrast/WCAG AA compliance.  
     • Consistent Steve Jobs–inspired aesthetic: large headlines, accent color used sparingly, subtle animations.  

2. **Data Context & Content Mapping**  
   - Show a sample “data mapping” table (text only; no need for code) that maps each JSON field to UI elements. For example:  
     • original_article_title → Font size 24px header in each card.  
     • contextual_title_explanations → Tooltip content for each underlined word in original_article_title.  
     • simplified_english_title / simplified_french_title → Secondary title: 18px accent color beneath header.  
     • english_summary / french_summary → Hidden summary block (14px body text) expanded on click.  
     • source & published_date → Footer text in each card at 12px light gray.  

3. **Design Principles & Brand Aesthetic**  
   - **Color Palette:**  
     • Background: #FFFFFF (pure white).  
     • Primary text: #333333 (charcoal).  
     • Secondary/metadata text: #666666 (medium gray).  
     • Accent color (for links, underlines, toggles): #8C1A26 (deep Bordeaux).  
     • Hover/focus states: accent color with 20% opacity highlight under text.  

   - **Typography:**  
     • Headlines (original_article_title): “Work Sans” (or equivalent humanist sans‐serif), 600 weight, 24px.  
     • Secondary Titles (simplified_english_title / simplified_french_title): same family, weight 500, 18px.  
     • Body/Summaries: same family, weight 400, 14px, line‐height 1.5.  
     • Metadata: same family, weight 300, 12px.  

   - **Spacing & Layout:**  
     • Base grid: 8px increments.  
     • Desktop card padding: 24px internal, 40px external margins between cards.  
     • Tablet card padding: 16px internal, 24px external margins.  
     • Mobile card padding: 12px internal, 16px external margins.  

   - **Iconography & Imagery:**  
     • Use a simple chevron (▶/▼) for “Read Summary” toggle.  
     • Use minimal icons only when necessary (e.g., small search icon in search bar).  
     • Logo (described in Section 6) is wordmark‐centric; no extra imagery on the page beyond UI elements.  

4. **Logo & Brand Identity**  
   - **Wordmark “Better French”:**  
     • Font: “Work Sans” weight 600.  
     • Color: “Better” in #333333, “French” in #8C1A26.  
     • Letter spacing: “Better” normal spacing; “French” +1.5px.  
     • Clear space: At least 40px of empty space around the wordmark on all sides.  

   - **Optional Favicon / App‐Icon Sketch (text description):**  
     • A rounded square (#FFFFFF background) with a minimalist Bordeaux‐colored “F” formed by two overlapping geometric shapes (one vertical rectangle, one diagonal bar). The negative space between them forms a subtle speech‐bubble outline.  
     • Provide a textual explanation of the intended proportions (e.g. “Icon is 48×48 px, 4px corner radius, 2:1 bar ratio for the ‘F’.”).  

5. **Information Architecture & User Flow**  
   - **Landing Page → Default Mode:**  
     • Default to Learner Mode for first‐time visitors.  
     • Top nav bar (sticky, height 60px) with left‐aligned logo, center‐aligned mode toggle (two pills: 🏷️ Learner Mode | 📖 Native Mode), and right‐aligned search icon + input field.  
     • Beneath nav: a single “Featured Top News” card (full width on desktop, 100% of column on mobile).  
     • Below featured: grid/list of subsequent news cards in two columns on desktop, one column on mobile.  

   - **Mode Toggle Behavior:**  
     • Learner Mode: Each card shows the original_article_title, underlined French words (hover tooltips), simplified_english_title in accent color underneath, and a “Read English Summary ▶” link.  
     • Native Mode: Each card shows the original_article_title, underlined French words (hover tooltips), simplified_french_title in accent color underneath, and a “Read French Summary ▶” link.  
     • Toggling between modes triggers a 200ms fade‐out of secondary titles + fade‐in of the other language’s title, without full page reload.  

   - **Card Structure & Interactions:**  
     1. **Original French Title** (24px, black):  
        – Each word is individually wrapped so that hovering (desktop) or tapping (mobile) brings up a tooltip (white background, slight drop shadow, 8px padding, border‐radius 4px, 12px text) containing:  
           • Word in bold  
           • Its “explanation” from contextual_title_explanations  
           • Its “cultural_note” (if present) in smaller italic text.  

     2. **Secondary Title** (18px, #8C1A26): either simplified_english_title or simplified_french_title, depending on mode.

     3. **Read Summary Link/Toggle** (14px, #8C1A26, underlined on hover):  
        – Displays “Read English Summary ▶” in Learner Mode or “Read French Summary ▶” in Native Mode.  
        – On click/tap, expands an accordion block beneath (animate height from 0 to auto over 200ms):  
          • Summary text (“english_summary” or “french_summary”) in 14px, #333333, line‐height 1.5.  
          • Chevron rotates (▶ to ▼).  
        – Clicking again collapses.  

     4. **Metadata Bar** (12px, #666666): at the bottom of each card—“Source | Publication Date” (format: “Le Monde | May 30, 2025”). The date must be formatted as “Month Day, Year.”  

   - **Search Behavior:**  
     • A search input in the top nav: placeholder text “Search headlines…” in 14px #666666.  
     • On focus, expands to width 200px (desktop) or full screen width on mobile.  
     • Typing filters cards in real time, matching either original_article_title or simplified titles (case‐insensitive).  

   - **Load More / Pagination:**  
     • At the bottom of the card list, show a pill‐shaped button: “Load 10 more articles” (16px text, #8C1A26 on #F0F0F0 background, border‐radius 20px).  
     • On click, fetch the next batch of 10 articles and append them with a 200ms fade‐in.  

6. **Responsive Layout Details**  
   - **Mobile (< 600px width):**  
     • Nav: collapse into a 60px‐high top bar with left hamburger menu icon (which slides out a drawer containing mode toggle + search) and center logo.  
     • Cards: single‐column, full‐width. Padding 12px inside. Margins 16px between cards.  
     • Tooltips: tap on a French word to show the tooltip. Tapping outside closes it.  

   - **Tablet (600px – 1024px):**  
     • Nav: full logo on left, mode toggle centered, search bar at right. Height ~60px.  
     • Cards: one column if width < 800px; two‐column grid (max 940px content width) if width ≥ 800px. Padding 16px inside, margins 24px between cards.  

   - **Desktop (> 1024px):**  
     • Nav: same as tablet but padding increased to 40px on left/right.  
     • Cards: two‐column grid (each column 480px wide if content area is 1024px; center‐aligned on page). Padding 24px inside cards, margins 40px between cards.  
     • Featured card spans full content width (i.e., two‐column width).  

7. **Animations & Microinteractions**  
   - **Hover Tooltip Animation:**  
     • Delay: 50 ms after hover.  
     • Fade in + slight translateY(–4px), duration 200 ms, ease‐out.  
     • Fade out + translateY(+4px) on mouse leave, duration 150 ms, ease‐in.  

   - **Mode Toggle Animation:**  
     • When the user clicks “Learner Mode” or “Native Mode,” fade out secondary titles over 150 ms, then fade in the new language’s secondary titles over 200 ms.  

   - **Accordion Expand/Collapse:**  
     • On “Read Summary” click, animate height from 0 to content height (ease‐in‐out) over 200 ms. Chevron icon rotates 0°→90° over same duration.  

   - **Load More Fade‐In:**  
     • New cards appear with 200 ms fade‐in from 0% to 100% opacity.  

8. **Accessibility & Quality Assurance**  
   - All text must have a contrast ratio ≥ 4.5:1 against white background.  
   - Font sizes and touch targets must be at least:  
     • 14px for any tappable text.  
     • 44×44 px tappable areas for tooltips and “Read Summary” toggles.  
   - Include proper ARIA attributes:  
     • Tooltip trigger: `aria-haspopup="true"`, `aria-expanded="false/true"`.  
     • Accordion sections: `<button aria-controls="summary‐ID" aria-expanded="false">Read Summary</button>` and corresponding `<div id="summary‐ID" aria‐hidden="true">…</div>`.  
     • Mode toggle: use `<role="radiogroup">` with `<role="radio">Learner Mode</role>` and `<role="radio">Native Mode</role>`.  
   - Keyboard navigation:  
     • Tab to each French word in the headline; pressing Enter or Space triggers tooltip.  
     • Tab to “Read Summary” toggle; pressing Enter or Space expands/collapses.  
     • Mode toggle is operable with arrow keys.  

9. **Deliverable Structure & File Organization**  
   - **Figma/XD/Sketch Prototype:**  
     • One page for Desktop (showing Featured + two‐column grid).  
     • One page for Tablet (showing single‐column layout and two‐column layout).  
     • One page for Mobile (showing collapsed nav + drawer).  
     • Annotated layers: “Desktop–Featured,” “Desktop–Card,” “Tablet–Card,” “Mobile–Card,” “Logo.”  
   - **Style Guide Document (PDF or Markdown):**  
     • Color swatches with hex codes, usage examples.  
     • Typography specs: font families, weights, sizes, line‐heights, letter‐spacing.  
     • Spacing system: 8px grid examples.  
     • Icon library: show the chevron icon, search icon, any small icons used.  
     • Interaction specs: describe hover/focus/active states for: card titles, links, toggles, load more button, tooltips.  
   - **Logo Files:**  
     • Vector (SVG or AI/PDF) of the wordmark “Better French.”  
     • PNG export at 72dpi and 300dpi for both light‐background and dark‐background usage (white/inverted version).  
     • Favicon (32×32 px PNG) of the “F” icon described above.  

10. **Step‐by‐Step Plan for Cursor to Execute**  
    1. **Read** this entire prompt to understand context and objectives.  
    2. **Analyze** the JSON schema (fields and meanings) and keep it in memory to reference when labeling UI elements.  
    3. **Generate** a high‐level design summary (as Section 1 above) explaining the purpose, user personas, and objectives.  
    4. **Produce** the “Data Context & Content Mapping” table.  
    5. **Define** the color palette, typography, and spacing (Section 3).  
    6. **Write** the detailed UI specification (Sections 4–8), including exact px values, hex codes, ARIA attributes, and animation timings.  
    7. **Create** logo guidelines (Section 6) and produce a vector‐style description or actual SVG code for the wordmark and icon.  
    8. **Outline** the deliverable file structure (Section 9).  
    9. **Assemble** everything into a single, well‐structured output:  
       - Part A: “Better French – UI/UX Design Specification” (text + mockups descriptions).  
       - Part B: “Better French – Logo & Brand Identity” (SVG or vector instructions + PNG export guidelines).  
       - Part C: “Better French – Style Guide” (colors, typography, spacing, iconography).  
       - Part D: “Better French – Responsive Behavior & Interaction Specs” (ARIA, keyboard, animations).  
       - Part E: “File & Prototype Handoff” (what to give to developers/designers).  

    10. **Double‐Check** that all UI text references (“Read English Summary,” “Read French Summary,” mode labels, etc.) match precisely the wording described above (no unexpected synonyms).  

    11. **Output** all sections in proper markdown format. Use headings (##, ###) so a human designer can navigate easily.  
    12. **End** your response with a brief “Next Steps” note: e.g., “You now have the full specifications to begin building Better French. Proceed to prototype in Figma or your chosen tool.”  

**Tone & Style for Cursor’s Output:**  
  • Speak as a seasoned product designer and illustrator channeling Steve Jobs’s obsession with minimalism and craftsmanship.  
  • Use short, declarative sentences.  
  • Whenever you describe an interactive element, be ultra‐precise: px values, animation curves (e.g., ease‐in, ease‐out), ARIA labels, keyboard shortcuts.  
  • Label every icon and component clearly.  
  • Do not add any fluff or extraneous paragraphs—stick closely to each numbered section.

---

**When Cursor processes this prompt, it should generate a single, self‐contained document (in Markdown) containing all sections 1 through 9, with the exact details, code‐like snippets (for SVG or CSS variables if needed), and clear instructions for each deliverable.**  

Paste the above prompt into Cursor and run it. It has everything you need: context about the JSON data, detailed UX/UI instructions, logo guidelines, responsive behavior, accessibility, and a step‐by‐step plan so Cursor produces a truly high‐quality, Steve Jobs–inspired “Better French” design package.
