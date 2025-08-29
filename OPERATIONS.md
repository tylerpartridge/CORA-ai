# OPERATIONS

## Bootup Discipline
- Bootup must honor Optional block: `# present` → hydrate, `# optional` → skip

## Checkpoint Discipline

### Mandatory Checkpoint Rules
- **Before merges** → Must have valid checkpoint in all awareness files
- **Before major operations** → Database migrations, production deploys, architecture changes
- **Before multi-agent tasks** → Deploy checkpoint before parallel agent operations
- **Before handoffs** → AI session transfers require synchronized awareness state

### Checkpoint Requirements
- All 5 core files updated: STATE.md, NEXT.md, AI_WORK_LOG.md, HANDOFF.md, AIM.md
- Each file must have checkpoint capsule with timestamp and status
- Files must be synchronized and consistent across all awareness data

### Compaction & Archiving Policies
- **AI_WORK_LOG.md** → Archive when >300 lines, keep last 2 weeks active
- **SPARKS.md** → Prune completed items every Friday
- **NEXT.md** → Prune at sprint close, archive old priorities

**Reference:** Complete checkpoint system defined in `/docs/ai-awareness/CHECKPOINT_SYSTEM.md`

## TLS Renewal

Renew Let's Encrypt TLS **before Sep 19, 2025**.

**Commands:**
sudo certbot renew --dry-run
sudo certbot renew

**Reference:** nginx on :443; renewal managed on the prod droplet.
