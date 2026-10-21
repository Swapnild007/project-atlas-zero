# Settings architecture (design reference)

Status: **design specification only**. This document does not imply that these settings are implemented.

The settings interface should use a mobile-first single-column list with clear icons, large touch targets, readable descriptions and distinct sections. The reference is used for usability principles, not copied assets, branding or layout code.

## Proposed information architecture

| Section | Purpose | Dependency |
| --- | --- | --- |
| General | Theme, language, accessibility | Frontend |
| AI & Models | Configured providers, selection, usage visibility | Provider registry |
| Voice & Languages | Speech preferences and Indian-language options | Speech services |
| Safety & Permissions | Explicit tool approvals and action scopes | Policy engine |
| Account & Security | Authentication, sessions, connected devices | Identity service |
| Devices & Remote Actions | Permissioned remote operations | Device connector |
| Web & Research | Browsing preferences and source transparency | Research agent |
| Knowledge & Storage | Documents, retrieval collections and storage controls | RAG |
| Memory & History | Conversation retention, deletion and export | Storage API |
| Notifications | Task results and alerts | Task runner |
| Diagnostics | User-visible error codes and issue reporting | Observability |
| About | Version, licenses and release status | Release metadata |

## Interaction requirements

- Minimum 44 by 44 CSS pixel touch targets, visible focus indicators, semantic labels.
- Light and dark themes with sufficient text contrast.
- Keyboard and screen-reader support; Hindi, Marathi and English copy can be introduced after localization tests.
- Each settings row opens a functioning detail view. Never display a nonfunctional switch.
- Disabled features must be labeled unavailable, not presented as operational.
- Risky actions require explicit approval and should provide an audit trail.
- Secrets must not be stored in frontend local storage or exposed to browser JavaScript.
- Privacy, data deletion and export must match actual backend behavior.
- Avoid duplicate categories and duplicate navigation entries.

## Delivery sequence

1. Complete and verify backend chat, error handling and authentication.
2. Implement the settings shell with only functional About, diagnostics and supported general preferences.
3. Introduce provider and conversation settings once backed by tested APIs.
4. Add permissions, tools, voice and device controls only when the corresponding systems exist.

## Acceptance criteria

- Every visible enabled control performs its stated action and survives reload when persistence is promised.
- Navigation works on Android-sized screens and desktop.
- Automated tests cover each settings API and critical UI interaction.
- No copy of third-party icons, visual assets, logos or proprietary code.
