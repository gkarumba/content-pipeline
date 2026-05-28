# Automated Content Pipeline — MVP

A 7-stage end-to-end content automation system: scrape trends → generate ideas + scripts → create thumbnail prompts → push to approval board → schedule publishing → track engagement.

## Quick Start

```bash
# 1. Install dependencies
cd pipeline && pip install -r requirements.txt

# 2. Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# 3. Test run (no Airtable writes)
python pipeline.py --niche "your niche here" --ideas 5 --dry-run

# 4. Real run
python pipeline.py --niche "your niche here" --ideas 5

# 5. Start API server (for n8n)
python api_server.py
```

## Project Structure

```
content-pipeline/
├── pipeline/
│   ├── pipeline.py           # Main orchestrator — run this
│   ├── api_server.py         # Flask server for n8n integration
│   ├── scraper.py            # Trend scraping (Serper API)
│   ├── content_generator.py  # AI idea + script generation
│   ├── thumbnail_generator.py
│   ├── airtable_client.py
│   ├── publisher.py          # Buffer scheduling + engagement tracking
│   ├── config.py
│   └── requirements.txt
├── n8n/
│   └── workflow.json         # Import into n8n
├── dashboard/
│   └── Dashboard.jsx         # React approval board
├── docs/
│   └── ContentPipeline_Documentation.docx
└── .env.example
```

## API Keys Needed

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| Serper.dev | Trend scraping | 2,500/month | serper.dev |
| OpenAI | Content generation | Pay-as-you-go | platform.openai.com |
| Airtable | Approval board | 1,000 records | airtable.com |
| Buffer | Scheduling | 3 channels | buffer.com |

## See `docs/ContentPipeline_Documentation.docx` for full setup guide.