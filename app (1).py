import streamlit as st
import anthropic
import json
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Relationship Text Analyzer",
    page_icon="💬",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background: #0f0f0f; }

h1, h2, h3 { font-family: 'DM Serif Display', serif; }

/* Hero */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    font-weight: 400;
    color: #f5f0e8;
    line-height: 1.15;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-size: 1rem;
    color: #888;
    margin-bottom: 2rem;
}

/* Section labels */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.6rem;
    margin-top: 1.6rem;
}

/* Score cards */
.score-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 1.2rem;
}
.score-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 14px 16px;
}
.score-label {
    font-size: 0.72rem;
    color: #777;
    margin-bottom: 4px;
}
.score-value {
    font-size: 1.7rem;
    font-weight: 500;
    color: #f5f0e8;
    line-height: 1;
}
.score-bar-bg {
    height: 3px;
    background: #2a2a2a;
    border-radius: 2px;
    margin-top: 8px;
}
.score-bar-fill {
    height: 3px;
    border-radius: 2px;
}

/* Signal cards */
.signal-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 1.2rem;
}
.signal-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 14px 16px;
}

/* Flag cards */
.flags-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 1.2rem;
}
.flag-card {
    border-radius: 12px;
    padding: 14px 16px;
}
.flag-card.green { background: #0d1f0f; border: 1px solid #1a3a1e; }
.flag-card.yellow { background: #1f1800; border: 1px solid #3a2e00; }
.flag-card.red { background: #1f0d0d; border: 1px solid #3a1a1a; }
.flag-head { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }
.flag-card.green .flag-head { color: #4caf6e; }
.flag-card.yellow .flag-head { color: #d4a017; }
.flag-card.red .flag-head { color: #d45757; }
.flag-item { font-size: 0.78rem; line-height: 1.5; margin-bottom: 5px; }
.flag-card.green .flag-item { color: #8ecf9e; }
.flag-card.yellow .flag-item { color: #c9a84c; }
.flag-card.red .flag-item { color: #c98c8c; }

/* Archetype pill */
.archetype-pill {
    display: inline-block;
    background: #1e1a2e;
    border: 1px solid #3a3260;
    color: #a89fd4;
    font-size: 0.82rem;
    font-weight: 500;
    border-radius: 20px;
    padding: 5px 16px;
    margin-bottom: 12px;
}

/* Summary and advice */
.summary-box {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #4a4080;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    font-size: 0.9rem;
    color: #ccc;
    line-height: 1.7;
    margin-bottom: 1rem;
}
.advice-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 10px;
}
.advice-num {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #1a1e2e;
    border: 1px solid #2a3460;
    color: #7a8ad4;
    font-size: 0.7rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.advice-text {
    font-size: 0.85rem;
    color: #aaa;
    line-height: 1.6;
}
.disclaimer {
    font-size: 0.72rem;
    color: #555;
    border-top: 1px solid #222;
    padding-top: 12px;
    margin-top: 1.5rem;
    line-height: 1.6;
}

/* Sticker */
.sticker {
    font-size: 0.75rem;
    color: #555;
    text-align: center;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert AI communication pattern analyst. A user will paste a conversation (text messages, WhatsApp, iMessage, Instagram DMs, etc.) and you will analyze it.

IMPORTANT RULES:
- Do NOT diagnose psychological disorders.
- Frame ALL insights as communication patterns and behavioral signals only.
- Be balanced, neutral, and non-judgmental.
- All scores are float 0.0–10.0. All percentages are int 0–100.

You MUST respond ONLY with a single valid JSON object. No preamble, no markdown, no explanation outside the JSON.

The JSON must match this exact schema:
{
  "communication_style_scores": {
    "emotional_availability": float,
    "effort_level": float,
    "warmth": float,
    "respectfulness": float,
    "consistency": float,
    "clarity_of_intent": float
  },
  "behavior_signals": {
    "mixed_signals_pct": int,
    "avoidant_communication_pct": int,
    "genuine_interest_pct": int,
    "emotional_investment_pct": int,
    "flirtation_level_pct": int,
    "ghosting_risk_pct": int
  },
  "bonus_signals": {
    "initiation_ratio_pct": int,
    "question_reciprocity_pct": int,
    "emoji_expressiveness": float,
    "response_length_symmetry_pct": int,
    "topic_breadth_score": float,
    "apology_accountability_pct": int,
    "future_planning_language_pct": int,
    "memory_signals_count": int,
    "dry_response_ratio_pct": int,
    "affirmation_frequency_pct": int
  },
  "green_flags": [string, ...],
  "yellow_flags": [string, ...],
  "red_flags": [string, ...],
  "archetype": string,
  "archetype_reason": string,
  "summary": string,
  "actionable_advice": [string, string, string],
  "disclaimer": "This analysis is for personal reflection and entertainment only. It is not a psychological assessment or substitute for professional advice."
}

Archetypes to choose from (pick the single best fit):
The Inconsistent Texter, The Slow Burner, The Curious Flirt, The Busy Avoider,
The Direct Communicator, The Emotional Wallflower, The Overcommunicator,
The Cautious Opener, The Reciprocal Partner, The Distant Admirer.

Analyze the OTHER person in the conversation (not the user who submitted it — infer who is who from context). If unclear, analyze the most prominent non-submitter party.
"""

# ── Score color helper ─────────────────────────────────────────────────────────
def score_color(val, max_val=10):
    ratio = val / max_val
    if ratio >= 0.7:
        return "#4caf6e"
    elif ratio >= 0.45:
        return "#d4a017"
    else:
        return "#d45757"

def pct_color(val):
    return score_color(val, 100)

# ── Render score grid ──────────────────────────────────────────────────────────
def render_scores(scores: dict):
    labels = {
        "emotional_availability": "Emotional Availability",
        "effort_level": "Effort Level",
        "warmth": "Warmth",
        "respectfulness": "Respectfulness",
        "consistency": "Consistency",
        "clarity_of_intent": "Clarity of Intent",
    }
    cards = ""
    for key, label in labels.items():
        val = scores.get(key, 0)
        color = score_color(val)
        pct = int((val / 10) * 100)
        cards += f"""
        <div class="score-card">
            <div class="score-label">{label}</div>
            <div class="score-value">{val:.1f}</div>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%;background:{color}"></div></div>
        </div>"""
    st.markdown(f'<div class="score-grid">{cards}</div>', unsafe_allow_html=True)

# ── Render behavior signals ────────────────────────────────────────────────────
def render_signals(signals: dict):
    labels = {
        "mixed_signals_pct": ("Mixed Signals", False),
        "genuine_interest_pct": ("Genuine Interest", True),
        "emotional_investment_pct": ("Emotional Investment", True),
        "avoidant_communication_pct": ("Avoidant Communication", False),
        "flirtation_level_pct": ("Flirtation Level", None),
        "ghosting_risk_pct": ("Ghosting Risk", False),
    }
    cards = ""
    for key, (label, positive) in labels.items():
        val = signals.get(key, 0)
        if positive is True:
            color = pct_color(val)
        elif positive is False:
            color = pct_color(100 - val)
        else:
            color = "#7a8ad4"
        cards += f"""
        <div class="signal-card">
            <div class="score-label">{label}</div>
            <div class="score-value" style="font-size:1.5rem;color:{color}">{val}%</div>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{val}%;background:{color}"></div></div>
        </div>"""
    st.markdown(f'<div class="signal-grid">{cards}</div>', unsafe_allow_html=True)

# ── Render bonus signals ───────────────────────────────────────────────────────
def render_bonus(bonus: dict):
    labels = {
        "initiation_ratio_pct": "Initiation Ratio",
        "question_reciprocity_pct": "Question Reciprocity",
        "emoji_expressiveness": "Emoji Expressiveness",
        "response_length_symmetry_pct": "Response Length Symmetry",
        "topic_breadth_score": "Topic Breadth",
        "apology_accountability_pct": "Apology & Accountability",
        "future_planning_language_pct": "Future Planning Language",
        "memory_signals_count": "Memory Signals (count)",
        "dry_response_ratio_pct": "Dry Response Ratio",
        "affirmation_frequency_pct": "Affirmation Frequency",
    }
    cards = ""
    for key, label in labels.items():
        val = bonus.get(key, 0)
        if key == "emoji_expressiveness" or key == "topic_breadth_score":
            display = f"{val:.1f}"
            bar_pct = int((val / 10) * 100)
            color = score_color(val)
        elif key == "memory_signals_count":
            display = str(val)
            bar_pct = min(int(val * 20), 100)
            color = "#7a8ad4"
        else:
            display = f"{val}%"
            bar_pct = val
            color = pct_color(val) if key not in ("dry_response_ratio_pct",) else pct_color(100 - val)
        cards += f"""
        <div class="signal-card">
            <div class="score-label">{label}</div>
            <div class="score-value" style="font-size:1.4rem;color:{color}">{display}</div>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{bar_pct}%;background:{color}"></div></div>
        </div>"""
    st.markdown(f'<div class="signal-grid">{cards}</div>', unsafe_allow_html=True)

# ── Render flags ───────────────────────────────────────────────────────────────
def render_flags(green, yellow, red):
    def items_html(items, cls):
        return "".join(f'<div class="flag-item">{"✦"} {i}</div>' for i in items) if items else f'<div class="flag-item" style="opacity:.4">None detected</div>'

    html = f"""
    <div class="flags-grid">
        <div class="flag-card green">
            <div class="flag-head">Green Flags</div>
            {items_html(green, "green")}
        </div>
        <div class="flag-card yellow">
            <div class="flag-head">Yellow Flags</div>
            {items_html(yellow, "yellow")}
        </div>
        <div class="flag-card red">
            <div class="flag-head">Red Flags</div>
            {items_html(red, "red")}
        </div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ── Call Claude API ────────────────────────────────────────────────────────────
def analyze_conversation(conversation_text: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Analyze this conversation:\n\n{conversation_text}"}],
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)

# ── App UI ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Relationship<br>Text Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Paste any conversation — the AI will decode the communication patterns.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("---")
    st.markdown("**How to use**")
    st.markdown("1. Enter your API key\n2. Paste any conversation\n3. Hit Analyze")
    st.markdown("---")
    st.markdown('<div class="sticker">For reflection only. Not clinical advice.</div>', unsafe_allow_html=True)

conversation = st.text_area(
    "Paste your conversation here",
    height=220,
    placeholder="Alex: hey! are you free this weekend?\nYou: yeah probably, why?\nAlex: idk just thought maybe we could hang\n...",
)

analyze_btn = st.button("Analyze Conversation →", use_container_width=True, type="primary")

if analyze_btn:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not conversation.strip():
        st.warning("Please paste a conversation to analyze.")
    elif len(conversation.strip()) < 50:
        st.warning("The conversation seems too short for meaningful analysis. Try pasting more messages.")
    else:
        with st.spinner("Analyzing communication patterns..."):
            try:
                result = analyze_conversation(conversation, api_key)

                st.markdown("---")

                # Communication Style Scores
                st.markdown('<div class="section-label">Communication Style Scores</div>', unsafe_allow_html=True)
                render_scores(result.get("communication_style_scores", {}))

                # Behavior Signals
                st.markdown('<div class="section-label">Behavior Signals</div>', unsafe_allow_html=True)
                render_signals(result.get("behavior_signals", {}))

                # Bonus Signals
                with st.expander("Deep Signal Analysis (10 Bonus Metrics)", expanded=False):
                    render_bonus(result.get("bonus_signals", {}))

                # Flags
                st.markdown('<div class="section-label">Flags Detected</div>', unsafe_allow_html=True)
                render_flags(
                    result.get("green_flags", []),
                    result.get("yellow_flags", []),
                    result.get("red_flags", []),
                )

                # Archetype & Summary
                st.markdown('<div class="section-label">Relationship Dynamic</div>', unsafe_allow_html=True)
                archetype = result.get("archetype", "Unknown")
                archetype_reason = result.get("archetype_reason", "")
                summary = result.get("summary", "")
                st.markdown(f'<span class="archetype-pill">✦ {archetype}</span>', unsafe_allow_html=True)
                if archetype_reason:
                    st.markdown(f'<div class="summary-box"><em style="color:#777;font-size:0.8rem">Why this archetype: </em>{archetype_reason}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

                # Actionable Advice
                st.markdown('<div class="section-label">Actionable Advice</div>', unsafe_allow_html=True)
                advice_html = ""
                for i, tip in enumerate(result.get("actionable_advice", []), 1):
                    advice_html += f'<div class="advice-item"><div class="advice-num">{i}</div><div class="advice-text">{tip}</div></div>'
                st.markdown(advice_html, unsafe_allow_html=True)

                # Disclaimer
                st.markdown(
                    '<div class="disclaimer">⚠ This analysis is for personal reflection and entertainment only. '
                    'It is not a psychological assessment, clinical diagnosis, or substitute for professional '
                    'relationship advice. Communication patterns are inferred from text signals and may not '
                    'reflect the full context of your relationship.</div>',
                    unsafe_allow_html=True,
                )

                # Raw JSON expander
                with st.expander("View raw JSON output"):
                    st.json(result)

            except json.JSONDecodeError:
                st.error("The AI returned an unexpected format. Please try again.")
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key in the sidebar.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
