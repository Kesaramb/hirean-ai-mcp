# Changelog

## 0.2.0

- Rebrand the product and MCP server identity as HireAn AI.
- Rename the distribution and primary command to `hirean-ai-mcp`, and the Python
  package to `hirean_ai_mcp`.
- Add `HIREAN_AI_API_URL`, `HIREAN_AI_TIMEOUT` and `HIREAN_AI_DRAFT_FOLDER`, with
  fallback to the existing `CAPCUT_*` settings.
- Retain the `capcut-mcp` command and `capcut_mcp.server` launch entry point.
- Update setup instructions and the included video workflow references.
- Add development installation instructions and scope test discovery to this
  project's tests, independently of the external backend checkout.

## 0.1.0

- Initial CapCut MCP implementation: 14 tools for editable video projects,
  VectCutAPI error handling, draft saving and status polling.
