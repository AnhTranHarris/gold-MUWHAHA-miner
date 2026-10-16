# CHAT TRANSCRIPT CAPTURE FORMAT v1.3 — DATA CONTRACT, NOT A CHAT EXPORT
## Status fields
- export_id: <UUID or verified stable ID>
- captured_utc: <actual timestamp if known; never invent>
- source_session_url: <known URL, otherwise UNAVAILABLE>
- source_type: CHAT_VISIBLE_MESSAGES | USER_SUPPLIED_FULL_EXPORT | MANUAL_EXACT_COPY
- coverage: COMPLETE_VERIFIED | PARTIAL_VISIBLE | NONE_AVAILABLE
- first_accessible_message: <role + ordinal>
- last_accessible_message: <role + ordinal>
- known_unavailable_spans: <explicit description>
- attachments_manifest: <path/hash or source URL for every visible attachment>
- evidence_sha256: <compute over actual exported bytes>
- source_sha256: <if an authenticated original export can be checked>
- cloud_destination_id: <actual Google Drive ID on verified upload, else NOT_UPLOADED>
- note: self-summary has NO authority to fill absent messages.

## Actual messages — APPEND verbatim, one record per message
### MESSAGE 000001
ROLE: USER | ASSISTANT | TOOL
TIME_UTC: <actual value if present, otherwise NOT_AVAILABLE>
ORIGINAL_MESSAGE_ID: <exact value if available, otherwise NOT_AVAILABLE>
BODY_FORMAT: Markdown/plain/text/JSON
SOURCE_COMPLETENESS: EXACT_AVAILABLE | TRUNCATED | ABSENT

<verbatim body from accessible original; escape only if necessary to preserve meaning. No paraphrasing. Use a raw attachment for huge binary content and hash its original bytes.>

ATTACHMENTS: <exact original locations and checksums>
---

## Integrity and boundary checks
- Never populate verbatim bodies from remembered paraphrases or AI-written recovery notes.
- Mark assistant-generated planning/conclusions as actual assistant messages if present; no backdating or filling omitted messages.
- Include original user requests, source URLs, exact command lines, error logs, code and parameter tables if they are actually visible.
- Conversation interfaces may not expose full history or tool invocation details. If absent, record as UNAVAILABLE; request an actual export for COMPLETE_VERIFIED.
- Chunk long captures into numbered .md parts without dropping lines; maintain `TRANSCRIPT_PARTS_MANIFEST.json` with per-file SHA-256/byte size/line counts and deterministic ordered part IDs.
- Preserve raw export separately; any Markdown conversion is a derived representation with its own hash. Annotate conversion fidelity and lost metadata explicitly.
