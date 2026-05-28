"""
ContentGenerator — uses OpenAI or Anthropic to generate:
  - Content ideas from trending topics
  - Full scripts for each idea
  - Platform-specific copy variants
"""

import json
import logging
from typing import Any

from config import Config

log = logging.getLogger(__name__)

IDEA_SYSTEM_PROMPT = """You are a world-class content strategist and viral content creator.
Your job is to analyze trending topics and produce highly engaging content ideas that
will perform well on social media. You understand hooks, pattern interrupts, storytelling,
and what makes content share-worthy."""

IDEA_USER_TEMPLATE = """
Niche: {niche}

Trending topics and recent news:
{trends_block}

Generate exactly {count} content ideas. For each idea return a JSON object with:
- title: compelling, specific title (NOT clickbait, but genuinely interesting)
- platform: one of [YouTube, TikTok, Instagram, LinkedIn, Twitter/X]
- format: one of [Short-form video, Long-form video, Carousel, Thread, Reel, Blog post]
- hook: the opening 1-2 sentences that stop the scroll (under 30 words)
- script: a full content script (300-600 words), formatted for the chosen platform
- cta: the call-to-action at the end
- hashtags: array of 5-8 relevant hashtags
- estimated_reach: "Low" | "Medium" | "High" based on topic virality potential
- rationale: one sentence explaining WHY this will perform well

Return ONLY a JSON array of {count} objects. No preamble, no markdown fences.
"""

SCRIPT_REFINEMENT_PROMPT = """
Refine this content script to be more engaging. Keep the same core idea but:
1. Make the hook more specific and punchy
2. Add 2-3 concrete examples or data points
3. Structure it with clear sections for the chosen platform
4. End with a strong CTA that drives action

Script: {script}
Platform: {platform}
Return ONLY the refined script text.
"""


class ContentGenerator:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.provider = cfg.ai_provider

        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=cfg.openai_api_key)
            except ImportError:
                log.warning("openai package not installed — using mock generator")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
            except ImportError:
                log.warning("anthropic package not installed — using mock generator")
                self.client = None
        else:
            self.client = None

    def generate_ideas(
        self,
        niche: str,
        trends: list[dict],
        count: int = 5
    ) -> list[dict[str, Any]]:
        """
        Generates content ideas from trending topics.
        Returns list of idea dicts with title, platform, script, etc.
        """
        if not self.client:
            log.warning("No AI client configured — returning mock ideas")
            return self._mock_ideas(niche, count)

        trends_block = "\n".join(
            f"- {t['title']}: {t['snippet']}" for t in trends[:15]
        )

        prompt = IDEA_USER_TEMPLATE.format(
            niche=niche,
            trends_block=trends_block,
            count=count
        )

        try:
            raw = self._call_llm(
                system=IDEA_SYSTEM_PROMPT,
                user=prompt,
                max_tokens=4000
            )
            ideas = json.loads(raw)
            log.info(f"Generated {len(ideas)} ideas via {self.provider}")
            return ideas

        except (json.JSONDecodeError, KeyError) as e:
            log.error(f"Failed to parse LLM response: {e}\nRaw: {raw[:500]}")
            return self._mock_ideas(niche, count)

    def _call_llm(self, system: str, user: str, max_tokens: int = 2000) -> str:
        """Calls the configured LLM and returns raw text response."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.cfg.ai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                max_tokens=max_tokens,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.cfg.ai_model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
            return response.content[0].text.strip()

        raise ValueError(f"Unknown AI provider: {self.provider}")

    def _mock_ideas(self, niche: str, count: int) -> list[dict]:
        """Realistic mock ideas for testing without API keys."""
        templates = [
            {
                "title": f"The {niche} strategy nobody is talking about",
                "platform": "LinkedIn",
                "format": "Thread",
                "hook": f"I spent 6 months testing every {niche} approach. Most advice is wrong. Here's what actually works:",
                "script": f"[HOOK]\nI spent 6 months testing every {niche} approach. Most advice is wrong.\n\nHere's what actually works — a thread:\n\n[POINT 1]\nFirst, forget the conventional wisdom about {niche}. The data tells a completely different story...\n\n[POINT 2]\nMost people optimize for the wrong metric. Instead of chasing X, focus on Y...\n\n[POINT 3]\nThe compounding effect: small consistent actions in {niche} beat big sporadic ones by 3x...\n\n[CTA]\nWhat's your biggest {niche} challenge right now? Drop it below — I read every reply.",
                "cta": f"What's your biggest {niche} challenge? Reply below.",
                "hashtags": [f"#{niche.replace(' ', '')}", "#strategy", "#growth", "#productivity", "#2025"],
                "estimated_reach": "High",
                "rationale": "Contrarian takes with personal evidence consistently outperform generic advice."
            },
            {
                "title": f"I tested 5 {niche} tools so you don't have to",
                "platform": "YouTube",
                "format": "Short-form video",
                "hook": f"Which {niche} tool is actually worth paying for in 2025? I tested all 5. Results were surprising.",
                "script": f"[HOOK — 0-3 seconds]\nWhich {niche} tool is actually worth it? I tested all 5.\n\n[SETUP — 3-10 seconds]\nI spent two weeks using each tool daily and tracked results across three key metrics...\n\n[REVEAL — 10-50 seconds]\nTool #1: Looks impressive but... [detail]\nTool #2: Underrated gem — [detail]\nTool #3: Overhyped. Here's why...\n\n[VERDICT]\nIf I had to pick just one, it's [tool] because...\n\n[CTA]\nComment your current tool — I'll tell you if it's worth keeping.",
                "cta": "Comment your current tool — I'll tell you if it's worth keeping.",
                "hashtags": [f"#{niche.replace(' ', '')}", "#tools", "#review", "#productivity", "#tech"],
                "estimated_reach": "Medium",
                "rationale": "Tool comparison content drives high intent traffic and saves people research time."
            },
        ]
        return templates[:count]