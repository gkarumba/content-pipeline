"""
Automated Content Pipeline — Core Orchestrator
Runs the full pipeline: scrape → ideate → script → thumbnail → push to Airtable
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Optional

from scraper import TrendScraper
from content_generator import ContentGenerator
from airtable_client import AirtableClient
from thumbnail_generator import ThumbnailGenerator
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)
log = logging.getLogger(__name__)


def run_pipeline(
    niche: str,
    num_ideas: int = 5,
    dry_run: bool = False
):
    """
    Full pipeline execution.

    Args:
        niche:     Topic or niche to generate content for (e.g. "personal finance Kenya")
        num_ideas: How many content ideas to generate per run
        dry_run:   If True, prints output but does NOT write to Airtable
    """
    cfg = Config()
    log.info(f"=== Pipeline started | niche='{niche}' | ideas={num_ideas} ===")
    start = time.time()

    # ── Step 1: Scrape trending topics ──────────────────────────────────────
    log.info("Step 1/4 — Scraping trending topics...")
    scraper = TrendScraper(cfg)
    trends = scraper.get_trends(niche, limit=20)
    log.info(f"  Found {len(trends)} trending items")

    # ── Step 2: Generate content ideas + scripts ─────────────────────────────
    log.info("Step 2/4 — Generating content ideas...")
    generator = ContentGenerator(cfg)
    ideas = generator.generate_ideas(niche=niche, trends=trends, count=num_ideas)
    log.info(f"  Generated {len(ideas)} ideas")

    # ── Step 3: Generate thumbnail prompts ───────────────────────────────────
    log.info("Step 3/4 — Generating thumbnail prompts...")
    thumb_gen = ThumbnailGenerator(cfg)
    for idea in ideas:
        idea["thumbnail_prompt"] = thumb_gen.generate_prompt(idea)
        idea["thumbnail_url"] = thumb_gen.generate_image(idea["thumbnail_prompt"])

    # ── Step 4: Push to Airtable approval board ──────────────────────────────
    if dry_run:
        log.info("Step 4/4 — DRY RUN: Printing ideas (not writing to Airtable)")
        for i, idea in enumerate(ideas, 1):
            print(f"\n{'='*60}")
            print(f"IDEA {i}: {idea['title']}")
            print(f"Platform: {idea['platform']} | Format: {idea['format']}")
            print(f"Hook: {idea['hook']}")
            print(f"Script preview: {idea['script'][:200]}...")
            print(f"Thumbnail prompt: {idea['thumbnail_prompt']}")
    else:
        log.info("Step 4/4 — Pushing to Airtable...")
        airtable = AirtableClient(cfg)
        record_ids = []
        for idea in ideas:
            record_id = airtable.create_content_record(idea)
            record_ids.append(record_id)
            log.info(f"  Created record {record_id}: {idea['title'][:50]}")

    elapsed = round(time.time() - start, 1)
    log.info(f"=== Pipeline complete in {elapsed}s | {len(ideas)} ideas pushed ===")
    return ideas


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automated Content Pipeline")
    parser.add_argument("--niche", required=True, help="Content niche or topic")
    parser.add_argument("--ideas", type=int, default=5, help="Number of ideas to generate")
    parser.add_argument("--dry-run", action="store_true", help="Print without saving to Airtable")
    args = parser.parse_args()

    run_pipeline(
        niche=args.niche,
        num_ideas=args.ideas,
        dry_run=args.dry_run
    )