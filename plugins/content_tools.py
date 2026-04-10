# plugins/content_tools.py — Content Creation, Writing & Social Media Tools

import os, re, json, random
from datetime import datetime
from plugins.advanced_ai import _ai


# ══ CONTENT CALENDAR ══════════════════════════════════════════════════════════
def content_calendar(topic, days=7, platforms=None):
    platforms = platforms or ["Instagram","Twitter","YouTube","LinkedIn"]
    plat_str  = ", ".join(platforms)
    prompt = (f"Create a {days}-day content calendar for: {topic}\n"
              f"Platforms: {plat_str}\n\n"
              f"For each day provide:\n"
              f"Day N | Platform | Content Type | Topic/Hook | Best Time to Post\n"
              f"Format as a table.")
    return _ai(prompt)

def social_media_strategy(niche, goal):
    return _ai(f"Create a 30-day social media growth strategy for a {niche} creator with goal: {goal}. "
               f"Include content types, posting frequency, engagement tactics, and hashtag strategy.")

def viral_hook_generator(topic, count=5):
    return _ai(f"Write {count} viral hooks/opening lines for content about: {topic}\n"
               f"Make them attention-grabbing, curiosity-driven, and platform-agnostic.")

def caption_generator(image_description, platform="instagram", tone="casual"):
    return _ai(f"Write a {tone} {platform} caption for: {image_description}\n"
               f"Include relevant emojis, call-to-action, and 10 hashtags.")

def thread_generator(topic, tweets=8):
    return _ai(f"Write a {tweets}-tweet Twitter thread about: {topic}\n"
               f"Start with a hook, build value, end with CTA. Number each tweet.")

def youtube_description(video_title, key_points):
    return _ai(f"Write a YouTube video description for: '{video_title}'\n"
               f"Key points: {key_points}\n"
               f"Include: hook paragraph, timestamps placeholder, links section, hashtags.")

def youtube_title_ideas(topic, count=10):
    return _ai(f"Generate {count} high-CTR YouTube video titles for: {topic}\n"
               f"Mix formats: how-to, listicle, question, shocking stat, story.")

def blog_outline(topic, style="comprehensive"):
    return _ai(f"Create a detailed {style} blog post outline for: '{topic}'\n"
               f"Include: title, meta description, H2/H3 headings, key points per section, FAQ.")

def seo_keywords(topic, count=20):
    return _ai(f"Generate {count} SEO keywords for: {topic}\n"
               f"Include: primary keywords, long-tail variations, question keywords, related terms.\n"
               f"Format as a table with search intent (informational/commercial/transactional).")

def newsletter_template(niche, issue_number=1):
    return _ai(f"Write a newsletter template for a {niche} newsletter (Issue #{issue_number}).\n"
               f"Include: subject line, preheader, intro, 3 value sections, CTA, footer.")

def press_release(event, company, date):
    return _ai(f"Write a professional press release:\n"
               f"Event: {event}\nCompany: {company}\nDate: {date}\n"
               f"Include: headline, dateline, lead paragraph, body, boilerplate, contact info.")

def product_description(product, features, audience):
    return _ai(f"Write a compelling product description for: {product}\n"
               f"Features: {features}\nTarget audience: {audience}\n"
               f"Make it persuasive, benefit-focused, SEO-friendly.")

def ad_copy(product, platform, objective):
    return _ai(f"Write ad copy for {platform}:\n"
               f"Product: {product}\nObjective: {objective}\n"
               f"Include: headline, primary text, CTA. Write 3 variations.")

def cold_email_template(sender_role, recipient_role, offer):
    return _ai(f"Write a cold email from {sender_role} to {recipient_role} about: {offer}\n"
               f"Keep it under 150 words. Subject line + body. Be specific, not spammy.")

def resume_bullet_point(role, achievement, metric=""):
    return _ai(f"Rewrite this resume bullet point using the STAR method and strong action verbs:\n"
               f"Role: {role}\nAchievement: {achievement}\nMetric: {metric}\n"
               f"Return 3 variations.")


# ══ WRITING TOOLS ════════════════════════════════════════════════════════════
def grammar_check(text):
    return _ai(f"Check grammar and spelling in this text. List all errors with corrections:\n\n{text}")

def tone_analyzer(text):
    return _ai(f"Analyze the tone and sentiment of this text. Provide:\n"
               f"1. Overall tone (formal/informal/aggressive/friendly etc)\n"
               f"2. Sentiment (positive/negative/neutral)\n"
               f"3. Readability level\n4. Suggestions to improve\n\nText: {text[:1000]}")

def paraphrase(text, style="standard"):
    styles = {
        "standard":  "Rewrite in a clear, standard way.",
        "formal":    "Rewrite in a formal, professional tone.",
        "simple":    "Rewrite in simple, easy-to-understand language.",
        "creative":  "Rewrite creatively and engagingly.",
        "academic":  "Rewrite in academic style.",
    }
    inst = styles.get(style.lower(), styles["standard"])
    return _ai(f"{inst} Keep the meaning. Return only the rewritten text.\n\n{text}")

def expand_text(text, target_words=200):
    return _ai(f"Expand this text to approximately {target_words} words while maintaining the core message:\n\n{text}")

def condense_text(text, target_words=50):
    return _ai(f"Condense this text to approximately {target_words} words, keeping all key information:\n\n{text}")

def formal_to_casual(text):
    return _ai(f"Convert this formal text to a casual, friendly tone:\n\n{text}")

def casual_to_formal(text):
    return _ai(f"Convert this casual text to a formal, professional tone:\n\n{text}")

def bullet_to_paragraph(bullets):
    return _ai(f"Convert these bullet points into flowing paragraphs:\n\n{bullets}")

def paragraph_to_bullets(text):
    return _ai(f"Convert this text into clear, concise bullet points:\n\n{text}")

def active_to_passive(text):
    return _ai(f"Convert active voice to passive voice in this text:\n\n{text}")

def passive_to_active(text):
    return _ai(f"Convert passive voice to active voice in this text. Return only the converted text:\n\n{text}")

def add_examples(text):
    return _ai(f"Add concrete examples and analogies to make this text more understandable:\n\n{text}")

def simplify_jargon(text, field="technology"):
    return _ai(f"Replace {field} jargon with plain language anyone can understand:\n\n{text}")


# ══ SOCIAL MEDIA UTILITIES ════════════════════════════════════════════════════
def hashtag_generator(topic, platform="instagram", count=20):
    return _ai(f"Generate {count} relevant hashtags for {platform} about: {topic}\n"
               f"Mix popular and niche hashtags. Return only the hashtags.")

def bio_generator(name, role, niche, tone="professional"):
    return _ai(f"Write a compelling social media bio for:\n"
               f"Name: {name}\nRole: {role}\nNiche: {niche}\nTone: {tone}\n"
               f"Keep under 160 characters for Twitter, write 3 versions for different platforms.")

def engagement_response(comment, brand_voice="friendly"):
    return _ai(f"Write a {brand_voice} response to this social media comment:\n'{comment}'\n"
               f"Keep it authentic and under 50 words.")

def collaboration_pitch(your_niche, their_niche, proposal):
    return _ai(f"Write a collaboration pitch DM from {your_niche} to {their_niche}:\n"
               f"Proposal: {proposal}\nKeep it brief, specific, and mutually beneficial.")

def content_ideas(niche, count=15):
    return _ai(f"Generate {count} unique content ideas for a {niche} creator.\n"
               f"Format: Type | Topic | Hook | Target Audience")

def trending_topics_prompt(niche):
    return _ai(f"Suggest 10 trending topics in {niche} right now that would make great content. "
               f"Explain why each is trending and how to approach it.")
