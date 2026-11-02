# Development instructions

- Read HANDOFF_RU.md before changing code/data. User language is Russian.
- Preserve evidence and source provenance. Never invent item drop probabilities, sources, gate requirements, or world coordinates.
- data.js is the current complete recovered dataset. Old migration/packaging scripts are not an idempotent build pipeline.
- Run npm run check after changes. Check changed UI flows in a browser.
- Research bundles must never include public-config.json, credentials, .env, raw game binaries or .git authentication state.
- This checkout is independent of the original private Sites deployment. Do not reuse its project ID or change its audience.
