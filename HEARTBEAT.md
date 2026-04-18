# HEARTBEAT.md - Active Tasks Monitor
Updated: 2026-04-18 17:30 HKT

## Polymarket Elon Tracker (xTracker Clone) - Updated 2026-04-18 17:30 HKT
- **Repo**: `polymarket-elon-tracker/` (独立实时追踪器)
- **架构**:
  - `simple_collect.py` — Tweet采集 via Node.js + openclaw CLI (`node .../openclaw.mjs browser evaluate`)
  - `beval_collect.py` — 备用采集方案（通过PowerShell）
  - `src/database.py` — SQLite持久化
  - `src/analyzer.py` — 3情景MC + Kelly
  - `quick_check.py` — 快速分析入口 (用 `python quick_check.py` 在tracker目录)
- **Browser Relay**: Chrome tab `B8795CA0F4574E46F3E6F21B1D5F8F4E` at x.com/home
- **DB**: `data/tracker.db` (69 tweets)
- **当前状态**: 81 tweets collected this run, 69 unique total. Elon's last post Apr17 22:42 GMT — no new Elon posts detected.
- **Tracker状态**: Working, but tweets from general home feed (not Elon-specific filter)
- **Analyzer**: ✅ Works (P=96-100%, Kelly=23-25%)
- **覆盖校正**: 1.909x (xtracker Apr16-18=42 / BrowserRelay=22)
- **真实日均**: ~57 tweets/day

### 每小时采集 (HEARTBEAT任务)
1. `simple_collect.py` — 通过Node.js CLI执行browser evaluate，8次滚动采集
   - `python simple_collect.py 8` 在tracker目录
2. 结果存: `data/tweets_latest.json` + `output/latest_snapshot.json`
3. 边缘>15%时发送飞书警报

### 市场信号
| 市场 | 目标 | xtracker | 价格 | P(YES) | 边缘 | Kelly¼ |
|------|------|----------|------|--------|------|--------|
| Apr14-21 | 190 | 116 | 57% | ~96% | +39% | 20% |
| Apr17-24 | 200 | 7 | 50% | ~100% | +50% | 25% |
| May2026 | 800 | 0 | 50% | ~100% | +50% | 25% |

### 采集命令
```bash
python "C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\simple_collect.py" 8
```
Node路径: `C:\Program Files\nodejs\node.exe`

### Lucky Defense Game
- **Path**: `lucky-defense/` (standalone)
- **Type**: Single-file HTML5 tower defense + merge game
- **Status**: APK built (v3, 3.9MB)
- **Features**: 5 lanes, 6 defender types, 5 tiers auto-merge, 10 rounds
- **Mobile**: Capacitor Android APK, full-screen, touch optimized

## Active Projects

### FormForge (AI Form Filler)
- **Repo**: https://github.com/TeapoyY/ai-form-filler
- **Stack**: FastAPI + PyMuPDF + PaddleOCR + Ollama (gemma3:1b + minicpm-v)
- **Status**: 鉁?2-step E2E working; Vision endpoint intermittent
- **Backend**: port 8001 ✅ (was DOWN, now UP)
- **OCR**: PyMuPDF text 鉁?| PaddleOCR 3.4.0 + paddlepaddle 3.0.0 鉁?(~37s cold-start) | DeepSeek OCR 0.3.0 (needs DS_OCR_API_KEY) | EasyOCR disabled
- **LLM**: Ollama gemma3:1b (text) + minicpm-v (vision) 鈥?direct localhost, no proxy
- **E2E**: 12/12 EN10204 鉁?(2-step: OCR ~3s + extract ~10s)
- **鈿狅笍 Vision endpoint**: Intermittently hangs when calling Ollama minicpm-v from FastAPI. Direct Ollama calls work fine (~20s). Root cause unclear 鈥?possibly httpx async threading issue. 2-step path is the reliable workhorse.
- **鈿狅笍 Python PATH**: WindowsApps stub 鈫?鐢ㄥ畬鏁磋矾寰?`C:\...\Python311\python.exe`
- **Server**: `cd backend && python start_ff.py` (uses .env for PORT=8001, OLLAMA_VISION_MODEL=minicpm-v)
- **Setup after clone**: Copy `.env.example` 鈫?`.env`, run `backend/create_test_samples.py`

### Douyin Game Forge (鎶栭煶娓告垙宸ュ潑) 馃啎
- **Repo**: https://github.com/TeapoyY/douyin-game-forge
- **Stack**: Node.js/Express (8010) + React 18 + Vite + TypeScript (3000)
- **Status**: 鉁?Backend+Frontend running
- **Issue**: Claude Code not called - uses hardcoded fallback puzzle/2048 template
- **Bugs**: Chinese encoding garbled in API responses
- **Path Fix**: outputDir = `..\..\..\output` (4 levels up from backend/)
- **Test**: Create survivor-like 鈫?generates puzzle game instead

### LearnAny
- **Repo**: https://github.com/TeapoyY/learn-any
- **Stack**: FastAPI + MiniMax + 鍗曟枃浠?SPA
- **Status**: 鉁?Running (port 8003)
- **鍔熻兘**: 璐规浖+鑻忔牸鎷夊簳娓愯繘瀛︿範寮曟搸

### AI News / WorldPredict
- **Repos**: ai-news, world-predict
- **Status**: 鉁?Running
- **Ports**: 8002 (news), 8011 (wp), 3002/3004 (frontend)

### Parallax Train Widget
- **Repo**: https://github.com/TeapoyY/parallax-train-widget
- **Status**: 鉁?
## Bounty Hunt 鈿狅笍
1. Find: BountyHub.dev / Algora.io
2. **Verify real money**: `bounty` label 鈮?cash!
3. Claude Code: `claude --print "implement..."`
4. PR verification: `gh pr list --author TeapoyY`

### Active PRs (verified 2026-04-18 17:25 HKT)
- **#887** OPEN: `feat(frontend): live countdown timer + search bar` (TeapoyY)
  - Combined T1 bounty: countdown timer #826 + search bar #823 + mobile polish #824
  - Label: `missing-wallet`
- **#875** OPEN: `[Bounty] T1: Fix GitHub OAuth Sign-In Flow` (TeapoyY)
  - CodeRabbit review: docstring coverage warning (50% < 80% threshold)
  - Needs docstrings to pass pre-merge

### SolFoundry Bounty Status (2026-04-18 17:25 HKT)
- **#831** OPEN: `🏭 Bounty T1: Animated GIF of Bounty Creation Flow`
  - PR #1032 (lui62233) — closed, submitted GIF (603KB, 10-frame)
  - PR #1039 (denishpt) — closed, submitted GIF
  - Both closed, issue still open — may need re-submission
- **#834** OPEN: Same title as #831, opened Apr 8 — possible duplicate
- Bounty board: https://www.algora.io/bounties?org=SolFoundry

## Cron Jobs
| Job | Schedule | Status |
|-----|----------|--------|
| gateway-keepalive | every 10m | 鉁?|
| bounty-hunt-monitor | every 1h | 鉁?|
| ai-money-hunter | every 1h | 鉁?|

---

## Self-Improvement Loop (Hermes-style) 鈿?NEW

### 缁勪欢 (4 Skills)
| Skill | 鍔熻兘 | 瑙﹀彂 |
|-------|------|------|
| auto-skill-creator | 浠庡鏉備换鍔″垱寤?Skill | tool_calls >= 5 |
| memory-guardian | 鏈夌晫璁板繂 + 鑷姩绮剧畝 | >80% 鏃剁簿绠€ |
| session-archivist | 浼氳瘽褰掓。 + 鎼滅储 | 姣?30 鍒嗛挓 |
| nudge-memory | 鍛ㄦ湡鎬т繚瀛樻彁閱?| 姣忓皬鏃?HEARTBEAT |

### HEARTBEAT 妫€鏌ユ竻鍗?(鎸夐『搴?

**姣?30 鍒嗛挓:**
- [ ] 妫€鏌ユ槸鍚﹂渶瑕佸綊妗ｅ綋鍓嶄細璇?(session-archivist)
- [ ] 妫€鏌ユ槸鍚﹂渶瑕佸垱寤烘柊 Skill (auto-skill-creator)

**姣忓皬鏃?**
- [ ] MEMORY.md 浣跨敤鐜囨鏌?(memory-guardian)
  - 濡傛灉 >70%: 鎻愮ず consolidation
  - 濡傛灉 >80%: 鎵ц consolidation
- [ ] 閲嶈鐭ヨ瘑淇濆瓨鎻愰啋 (nudge-memory)
- [ ] USER.md 浣跨敤鐜囨鏌?
**姣忓ぉ (棣栨 HEARTBEAT):**
- [ ] 鍥為【鏄ㄥぉ鍏抽敭杩涘睍
- [ ] 娓呯悊杩囨椂 MEMORY 鏉＄洰
- [ ] 妫€鏌?session archives 鎼滅储鑳藉姏

### 淇濆瓨瑙勫垯
| 鍐呭 | 浣嶇疆 |
|------|------|
| 宸ュ叿鎶€宸?| TOOLS.md |
| 琛屼负妯″紡 | SOUL.md |
| 宸ヤ綔娴佹敼杩?| AGENTS.md |
| 鏅亶鏁欒 | .learnings/LEARNINGS.md |
| 鍛戒护閿欒 | .learnings/ERRORS.md |
| 鐢ㄦ埛璇锋眰 | .learnings/FEATURE_REQUESTS.md |

### 瀹归噺闄愬埗
- MEMORY.md: **4,000 chars** (80% of 5,000)
- USER.md: **2,400 chars** (80% of 3,000)
- 瓒呭嚭 鈫?鑷姩 consolidation

---

## Service Ports
| Port | Service | Status |
|------|---------|--------|
| 8001 | FormForge backend | ✅ Listen (PID 2208, confirmed 09:36) |
| 8002 | AI News backend | ✅ Listen (PID 6768, confirmed 11:55) |
| 8003 | LearnAny backend | ✅ Listen (PID 10800, confirmed 11:55) |
| 8010 | Douyin Game Forge backend | ❌ Project dir removed from workspace |
| 8011 | WorldPredict backend | ✅ Listen (PID 24088, confirmed 11:55) |
| 3000 | Douyin Game Forge frontend | ❌ Project removed |
| 3002/3004 | AI News/WorldPredict frontend | 鉁?|
