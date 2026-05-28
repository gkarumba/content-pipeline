"""
AirtableClient — read/write content records to the Airtable approval board.

Table schema (create this manually in Airtable or use setup_airtable.py):
  Title           Single line text
  Platform        Single select: YouTube | TikTok | Instagram | LinkedIn | Twitter/X
  Format          Single select: Short-form video | Long-form video | Carousel | Thread | Reel | Blog post
  Status          Single select: Pending | Approved | Rejected | Scheduled | Published
  Hook            Long text
  Script          Long text
  CTA             Single line text
  Hashtags        Long text
  Thumbnail URL   URL
  Thumbnail Prompt Long text
  Estimated Reach Single select: Low | Medium | High
  Rationale       Long text
  Scheduled Date  Date
  Published URL   URL
  Views           Number
  Likes           Number
  Shares          Number
  Comments        Number
  Created Date    Created time (auto)
  Niche           Single line text
"""

import logging
import requests
from datetime import datetime
from typing import Any, Optional

from config import Config

log = logging.getLogger(__name__)

AIRTABLE_BASE_URL = "https://api.airtable.com/v0"


class AirtableClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.base_url = f"{AIRTABLE_BASE_URL}/{cfg.airtable_base_id}/{cfg.airtable_table_name}"
        self.headers = {
            "Authorization": f"Bearer {cfg.airtable_api_key}",
            "Content-Type": "application/json"
        }

    def create_content_record(self, idea: dict[str, Any]) -> str:
        """
        Creates a new record in the Airtable content board.
        Returns the new record ID.
        """
        hashtags_str = " ".join(idea.get("hashtags", []))

        fields = {
            "Title": idea.get("title", "Untitled"),
            "Platform": idea.get("platform", ""),
            "Format": idea.get("format", ""),
            "Status": "Pending",
            "Hook": idea.get("hook", ""),
            "Script": idea.get("script", ""),
            "CTA": idea.get("cta", ""),
            "Hashtags": hashtags_str,
            "Thumbnail URL": idea.get("thumbnail_url", ""),
            "Thumbnail Prompt": idea.get("thumbnail_prompt", ""),
            "Estimated Reach": idea.get("estimated_reach", "Medium"),
            "Rationale": idea.get("rationale", ""),
            "Niche": idea.get("niche", ""),
        }

        # Remove empty optional fields to avoid Airtable validation errors
        fields = {k: v for k, v in fields.items() if v}

        resp = requests.post(
            self.base_url,
            headers=self.headers,
            json={"fields": fields},
            timeout=10
        )

        if resp.status_code not in (200, 201):
            log.error(f"Airtable error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        record_id = resp.json()["id"]
        log.info(f"Created Airtable record {record_id}")
        return record_id

    def get_approved_records(self) -> list[dict[str, Any]]:
        """Fetches all records with Status = 'Approved' (ready to schedule)."""
        params = {
            "filterByFormula": "{Status} = 'Approved'",
            "sort[0][field]": "Created Date",
            "sort[0][direction]": "desc"
        }
        resp = requests.get(
            self.base_url,
            headers=self.headers,
            params=params,
            timeout=10
        )
        resp.raise_for_status()
        records = resp.json().get("records", [])
        log.info(f"Found {len(records)} approved records")
        return records

    def get_published_records(self) -> list[dict[str, Any]]:
        """Fetches all records with Status = 'Published' (for engagement tracking)."""
        params = {
            "filterByFormula": "{Status} = 'Published'",
            "fields[]": ["Title", "Platform", "Published URL", "Views", "Likes", "Shares"]
        }
        resp = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("records", [])

    def update_record(self, record_id: str, fields: dict[str, Any]) -> None:
        """Updates specific fields on an existing record."""
        resp = requests.patch(
            f"{self.base_url}/{record_id}",
            headers=self.headers,
            json={"fields": fields},
            timeout=10
        )
        if resp.status_code not in (200, 201):
            log.error(f"Airtable update error {resp.status_code}: {resp.text}")
            resp.raise_for_status()
        log.info(f"Updated record {record_id}")

    def mark_scheduled(self, record_id: str, scheduled_date: str, buffer_id: str = "") -> None:
        """Marks a record as Scheduled with its scheduled publish date."""
        fields = {
            "Status": "Scheduled",
            "Scheduled Date": scheduled_date,
        }
        if buffer_id:
            fields["Buffer Update ID"] = buffer_id
        self.update_record(record_id, fields)

    def update_engagement(
        self,
        record_id: str,
        views: int = 0,
        likes: int = 0,
        shares: int = 0,
        comments: int = 0
    ) -> None:
        """Updates engagement metrics on a published record."""
        self.update_record(record_id, {
            "Views": views,
            "Likes": likes,
            "Shares": shares,
            "Comments": comments,
            "Last Tracked": datetime.utcnow().isoformat()
        })