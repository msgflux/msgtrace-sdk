# Automation Guide

This document describes all automated workflows configured for msgtrace-sdk.

## 🤖 Configured Automations

### 1. **Dependabot** - Dependency Updates

**File**: `.github/dependabot.yml`

**What it does**:
- Automatically checks for dependency updates weekly (Mondays at 9am UTC)
- Creates PRs for Python dependencies and GitHub Actions
- Groups OpenTelemetry packages together
- Groups dev dependencies by type (minor/patch)

**Labels**: `dependencies`, `python`, `github-actions`

**Configuration**:
- Max 10 PRs for Python deps
- Max 5 PRs for GitHub Actions
- Auto-labeled with `automerge` for automated merging

---

### 2. **Pre-commit Auto-update** - Hook Updates

**File**: `.github/workflows/pre-commit-autoupdate.yml`

**What it does**:
- Runs `pre-commit autoupdate` weekly (Mondays at 9am UTC)
- Creates PR with updated hook versions
- Automatically labeled with `automerge`

**Triggers**:
- Schedule: Weekly (Mondays)
- Manual: `workflow_dispatch`

---

### 3. **Merge Bot** - Command-based PR Merging

**File**: `.github/workflows/merge-bot.yml`

**What it does**:
- Merges PRs via comment commands (PyTorch-style)
- Waits up to 10 minutes for CI checks to pass
- Checks user permissions (write/admin only)
- Uses squash merge
- Deletes branch after merge
- Interactive feedback with emoji reactions

**Commands**:
- `@mergebot merge`
- `@merge-bot merge`
- `/merge`
- `merge`

**See**: `MERGE_BOT_GUIDE.md` for detailed usage

---

### 4. **Stale Bot** - Issue/PR Cleanup

**File**: `.github/workflows/stale.yml`

**What it does**:
- Marks issues as stale after 60 days of inactivity
- Closes stale issues after 7 days
- Marks PRs as stale after 30 days
- Closes stale PRs after 14 days
- Removes stale label when updated

**Exempt labels**: `keep-open`, `bug`, `security`, `enhancement`, `help-wanted`, `in-progress`, `work-in-progress`

**Triggers**:
- Schedule: Daily at midnight UTC
- Manual: `workflow_dispatch`

---

### 5. **Label Automation** - Auto-labeling

**Files**:
- `.github/workflows/labeler.yml`
- `.github/labeler.yml`

**What it does**:
- **File-based labeling**: Labels based on changed files (sdk, core, tests, docs, ci, dependencies, examples)
- **Size labeling**: Adds size labels (XS/S/M/L/XL) based on line changes
- **Title-based labeling**: Detects conventional commit prefixes (feat, fix, docs, etc.)
- **Keyword detection**: Detects breaking changes, security issues

**Labels added automatically**:
- `sdk`, `core`, `tests`, `documentation`, `ci`, `dependencies`, `examples`
- `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL`
- `enhancement`, `bug`, `maintenance`, `refactor`, `performance`
- `breaking-change`, `security`

---

### 6. **CodeQL Security Scanning**

**File**: `.github/workflows/codeql.yml`

**What it does**:
- Scans Python code for security vulnerabilities
- Runs on pushes to main, PRs, and weekly schedule
- Uses `security-extended` queries for comprehensive checking
- Reports findings in Security tab

**Triggers**:
- Push to main
- Pull requests
- Schedule: Weekly (Mondays at 3am UTC)

**Results**: View in GitHub Security tab

---

### 7. **Release Drafter** - Draft Release Notes

**Files**:
- `.github/workflows/release-drafter.yml`
- `.github/release-drafter.yml`

**What it does**:
- Automatically drafts release notes based on merged PRs
- Categorizes changes by type (Features, Bug Fixes, Docs, etc.)
- Suggests version bump (major/minor/patch) based on labels
- Lists contributors

**Categories**:
- 🚀 Features (`enhancement`, `feat`)
- 🐛 Bug Fixes (`bug`, `fix`)
- 📚 Documentation (`documentation`, `docs`)
- 🧪 Tests (`tests`, `test`)
- ⚡ Performance (`performance`, `perf`)
- 🔧 Maintenance (`maintenance`, `chore`)
- 🔐 Security (`security`)
- 📦 Dependencies (`dependencies`)

**View**: Check GitHub Releases page for draft

---

### 8. **Changelog Generator** - Auto-update CHANGELOG

**File**: `.github/workflows/changelog.yml`

**What it does**:
- Automatically updates CHANGELOG.md when PRs are merged
- Adds entry under appropriate section (Added/Fixed/Changed/etc.)
- Includes PR title and number
- Commits directly to main

**Sections**:
- Added (features)
- Fixed (bug fixes)
- Changed (modifications)
- Security (security fixes)
- Deprecated
- Removed

**Triggers**: When PR is closed and merged to main

---

## 🎯 Workflow Summary

| Workflow | Trigger | Frequency | Auto-action |
|----------|---------|-----------|-------------|
| Dependabot | Schedule | Weekly (Mon 9am) | Creates PRs |
| Pre-commit update | Schedule | Weekly (Mon 9am) | Creates PRs |
| Merge Bot | PR comment | On command | Merges PRs |
| Stale bot | Schedule | Daily | Closes stale items |
| Labeler | PR open/update | On PR | Adds labels |
| CodeQL | Push/PR/Schedule | Weekly (Mon 3am) | Security scan |
| Release Drafter | Push to main | On push | Drafts release |
| Changelog | PR merged | On merge | Updates CHANGELOG |

---

## 🏷️ Important Labels

- `keep-open` - Prevents stale bot from closing
- `dependencies` - Dependency updates
- `breaking-change` - Triggers major version bump
- `security` - Security-related changes
- `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` - PR size indicators

---

## 🚀 Usage Examples

### Merge a PR with bot
```bash
# Comment on PR:
@mergebot merge
# or
/merge
```

### Prevent stale bot from closing
```bash
gh issue edit <issue-number> --add-label "keep-open"
```

### Trigger pre-commit update manually
```bash
gh workflow run pre-commit-autoupdate.yml
```

---

## 📊 Monitoring

- **CI Status**: Check Actions tab for workflow runs
- **Security**: Check Security tab for CodeQL findings
- **Dependencies**: Check Pull Requests for Dependabot updates
- **Release Notes**: Check Releases page for draft release notes

---

## ⚙️ Configuration Files

All automation configurations are in `.github/`:

```
.github/
├── dependabot.yml              # Dependency updates
├── labeler.yml                 # File-based labeling rules
├── release-drafter.yml         # Release notes configuration
└── workflows/
    ├── merge-bot.yml           # Merge bot (command-based)
    ├── changelog.yml           # Changelog updates
    ├── codeql.yml              # Security scanning
    ├── labeler.yml             # Label automation
    ├── pre-commit-autoupdate.yml  # Pre-commit updates
    ├── release-drafter.yml     # Release drafter
    └── stale.yml               # Stale bot
```

---

## 🔧 Customization

To customize automations, edit the respective configuration files and commit changes. Most workflows support manual triggers via `workflow_dispatch`.

---

## 📝 Best Practices

1. **Use conventional commits** for automatic changelog updates
2. **Use merge bot commands** to merge PRs after CI passes
3. **Use `keep-open` label** for long-running issues/PRs
4. **Review Dependabot PRs** before merging (check breaking changes)
5. **Check CodeQL findings** regularly in Security tab
