import { useState, useEffect, useCallback } from "react";

const STATUS_COLORS = {
  Pending:   { bg: "#1a1a2e", accent: "#f0a500", text: "#f0a500" },
  Approved:  { bg: "#0d2e1a", accent: "#00e676", text: "#00e676" },
  Rejected:  { bg: "#2e0d0d", accent: "#ff4444", text: "#ff4444" },
  Scheduled: { bg: "#0d1a2e", accent: "#40c4ff", text: "#40c4ff" },
  Published: { bg: "#1a0d2e", accent: "#ce93d8", text: "#ce93d8" },
};

const PLATFORM_ICONS = {
  YouTube: "▶",
  TikTok: "♪",
  Instagram: "◈",
  LinkedIn: "in",
  "Twitter/X": "𝕏",
};

const REACH_COLORS = { High: "#00e676", Medium: "#f0a500", Low: "#ff4444" };

const MOCK_RECORDS = [
  {
    id: "rec001",
    fields: {
      Title: "The personal finance strategy nobody is talking about",
      Platform: "LinkedIn",
      Format: "Thread",
      Status: "Pending",
      Hook: "I tested every budgeting method for 6 months. Most advice is wrong. Here's what actually compounds:",
      Script: "HOOK\nI tested every budgeting method for 6 months. Most advice is wrong.\n\nHere's what actually works — a thread:\n\n1/ Forget the 50/30/20 rule. It's designed for American salaries. Here's the African-market adjusted version...\n\n2/ Most people optimize savings rate. The real lever is income growth speed...\n\n3/ Mobile money is an asset class nobody teaches. M-Pesa lock-ins can yield 8-12% annually...\n\n4/ The compounding effect: KES 1,000 daily beats KES 30,000 monthly by 23% in 2 years.\n\nCTA: What's your biggest money block right now? Reply — I read every comment.",
      CTA: "What's your biggest money block? Reply below.",
      Hashtags: "#PersonalFinance #MoneyKenya #Investing #FinancialFreedom #Wealth",
      "Thumbnail Prompt": "Professional confident person looking at upward trending financial graph, dramatic lighting, dark background, Kenyan business aesthetic, no text",
      "Thumbnail URL": "",
      "Estimated Reach": "High",
      Rationale: "Contrarian finance takes with local context consistently outperform generic advice in East African markets.",
      Niche: "personal finance Kenya",
    }
  },
  {
    id: "rec002",
    fields: {
      Title: "I tried 5 AI tools so you don't have to — here's the verdict",
      Platform: "YouTube",
      Format: "Short-form video",
      Status: "Approved",
      Hook: "Which AI tool is actually worth paying for in 2025? I tested all 5. One result surprised me.",
      Script: "HOOK (0-3s)\nWhich AI tool is worth paying for? I tested all 5.\n\nSETUP (3-8s)\nI spent two weeks using each daily and tracked output quality, speed, and cost.\n\nREVEALS (8-45s)\nTool #1 — ChatGPT Plus: Great for writing, bad at math. Worth it if you write daily.\nTool #2 — Claude Pro: Best for long documents and nuance. Underrated.\nTool #3 — Gemini Advanced: Weakest output but Google integration saves time.\nTool #4 — Perplexity Pro: Only one I'd pay for just for research.\nTool #5 — Cursor AI: If you code, non-negotiable.\n\nVERDICT\nFor most people: Claude Pro. For researchers: Perplexity. For devs: Cursor.\n\nCTA\nComment your use case — I'll tell you exactly which to get.",
      CTA: "Comment your use case — I'll tell you exactly which to get.",
      Hashtags: "#AI #AITools #Productivity #Tech2025 #ChatGPT",
      "Thumbnail Prompt": "Five glowing app icons arranged in a competition bracket on dark background, one highlighted as winner with golden glow",
      "Thumbnail URL": "",
      "Estimated Reach": "High",
      Rationale: "Tool comparison content drives high intent traffic and has long shelf life.",
      Niche: "AI tools",
    }
  },
  {
    id: "rec003",
    fields: {
      Title: "How to build your first automation in under 2 hours",
      Platform: "TikTok",
      Format: "Short-form video",
      Status: "Scheduled",
      Hook: "You're wasting 3 hours/week on tasks a $0 tool can do. Let me show you.",
      Script: "HOOK\nYou're wasting 3 hours/week on tasks a free tool can handle.\n\nSETUP\nI'm going to show you how to build your first automation — no code, no experience needed.\n\nSTEPS\nStep 1: Pick one repetitive task. Mine was email sorting.\nStep 2: Open Make.com — free account, no card needed.\nStep 3: Connect Gmail. Takes 90 seconds.\nStep 4: Set the rule: 'If subject contains INVOICE → move to Finance folder + add to spreadsheet.'\nStep 5: Turn it on.\n\nRESULT\nThat's it. I saved 45 minutes last week alone.\n\nCTA\nWhat task are you automating first? Comment below.",
      CTA: "What task are you automating first?",
      Hashtags: "#Automation #Productivity #NoCode #Make #WorkSmarter",
      "Thumbnail Prompt": "Robotic arm pressing play button on a laptop screen showing workflow diagram, neon green accent lights, dark industrial setting",
      "Thumbnail URL": "",
      "Estimated Reach": "Medium",
      Rationale: "Beginner automation tutorials have massive top-of-funnel demand on TikTok.",
      Niche: "automation tools",
      "Scheduled Date": "2025-06-02"
    }
  },
  {
    id: "rec004",
    fields: {
      Title: "Why your LinkedIn posts get 12 views (and how to fix it)",
      Platform: "LinkedIn",
      Format: "Carousel",
      Status: "Rejected",
      Hook: "12 views on your last LinkedIn post? Here's the algorithm truth nobody says out loud.",
      Script: "SLIDE 1 — HOOK\n12 views. That's the average for most LinkedIn posts.\nHere's why — and the fix.\n\nSLIDE 2 — PROBLEM\nLinkedIn's algorithm punishes:\n• Outbound links in the post\n• Posting and disappearing\n• Zero engagement in the first 60 minutes\n\nSLIDE 3 — THE FIX\nDo this instead:\n✅ Post, then comment on 10 other posts immediately\n✅ First comment on your own post = extra context, not spam\n✅ Engage with replies within 1 hour\n\nSLIDE 4 — THE HOOK FORMULA\nEvery viral LinkedIn post has:\nLine 1: Bold claim or surprising stat\nLine 2: Why this matters to YOU\nLine 3: Here's the thread (creates curiosity gap)\n\nSLIDE 5 — CTA\nSave this. Your next post will perform better.",
      CTA: "Save this post — your next one will perform better.",
      Hashtags: "#LinkedIn #ContentCreation #SocialMedia #GrowthHacks #PersonalBranding",
      "Thumbnail Prompt": "",
      "Thumbnail URL": "",
      "Estimated Reach": "Medium",
      Rationale: "Platform-specific growth hacks resonate strongly with creator audiences.",
      Niche: "LinkedIn growth",
    }
  },
  {
    id: "rec005",
    fields: {
      Title: "The 30-day content system that got me to 10K followers",
      Platform: "Instagram",
      Format: "Reel",
      Status: "Published",
      Hook: "30 days. 10K followers. One system. Here's the whole thing.",
      Script: "HOOK (0-2s)\n30 days. 10K followers. One system.\n\nDAY 1-7: FOUNDATION\nPost every day. Don't worry about quality yet — volume builds confidence and data.\n\nDAY 8-14: ANALYZE\nCheck your top 3 posts. What's common? That's your content DNA.\n\nDAY 15-21: DOUBLE DOWN\nOnly create content in the format of your top 3. No experimenting.\n\nDAY 22-30: REPURPOSE\nTake your best post. Make it a carousel. Then a Reel. Then a Story.\nOne idea = 4 pieces of content.\n\nRESULT\nDay 30: 10,247 followers, 3 brand deals, 1 paid client.\n\nCTA\nSave this Reel. Day 1 starts today.",
      CTA: "Save this. Day 1 starts today.",
      Hashtags: "#Instagram #ContentCreator #GrowOnInstagram #SocialMediaTips #CreatorEconomy",
      "Thumbnail Prompt": "Phone screen showing follower count going up with confetti explosion, clean white background, joyful energy",
      "Thumbnail URL": "",
      "Estimated Reach": "High",
      Rationale: "Documented personal results with a clear system drive saves and shares.",
      Niche: "Instagram growth",
      "Published URL": "https://instagram.com/p/example",
      Views: 24800,
      Likes: 1847,
      Shares: 312,
      Comments: 94,
    }
  }
];

const formatNumber = (n) => {
  if (!n) return "—";
  if (n >= 1000) return `${(n/1000).toFixed(1)}K`;
  return n.toString();
};

function StatusBadge({ status }) {
  const s = STATUS_COLORS[status] || STATUS_COLORS.Pending;
  return (
    <span style={{
      background: s.bg,
      color: s.text,
      border: `1px solid ${s.accent}40`,
      padding: "3px 10px",
      borderRadius: 20,
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
    }}>
      {status}
    </span>
  );
}

function ScriptModal({ idea, onClose }) {
  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 1000, padding: 24
    }} onClick={onClose}>
      <div style={{
        background: "#0e0e14", border: "1px solid #2a2a3a",
        borderRadius: 16, padding: 32, maxWidth: 680, width: "100%",
        maxHeight: "85vh", overflowY: "auto"
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 6 }}>
              {idea.fields.Platform} · {idea.fields.Format}
            </div>
            <h2 style={{ color: "#fff", margin: 0, fontSize: 18, lineHeight: 1.3 }}>
              {idea.fields.Title}
            </h2>
          </div>
          <button onClick={onClose} style={{
            background: "none", border: "none", color: "#666",
            fontSize: 22, cursor: "pointer", padding: "0 4px", marginLeft: 16
          }}>✕</button>
        </div>

        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Hook</div>
          <div style={{
            background: "#1a1a28", border: "1px solid #2a2a3a", borderRadius: 8,
            padding: "12px 16px", color: "#e0e0ff", fontSize: 14, lineHeight: 1.6,
            fontStyle: "italic"
          }}>
            "{idea.fields.Hook}"
          </div>
        </div>

        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Full Script</div>
          <div style={{
            background: "#1a1a28", border: "1px solid #2a2a3a", borderRadius: 8,
            padding: "16px", color: "#ccc", fontSize: 13, lineHeight: 1.8,
            whiteSpace: "pre-wrap", fontFamily: "monospace"
          }}>
            {idea.fields.Script}
          </div>
        </div>

        {idea.fields["Thumbnail Prompt"] && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Thumbnail Prompt</div>
            <div style={{
              background: "#1a1428", border: "1px solid #3a2a4a", borderRadius: 8,
              padding: "12px 16px", color: "#ce93d8", fontSize: 13, lineHeight: 1.6
            }}>
              {idea.fields["Thumbnail Prompt"]}
            </div>
          </div>
        )}

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {idea.fields.Hashtags && idea.fields.Hashtags.split(" ").map(tag => (
            <span key={tag} style={{
              background: "#1a2a1a", color: "#00e676", border: "1px solid #00e67620",
              padding: "3px 10px", borderRadius: 20, fontSize: 11
            }}>{tag}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function IdeaCard({ record, onStatusChange }) {
  const [showScript, setShowScript] = useState(false);
  const f = record.fields;
  const statusColor = STATUS_COLORS[f.Status] || STATUS_COLORS.Pending;

  return (
    <>
      <div style={{
        background: "#0e0e14",
        border: `1px solid ${f.Status === "Pending" ? "#2a2a3a" : statusColor.accent + "30"}`,
        borderLeft: `3px solid ${statusColor.accent}`,
        borderRadius: 12,
        padding: "18px 20px",
        transition: "transform 0.15s, box-shadow 0.15s",
        cursor: "default",
      }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = `0 8px 32px ${statusColor.accent}15`;
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
          <div style={{ flex: 1, marginRight: 12 }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6, flexWrap: "wrap" }}>
              <span style={{
                background: "#1a1a28", color: "#aaa", fontSize: 11,
                padding: "2px 8px", borderRadius: 4, fontWeight: 600
              }}>
                {PLATFORM_ICONS[f.Platform]} {f.Platform}
              </span>
              <span style={{ color: "#666", fontSize: 11 }}>{f.Format}</span>
              {f["Estimated Reach"] && (
                <span style={{
                  color: REACH_COLORS[f["Estimated Reach"]] || "#aaa",
                  fontSize: 11, fontWeight: 700
                }}>
                  ↑ {f["Estimated Reach"]} reach
                </span>
              )}
            </div>
            <h3 style={{ color: "#fff", margin: 0, fontSize: 14, lineHeight: 1.4, fontWeight: 600 }}>
              {f.Title}
            </h3>
          </div>
          <StatusBadge status={f.Status} />
        </div>

        {/* Hook */}
        <p style={{ color: "#888", fontSize: 12, lineHeight: 1.6, margin: "0 0 14px", fontStyle: "italic" }}>
          "{f.Hook?.substring(0, 120)}{f.Hook?.length > 120 ? "..." : ""}"
        </p>

        {/* Engagement stats for Published */}
        {f.Status === "Published" && (
          <div style={{ display: "flex", gap: 16, marginBottom: 14 }}>
            {[
              { label: "Views", val: f.Views },
              { label: "Likes", val: f.Likes },
              { label: "Shares", val: f.Shares },
              { label: "Comments", val: f.Comments },
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#ce93d8" }}>
                  {formatNumber(stat.val)}
                </div>
                <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Rationale */}
        {f.Rationale && (
          <p style={{ color: "#555", fontSize: 11, margin: "0 0 14px", lineHeight: 1.5 }}>
            💡 {f.Rationale}
          </p>
        )}

        {/* Actions */}
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={() => setShowScript(true)}
            style={{
              background: "#1a1a28", color: "#aaa", border: "1px solid #2a2a3a",
              padding: "6px 14px", borderRadius: 6, fontSize: 12, cursor: "pointer",
              fontWeight: 600, transition: "all 0.15s"
            }}
            onMouseEnter={e => { e.target.style.color = "#fff"; e.target.style.borderColor = "#444"; }}
            onMouseLeave={e => { e.target.style.color = "#aaa"; e.target.style.borderColor = "#2a2a3a"; }}
          >
            View Script
          </button>

          {f.Status === "Pending" && (
            <>
              <button
                onClick={() => onStatusChange(record.id, "Approved")}
                style={{
                  background: "#00e67615", color: "#00e676", border: "1px solid #00e67640",
                  padding: "6px 16px", borderRadius: 6, fontSize: 12, cursor: "pointer",
                  fontWeight: 700, transition: "all 0.15s"
                }}
                onMouseEnter={e => { e.target.style.background = "#00e67625"; }}
                onMouseLeave={e => { e.target.style.background = "#00e67615"; }}
              >
                ✓ Approve
              </button>
              <button
                onClick={() => onStatusChange(record.id, "Rejected")}
                style={{
                  background: "#ff444415", color: "#ff4444", border: "1px solid #ff444440",
                  padding: "6px 16px", borderRadius: 6, fontSize: 12, cursor: "pointer",
                  fontWeight: 700, transition: "all 0.15s"
                }}
                onMouseEnter={e => { e.target.style.background = "#ff444425"; }}
                onMouseLeave={e => { e.target.style.background = "#ff444415"; }}
              >
                ✕ Reject
              </button>
            </>
          )}

          {f.Status === "Approved" && (
            <span style={{ fontSize: 11, color: "#00e676", marginLeft: 4 }}>
              ✓ Will be scheduled in next publish run
            </span>
          )}

          {f["Scheduled Date"] && (
            <span style={{ fontSize: 11, color: "#40c4ff", marginLeft: 4 }}>
              📅 {f["Scheduled Date"]}
            </span>
          )}
        </div>
      </div>

      {showScript && <ScriptModal idea={record} onClose={() => setShowScript(false)} />}
    </>
  );
}

export default function ContentPipelineDashboard() {
  const [records, setRecords] = useState(MOCK_RECORDS);
  const [filter, setFilter] = useState("All");
  const [niche, setNiche] = useState("personal finance Kenya");
  const [isRunning, setIsRunning] = useState(false);
  const [runLog, setRunLog] = useState([]);

  const statuses = ["All", "Pending", "Approved", "Scheduled", "Published", "Rejected"];

  const counts = statuses.reduce((acc, s) => {
    acc[s] = s === "All" ? records.length : records.filter(r => r.fields.Status === s).length;
    return acc;
  }, {});

  const filtered = filter === "All" ? records : records.filter(r => r.fields.Status === filter);

  const handleStatusChange = useCallback((id, newStatus) => {
    setRecords(prev => prev.map(r =>
      r.id === id ? { ...r, fields: { ...r.fields, Status: newStatus } } : r
    ));
  }, []);

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setRunLog(["Starting pipeline..."]);

    const steps = [
      { msg: `Scraping trends for "${niche}"...`, delay: 800 },
      { msg: "Found 18 trending items via Serper", delay: 700 },
      { msg: "Generating 5 content ideas with GPT-4o-mini...", delay: 1200 },
      { msg: "Generating thumbnail prompts...", delay: 600 },
      { msg: "Pushing 5 records to Airtable...", delay: 900 },
      { msg: "✅ Pipeline complete — 5 ideas ready for review", delay: 0 },
    ];

    let t = 0;
    for (const step of steps) {
      await new Promise(r => setTimeout(r, t));
      setRunLog(prev => [...prev, step.msg]);
      t = step.delay;
    }

    await new Promise(r => setTimeout(r, 800));

    // Add a mock new idea
    const newIdea = {
      id: `rec_${Date.now()}`,
      fields: {
        Title: `${niche} — the data-backed strategy for 2025`,
        Platform: "LinkedIn",
        Format: "Thread",
        Status: "Pending",
        Hook: `Everyone talks about ${niche}. Almost nobody looks at the actual data. Here's what it says:`,
        Script: `HOOK\nEveryone talks about ${niche}. Almost nobody looks at the actual data.\n\nThread:\n\n1/ The conventional wisdom says X. The data says the opposite...\n\n2/ Three metrics that actually predict success in ${niche}:\n   • Metric A\n   • Metric B  \n   • Metric C\n\n3/ What this means for you in 2025...\n\nCTA: Save this thread. Share if it changed your view.`,
        CTA: "Save this thread.",
        Hashtags: "#DataDriven #Strategy #Growth #2025",
        "Thumbnail Prompt": `Bold data visualization with upward trend, dark background, ${niche} themed`,
        "Thumbnail URL": "",
        "Estimated Reach": "High",
        Rationale: "Data-backed content builds credibility and drives saves.",
        Niche: niche,
      }
    };
    setRecords(prev => [newIdea, ...prev]);
    setFilter("Pending");
    setIsRunning(false);
  };

  return (
    <div style={{
      background: "#07070f",
      minHeight: "100vh",
      fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
      color: "#ccc",
      padding: "0 0 60px"
    }}>
      {/* Header */}
      <div style={{
        background: "#0e0e14",
        borderBottom: "1px solid #1a1a28",
        padding: "20px 32px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 16
      }}>
        <div>
          <div style={{ fontSize: 10, color: "#555", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: 4 }}>
            AUTOMATED CONTENT PIPELINE
          </div>
          <h1 style={{ margin: 0, fontSize: 20, color: "#fff", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Approval Board
          </h1>
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <input
            value={niche}
            onChange={e => setNiche(e.target.value)}
            placeholder="Content niche..."
            style={{
              background: "#1a1a28", border: "1px solid #2a2a3a", color: "#fff",
              padding: "8px 14px", borderRadius: 8, fontSize: 12, fontFamily: "inherit",
              width: 220, outline: "none"
            }}
          />
          <button
            onClick={handleRunPipeline}
            disabled={isRunning}
            style={{
              background: isRunning ? "#1a1a28" : "#f0a500",
              color: isRunning ? "#666" : "#000",
              border: "none", padding: "9px 20px", borderRadius: 8,
              fontSize: 12, fontWeight: 700, cursor: isRunning ? "not-allowed" : "pointer",
              fontFamily: "inherit", letterSpacing: "0.05em", transition: "all 0.2s"
            }}
          >
            {isRunning ? "⟳ RUNNING..." : "▶ RUN PIPELINE"}
          </button>
        </div>
      </div>

      {/* Run log */}
      {runLog.length > 0 && (
        <div style={{
          background: "#080810", borderBottom: "1px solid #1a1a28",
          padding: "12px 32px", fontFamily: "monospace"
        }}>
          {runLog.map((line, i) => (
            <div key={i} style={{
              fontSize: 11, color: i === runLog.length - 1 ? "#00e676" : "#555",
              lineHeight: 1.8
            }}>
              <span style={{ color: "#333", marginRight: 8 }}>{String(i).padStart(2, "0")}</span>
              {line}
            </div>
          ))}
        </div>
      )}

      {/* Stats bar */}
      <div style={{
        display: "flex", gap: 0, borderBottom: "1px solid #1a1a28",
        overflowX: "auto"
      }}>
        {statuses.map(s => {
          const c = STATUS_COLORS[s] || { accent: "#666", text: "#888" };
          const isActive = filter === s;
          return (
            <button
              key={s}
              onClick={() => setFilter(s)}
              style={{
                background: isActive ? "#1a1a28" : "transparent",
                border: "none",
                borderBottom: isActive ? `2px solid ${s === "All" ? "#f0a500" : c.accent}` : "2px solid transparent",
                color: isActive ? "#fff" : "#555",
                padding: "14px 20px",
                cursor: "pointer",
                fontFamily: "inherit",
                fontSize: 12,
                fontWeight: isActive ? 700 : 400,
                whiteSpace: "nowrap",
                transition: "all 0.15s"
              }}
            >
              {s}
              <span style={{
                marginLeft: 8,
                background: isActive ? (s === "All" ? "#f0a50020" : c.bg) : "#1a1a28",
                color: isActive ? (s === "All" ? "#f0a500" : c.text) : "#555",
                padding: "1px 7px", borderRadius: 10, fontSize: 10, fontWeight: 700
              }}>
                {counts[s]}
              </span>
            </button>
          );
        })}
      </div>

      {/* Cards grid */}
      <div style={{ padding: "24px 32px" }}>
        {filtered.length === 0 ? (
          <div style={{ textAlign: "center", color: "#333", padding: "60px 0", fontSize: 14 }}>
            No {filter === "All" ? "" : filter.toLowerCase()} records.
            {filter === "Pending" && <div style={{ marginTop: 8, fontSize: 12 }}>Run the pipeline to generate new ideas.</div>}
          </div>
        ) : (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))",
            gap: 16
          }}>
            {filtered.map(record => (
              <IdeaCard key={record.id} record={record} onStatusChange={handleStatusChange} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}