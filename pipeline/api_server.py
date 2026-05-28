"""
publisher.py — Schedule approved content via Buffer API
tracker.py   — Pull engagement metrics back into Airtable

Buffer API docs: https://buffer.com/developers/api
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Optional

from config import Config
from airtable_client import AirtableClient

log = logging.getLogger(__name__)

BUFFER_API = "https://api.bufferapp.com/1"


# ─────────────────────────────────────────────────────────────
# Publisher
# ─────────────────────────────────────────────────────────────

class BufferPublisher:
    """
    Schedules approved Airtable records as posts in Buffer.
    Marks records as Scheduled after queuing.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.airtable = AirtableClient(cfg)
        self.profile_ids = [
            p.strip() for p in cfg.buffer_profile_ids.split(",") if p.strip()
        ]

        if not cfg.buffer_access_token:
            log.warning("BUFFER_ACCESS_TOKEN not set — publisher in dry-run mode")
        if not self.profile_ids:
            log.warning("BUFFER_PROFILE_IDS not set — no profiles to publish to")

    def run(self, dry_run: bool = False) -> int:
        """
        Fetches approved records and schedules them via Buffer.
        Returns number of records scheduled.
        """
        records = self.airtable.get_approved_records()
        if not records:
            log.info("No approved records to schedule")
            return 0

        scheduled = 0
        # Stagger posts: start tomorrow, one per day
        base_date = datetime.utcnow() + timedelta(days=1)

        for i, record in enumerate(records):
            fields = record.get("fields", {})
            title = fields.get("Title", "Untitled")
            script = fields.get("Script", "")
            hashtags = fields.get("Hashtags", "")
            platform = fields.get("Platform", "")

            # Build post text: hook + hashtags (Buffer truncates if too long)
            hook = fields.get("Hook", "")
            post_text = f"{hook}\n\n{hashtags}" if hook else f"{script[:280]}\n\n{hashtags}"

            schedule_time = base_date + timedelta(days=i)
            schedule_iso = schedule_time.strftime("%Y-%m-%dT09:00:00Z")  # 9am UTC

            if dry_run:
                log.info(f"[DRY RUN] Would schedule: '{title}' on {schedule_iso}")
                scheduled += 1
                continue

            if not self.cfg.buffer_access_token or not self.profile_ids:
                log.warning("Skipping — Buffer not configured")
                continue

            buffer_id = self._queue_to_buffer(
                text=post_text,
                scheduled_at=schedule_iso,
                profile_ids=self.profile_ids
            )

            if buffer_id:
                self.airtable.mark_scheduled(
                    record_id=record["id"],
                    scheduled_date=schedule_time.strftime("%Y-%m-%d"),
                    buffer_id=buffer_id
                )
                scheduled += 1
                log.info(f"Scheduled '{title}' → Buffer ID {buffer_id}")

        log.info(f"Scheduled {scheduled}/{len(records)} records")
        return scheduled

    def _queue_to_buffer(
        self,
        text: str,
        scheduled_at: str,
        profile_ids: list[str]
    ) -> Optional[str]:
        """Posts to Buffer API. Returns update ID or None on failure."""
        for profile_id in profile_ids:
            try:
                resp = requests.post(
                    f"{BUFFER_API}/updates/create.json",
                    data={
                        "access_token": self.cfg.buffer_access_token,
                        "profile_ids[]": profile_id,
                        "text": text,
                        "scheduled_at": scheduled_at,
                        "now": "false"
                    },
                    timeout=10
                )
                resp.raise_for_status()
                data = resp.json()
                updates = data.get("updates", [])
                if updates:
                    return updates[0].get("id", "")
            except requests.RequestException as e:
                log.error(f"Buffer API error for profile {profile_id}: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# Engagement Tracker
# ─────────────────────────────────────────────────────────────

class EngagementTracker:
    """
    Pulls engagement stats from Buffer (and optionally native social APIs)
    and writes them back into Airtable for performance tracking.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.airtable = AirtableClient(cfg)

    def run(self) -> int:
        """
        Fetches engagement for all Published records.
        Returns number of records updated.
        """
        records = self.airtable.get_published_records()
        if not records:
            log.info("No published records to track")
            return 0

        updated = 0
        for record in records:
            fields = record.get("fields", {})
            platform = fields.get("Platform", "")
            published_url = fields.get("Published URL", "")

            stats = self._fetch_stats(platform, published_url, record["id"])
            if stats:
                self.airtable.update_engagement(
                    record_id=record["id"],
                    views=stats.get("views", 0),
                    likes=stats.get("likes", 0),
                    shares=stats.get("shares", 0),
                    comments=stats.get("comments", 0)
                )
                updated += 1
                log.info(f"Updated engagement for '{fields.get('Title', record['id'])}'")

        log.info(f"Tracked engagement for {updated}/{len(records)} records")
        return updated

    def _fetch_stats(
        self, platform: str, url: str, record_id: str
    ) -> Optional[dict]:
        """
        Fetches engagement stats for a post.

        Currently fetches from Buffer's sent updates endpoint.
        Extend this method with native API calls per platform
        (Twitter API v2, YouTube Data API, LinkedIn API, etc.)
        """
        if not self.cfg.buffer_access_token:
            log.warning("Buffer not configured — returning mock stats")
            return {"views": 0, "likes": 0, "shares": 0, "comments": 0}

        try:
            resp = requests.get(
                f"{BUFFER_API}/profiles/{self.profile_id}/updates/sent.json",
                params={"access_token": self.cfg.buffer_access_token, "count": 100},
                timeout=10
            )
            resp.raise_for_status()
            updates = resp.json().get("updates", [])

            # Match by URL or find most recent
            for update in updates:
                if url and url in update.get("text", ""):
                    stats = update.get("statistics", {})
                    return {
                        "views": stats.get("reach", 0),
                        "likes": stats.get("favorites", 0),
                        "shares": stats.get("retweets", stats.get("shares", 0)),
                        "comments": stats.get("mentions", 0)
                    }

        except requests.RequestException as e:
            log.error(f"Buffer stats fetch failed: {e}")

        return None


# ─────────────────────────────────────────────────────────────
# CLI entry points
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    from config import Config

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["publish", "track"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = Config()

    if args.action == "publish":
        pub = BufferPublisher(cfg)
        pub.run(dry_run=args.dry_run)
    elif args.action == "track":
        tracker = EngagementTracker(cfg)
        tracker.run()