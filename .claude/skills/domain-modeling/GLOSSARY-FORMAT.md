# docs/glossary.md Format

build101 has a single context, so there is one glossary: [`docs/glossary.md`](../../../docs/glossary.md).

## Structure

```md
# Glossary

{One or two sentence description of what this product is and why the language matters.}

## Language

**Owner**:
{A one or two sentence description of the term}
_Avoid_: User, admin, client

**Staff member**:
A person who works for the Owner's business and can receive delegated tasks.
_Avoid_: Employee, worker, team member

**Supplier**:
An external business the Owner buys goods or services from.
_Avoid_: Vendor, provider
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this product, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge (e.g. People, Operations, Channels). If all terms belong to a single cohesive area, a flat list is fine.
- **Mark unsettled terms.** While the idea is still being refined, a term that is in use but not yet agreed can carry `_Status_: draft` under its definition. Remove the marker once the team agrees.
