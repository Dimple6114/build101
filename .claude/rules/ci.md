---
paths:
  - ".github/workflows/**"
  - "**/.github/workflows/**"
---

> Adapted from [guidodinello/claude-dotfiles `rules/ci.md`](https://github.com/guidodinello/claude-dotfiles/blob/main/.claude/rules/ci.md) (MIT, see [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)).

<!-- Code examples and table rows can't be rewrapped without breaking them;
     prose is held to 80 columns. This directive travels with the file so it
     lints clean in any repo that vendors it. Claude Code strips block HTML
     comments before injection, so this costs no context. -->
<!-- markdownlint-configure-file {
  "MD013": { "code_blocks": false, "tables": false }
} -->

# CI — Agent Authoring Guidelines

Guidelines for writing and modifying GitHub Actions workflows
(`.github/workflows/`), and the reasoning behind them, so they can be applied
consistently as a pipeline grows. build101 uses GitHub-hosted runners.

---

## Philosophy

- **Fail loudly, gate explicitly.** A job that silently skips or a summary gate
  that doesn't actually check its dependencies' results is worse than a red X.
- **Only run what changed.** Independent pipelines (e.g. backend and frontend)
  shouldn't pay for or block on a job whose inputs didn't change.
- **Least privilege by default.** A workflow file should state what its
  `GITHUB_TOKEN` can do, not silently inherit whatever the repo/org default
  scope happens to be.

---

## Least-privilege permissions

Add an explicit `permissions:` block to every workflow. Without one, every job
runs with the repo/org default `GITHUB_TOKEN` scope — often broader read/write
access than anything in the file actually uses, and that default can change
out from under you if the org setting changes later.

Set the workflow-level default to the narrowest shape most jobs need
(`contents: read` covers checkout + run-tools-and-exit, which is most CI),
then override per-job only where something genuinely needs more:

```yaml
# Bad — no permissions block; every job gets the repo's default GITHUB_TOKEN
# scope, whatever that happens to be
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

# Good — explicit, narrowest-common-denominator default; override per job
name: CI
on: [push, pull_request]
permissions:
  contents: read
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write   # only this job pushes an image
    steps: [...]
```

**A job-level `permissions:` replaces the workflow-level default entirely for
that job — it does not add to it.** Copy the base entries (`contents: read`)
into any job override that also needs something extra; don't rely on them
being inherited alongside it.

| Job does | Needs |
|---|---|
| Checkout + run linters/tests, nothing else | `contents: read` |
| Push a Docker image or package | `packages: write` |
| Merge, comment on, or push to a PR | `pull-requests: write` (+ `contents: write` to merge) |
| Auth via OIDC to a third-party action (e.g. `anthropics/claude-code-action`) | `id-token: write` |
| Pure SSH/external deploy — no GitHub API calls at all | nothing; `permissions: {}` makes that explicit |

A custom PAT passed via `secrets.SOME_PAT` (not `secrets.GITHUB_TOKEN`) is
unaffected by this block entirely — its scope is whatever was granted when
the token was created, configured outside the workflow file.

---

## Path filtering

Use `dorny/paths-filter` behind a `changes` job so backend and frontend
pipelines only run when their own tree changed:

```yaml
changes:
  outputs:
    backend: ${{ steps.filter.outputs.backend }}
    frontend: ${{ steps.filter.outputs.frontend }}
  steps:
    - uses: dorny/paths-filter@v4
      id: filter
      with:
        filters: |
          backend:
            - 'backend/**'
            - '.github/workflows/ci.yml'
          frontend:
            - 'frontend/**'
            - '.github/workflows/ci.yml'
```

Every downstream job gates on it: `needs: changes` + `if:
needs.changes.outputs.backend == 'true'`. Always include the workflow file
itself (`.github/workflows/ci.yml`) in each filter's path list — a workflow
change should re-run everything it affects, not be invisible to path filtering.

---

## Summary gates

A summary gate job exists purely so branch protection can require one check
instead of enumerating every job. It must use `if: always()` and explicitly scan
`needs.*.result` — without `always()`, the gate job is skipped (not failed) the
moment any dependency fails, which branch protection treats as "no status," not
"blocked."

```yaml
backend-gate:
  needs: [lint, typecheck, test-unit, test-integration]
  if: always()
  steps:
    - name: Check results
      run: |
        results=(${{ join(needs.*.result, ' ') }})
        for r in "${results[@]}"; do
          if [[ "$r" == "failure" || "$r" == "cancelled" ]]; then
            exit 1
          fi
        done
```

When adding a new job to a pipeline, add it to the matching summary gate's
`needs:` list too — a job left out of the gate can fail without blocking the
merge.

---

## Quick reference checklist

When authoring or reviewing a workflow file:

- [ ] Workflow has an explicit `permissions:` block (no reliance on the repo/
  org default)
- [ ] Any job overriding `permissions:` repeats the base entries it still
  needs — a job-level block replaces the default, it doesn't add to it
- [ ] New job is gated behind the `changes` job with the right `if:
  needs.changes.outputs.*`
- [ ] New job's path is listed in the relevant `paths-filter` filter, and the
  workflow file itself is included in that filter's path list
- [ ] New job is added to the matching summary gate's `needs:` list
- [ ] Summary/gate jobs use `if: always()` and explicitly check `needs.*.result`
