---
source_file: <path/name of the source, relative to the archive root>
source_origin: <the URL / forum thread / provider the source came from, or `unknown`>
scale: <pages for a PDF, duration for a transcript, token/row count for an API dump>
read_status: <fully-read YYYY-MM-DD | partial YYYY-MM-DD — pages A–B unread, <what's missing>>
sensitivity: <public | internal | contains-credentials>
---

# <human title of the content>

## One-line
<one sentence — the hook the master index shows for this source>

## Summary
<what it teaches / claims / contains: the full thread of steps or the shape of the data, enough
that the next agent can act without reopening the source>

## Key technical details
<commands, config snippets, version numbers, ports, prices, exact identifiers — transcribed
precisely, INCLUDING values that appear only inside screenshots/terminal captures>

## Source-only (image / chart / screenshot) — REQUIRED
<the facts that live only in the visual layer and are absent from any text extraction. If the
source has no visual-only information, write "none — text layer is complete." Never leave blank:
a blank here is the failure mode this section exists to catch (principle 42).>

## Relevance to this project
<why it matters to the current work, with risk notes; what is directly usable vs background>

## Limits & caveats
<what's stale, what the source's own replies/errata corrected, what was NOT captured (e.g. an
export that stopped mid-thread), and the condition under which the source must be re-read>
