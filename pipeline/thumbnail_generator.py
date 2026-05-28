"""
ThumbnailGenerator — generates thumbnail prompts and optionally calls DALL-E 3
to produce actual thumbnail images.

When ENABLE_IMAGE_GEN=false (default), returns only the text prompt.
When ENABLE_IMAGE_GEN=true, calls DALL-E 3 and returns the image URL.
"""

import logging
from typing import Optional
from openai import OpenAI
from config import Config

log = logging.getLogger(__name__)

THUMBNAIL_SYSTEM_PROMPT = """You are a professional YouTube thumbnail and social media
visual designer. You create highly specific, visually compelling image prompts that
result in click-worthy thumbnails. You understand color psychology, composition,
and what drives clicks on each platform."""

THUMBNAIL_PROMPT_TEMPLATE = """
Create a DALL-E image generation prompt for a thumbnail/cover image for this content:

Title: {title}
Platform: {platform}
Format: {format}
Hook: {hook}

Requirements:
- High contrast, bold colors that pop on mobile screens
- No text overlay (text will be added separately)
- Clear focal point — one main subject
- Style appropriate for {platform}
- Photorealistic or stylized depending on platform norms
- 16:9 aspect ratio composition

Return ONLY the image generation prompt. No explanation.
"""


class ThumbnailGenerator:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.enabled = cfg.enable_image_gen

        if self.enabled:
            try:
                self.client = OpenAI(api_key=cfg.openai_api_key)
            except ImportError:
                log.warning("openai not installed — image generation disabled")
                self.client = None
                self.enabled = False
        else:
            self.client = None

    def generate_prompt(self, idea: dict) -> str:
        """
        Generates a detailed DALL-E prompt for the content idea's thumbnail.
        Uses a simple template if no AI client is configured.
        """
        if not self.client:
            return self._template_prompt(idea)

        try:
            client = OpenAI(api_key=self.cfg.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": THUMBNAIL_SYSTEM_PROMPT},
                    {"role": "user", "content": THUMBNAIL_PROMPT_TEMPLATE.format(
                        title=idea.get("title", ""),
                        platform=idea.get("platform", ""),
                        format=idea.get("format", ""),
                        hook=idea.get("hook", "")
                    )}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            log.error(f"Thumbnail prompt generation failed: {e}")
            return self._template_prompt(idea)

    def generate_image(self, prompt: str) -> str:
        """
        Calls DALL-E 3 to generate the thumbnail image.
        Returns URL if generation is enabled, empty string otherwise.
        """
        if not self.enabled or not self.client:
            return ""

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",   # 16:9 landscape
                quality="standard",
                n=1
            )
            url = response.data[0].url
            log.info(f"Generated thumbnail: {url[:60]}...")
            return url
        except Exception as e:
            log.error(f"DALL-E image generation failed: {e}")
            return ""

    def _template_prompt(self, idea: dict) -> str:
        """Fallback prompt template when no AI client is available."""
        platform = idea.get("platform", "social media")
        title = idea.get("title", "content")
        platform_styles = {
            "YouTube": "cinematic, dramatic lighting, bold composition, thumbnail style",
            "TikTok": "vibrant, energetic, Gen-Z aesthetic, vertical composition",
            "Instagram": "clean, aesthetic, lifestyle photography style",
            "LinkedIn": "professional, corporate, clean background, business setting",
            "Twitter/X": "punchy, meme-aware, high contrast, shareable visual"
        }
        style = platform_styles.get(platform, "clean, modern, high contrast")
        return (
            f"A {style} image representing '{title}'. "
            f"Single focal subject, no text, photorealistic, 16:9 composition, "
            f"high saturation, designed to stop scrolling on {platform}."
        )