# Red Team Skills: developer and install targets.
#
# The skills are plain files (SKILL.md + references + stdlib Python helpers, plus pandoc for document
# conversion), so they need no plugin and no marketplace. `make install-skills` symlinks skills/rt-* into a skills directory that
# Claude Code auto-discovers, so /rt-govern, /rt-intel, ... register as slash commands.
#
#   make install-skills               # into ./.claude/skills (project scope, this repo)
#   make install-skills SCOPE=personal # into ~/.claude/skills (available from this repo path)
#   make uninstall-skills
#   make list-skills
#   make install-codex-skills         # symlink skills/rt-* into ./.agents/skills for Codex (invoke $rt-govern, or /skills)
#   make install-codex-skills SCOPE=personal # into ~/.agents/skills
#   make uninstall-codex-skills
#   make list-codex-skills
#   make install-agents               # symlink agents/rt-* into ./.claude/agents (project scope, this repo)
#   make install-agents SCOPE=personal # into ~/.claude/agents (available from this repo path)
#   make uninstall-agents
#   make list-agents
#   make new-engagement NAME=ENG-2026-020  # scaffold engagements/<slug>/intake.md from the template
#   make render-docx ENG=<id>              # render an engagement's deliverables + intake + engagement to docx (needs pandoc)
#   make install-agent-context DEST=<dir>  # copy the operating-context CLAUDE.md + AGENTS.md into a project
#   make check-docs    # flag AI-written tells in deliverables and docs
#   make test          # run the helper unit tests
#   make format        # prettier --write on markdown
#   make format-check  # prettier --check on markdown

RT_SKILLS := rt-govern rt-intel rt-emulate rt-adapt rt-verify rt-report rt-handoff rt-exposure
RT_AGENTS := rt-engagement-verifier rt-exposure-verifier
REPO_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
INTAKE_TEMPLATE := $(REPO_ROOT)/templates/INTAKE.md

ifeq ($(SCOPE),personal)
  SKILLS_DIR := $(HOME)/.claude/skills
  LINK_TARGET = $(REPO_ROOT)/skills/$(1)
  AGENTS_DIR := $(HOME)/.claude/agents
  AGENT_LINK_TARGET = $(REPO_ROOT)/agents/$(1).md
  CODEX_SKILLS_DIR := $(HOME)/.agents/skills
else
  SKILLS_DIR := $(REPO_ROOT)/.claude/skills
  LINK_TARGET = ../../skills/$(1)
  AGENTS_DIR := $(REPO_ROOT)/.claude/agents
  AGENT_LINK_TARGET = ../../agents/$(1).md
  CODEX_SKILLS_DIR := $(REPO_ROOT)/.agents/skills
endif

.PHONY: install-skills uninstall-skills list-skills install-codex-skills uninstall-codex-skills list-codex-skills install-agents uninstall-agents list-agents new-engagement render-docx install-agent-context check-docs test format format-check

# Copy the operating-context files (templates/CLAUDE.md + templates/AGENTS.md) into an engagement
# project. DEST is the target project root. Refuses to clobber an existing CLAUDE.md or AGENTS.md.
install-agent-context:
	@if [ -z "$(DEST)" ]; then echo "usage: make install-agent-context DEST=/path/to/engagement-project"; exit 1; fi
	@if [ ! -d "$(DEST)" ]; then echo "DEST '$(DEST)' is not a directory"; exit 1; fi
	@for f in CLAUDE.md AGENTS.md; do \
	  if [ -e "$(DEST)/$$f" ]; then echo "refusing to clobber existing $(DEST)/$$f"; exit 1; fi; \
	done
	@cp "$(REPO_ROOT)/templates/CLAUDE.md" "$(DEST)/CLAUDE.md"
	@cp "$(REPO_ROOT)/templates/AGENTS.md" "$(DEST)/AGENTS.md"
	@echo "copied operating-context CLAUDE.md + AGENTS.md into $(DEST)"

# Scaffold a new engagement intake from the template. NAME is the scope_ref (engagement id); it is
# slugified with rt-govern's rule (lowercase, keep [a-z0-9-], collapse other runs to one -). Refuses to
# clobber an existing intake.
new-engagement:
	@if [ -z "$(NAME)" ]; then echo "usage: make new-engagement NAME=ENG-2026-020"; exit 1; fi
	@slug=$$(printf '%s' "$(NAME)" | sed -E 's#.*/##' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//'); \
	if [ -z "$$slug" ]; then echo "NAME '$(NAME)' slugified to empty; use an id like ENG-2026-020"; exit 1; fi; \
	dir="$(REPO_ROOT)/engagements/$$slug"; intake="$$dir/intake.md"; \
	if [ -e "$$intake" ]; then echo "refusing to clobber existing $$intake"; exit 1; fi; \
	mkdir -p "$$dir"; \
	sed -E "s|^- \*\*Engagement ID:\*\*.*|- **Engagement ID:** $(NAME)|" "$(INTAKE_TEMPLATE)" > "$$intake"; \
	echo "created $$intake (engagement id: $(NAME))"; \
	echo "Fill it in, then run  /rt-govern engagements/$$slug/intake.md"

install-skills:
	@mkdir -p "$(SKILLS_DIR)"
	@for s in $(RT_SKILLS); do \
	  ln -sfn "$(call LINK_TARGET,$$s)" "$(SKILLS_DIR)/$$s"; \
	  echo "linked $(SKILLS_DIR)/$$s"; \
	done
	@echo ""
	@echo "Installed $(words $(RT_SKILLS)) skills into $(SKILLS_DIR)."
	@echo "Claude Code picks up new skills live (no restart). Invoke /rt-govern, /rt-intel, ..."
	@echo "Run agents from the repo root so the skills' shared paths resolve."

uninstall-skills:
	@for s in $(RT_SKILLS); do \
	  rm -f "$(SKILLS_DIR)/$$s" && echo "removed $(SKILLS_DIR)/$$s"; \
	done

list-skills:
	@echo "Skills dir: $(SKILLS_DIR)"
	@ls -l "$(SKILLS_DIR)" 2>/dev/null || echo "(nothing installed)"

# Symlink skills/rt-* into a Codex Agent Skills directory it scans (.agents/skills, walked from the working
# directory up to the repo root; Codex follows symlinks). The same SKILL.md files Claude Code uses are valid
# Codex skills. In Codex, invoke a skill with a $ mention ($rt-govern) or browse with /skills; Codex can also
# select one implicitly by its description. There is no /rt-govern slash command in Codex.
install-codex-skills:
	@mkdir -p "$(CODEX_SKILLS_DIR)"
	@for s in $(RT_SKILLS); do \
	  ln -sfn "$(call LINK_TARGET,$$s)" "$(CODEX_SKILLS_DIR)/$$s"; \
	  echo "linked $(CODEX_SKILLS_DIR)/$$s"; \
	done
	@echo ""
	@echo "Installed $(words $(RT_SKILLS)) skills into $(CODEX_SKILLS_DIR)."
	@echo "Restart Codex if they do not appear, then invoke \$$rt-govern, \$$rt-intel, ... (or /skills to browse)."
	@echo "Run Codex from the repo root so the skills' shared paths resolve."

uninstall-codex-skills:
	@for s in $(RT_SKILLS); do \
	  rm -f "$(CODEX_SKILLS_DIR)/$$s" && echo "removed $(CODEX_SKILLS_DIR)/$$s"; \
	done

list-codex-skills:
	@echo "Codex skills dir: $(CODEX_SKILLS_DIR)"
	@ls -l "$(CODEX_SKILLS_DIR)" 2>/dev/null || echo "(nothing installed)"

# Symlink the sub-agents (agents/rt-*.md) into a Claude Code agents directory it auto-discovers. rt-verify
# dispatches rt-engagement-verifier and rt-exposure dispatches rt-exposure-verifier for their
# independent-context passes. Codex has no equivalent named agents.
install-agents:
	@mkdir -p "$(AGENTS_DIR)"
	@for a in $(RT_AGENTS); do \
	  ln -sfn "$(call AGENT_LINK_TARGET,$$a)" "$(AGENTS_DIR)/$$a.md"; \
	  echo "linked $(AGENTS_DIR)/$$a.md"; \
	done
	@echo ""
	@echo "Installed $(words $(RT_AGENTS)) agent(s) into $(AGENTS_DIR)."
	@echo "Claude Code picks up new agents live (no restart). rt-verify and rt-exposure dispatch their verifiers."

uninstall-agents:
	@for a in $(RT_AGENTS); do \
	  rm -f "$(AGENTS_DIR)/$$a.md" && echo "removed $(AGENTS_DIR)/$$a.md"; \
	done

list-agents:
	@echo "Agents dir: $(AGENTS_DIR)"
	@ls -l "$(AGENTS_DIR)" 2>/dev/null || echo "(nothing installed)"

check-docs:
	@python3 skills/_shared/scripts/check_doc_style.py README.md MAINTENANCE.md docs skills templates engagements/DEMO-ENG-2026-014 exposures/DEMO-CVE-2026-0001

test:
	@cd skills/_shared/scripts && python3 -m unittest -q test_validate test_export test_check_doc_style test_pandoc_convert test_pdf_convert

# Render an engagement's human documents to docx (deliverables + intake + engagement). Needs pandoc.
render-docx:
	@if [ -z "$(ENG)" ]; then echo "usage: make render-docx ENG=DEMO-ENG-2026-014"; exit 1; fi
	@dir="$(REPO_ROOT)/engagements/$(ENG)"; \
	if [ ! -d "$$dir" ]; then echo "no engagement dir: $$dir"; exit 1; fi; \
	python3 "$(REPO_ROOT)/skills/_shared/scripts/pandoc_convert.py" to-docx $$dir/deliverables/*.md $$dir/intake.md $$dir/engagement.md

format:
	@npm run format

format-check:
	@npm run format-check 2>/dev/null || npm run format:check
