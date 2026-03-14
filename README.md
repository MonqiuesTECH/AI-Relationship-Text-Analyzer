# AI Relationship Text Analyzer

Paste any text conversation and get an AI-powered breakdown of communication patterns.

## Features

**Core Analysis**
- 6 Communication Style Scores (0–10): Emotional Availability, Effort Level, Warmth, Respectfulness, Consistency, Clarity of Intent
- 6 Behavior Signals (%): Mixed Signals, Genuine Interest, Emotional Investment, Avoidant Communication, Flirtation Level, Ghosting Risk

**10 Bonus Deep Signals**
- Initiation Ratio, Question Reciprocity, Emoji Expressiveness, Response Length Symmetry
- Topic Breadth, Apology & Accountability, Future Planning Language, Memory Signals, Dry Response Ratio, Affirmation Frequency

**Output**
- Green / Yellow / Red Flags
- Relationship Dynamic Summary
- Communication Archetype Label (e.g. "The Slow Burner")
- 3 Actionable Advice Points
- Full JSON export

## Setup & Launch

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Usage

1. Enter your Anthropic API key in the sidebar (get one at https://console.anthropic.com)
2. Paste any conversation (iMessage, WhatsApp, Instagram DMs, etc.)
3. Click "Analyze Conversation →"

## Notes

- Requires an Anthropic API key (uses `claude-opus-4-5`)
- For reflection and entertainment only — not a psychological diagnostic tool
- Works best with 10+ messages for meaningful pattern detection
