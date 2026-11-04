# R24: Historical MT5 economic calendar and broker/prop operating clock (non-trading)

## Source contract

The Python learner already computes **fully observed** session clocks using IANA time zones, but these are *nominal session context*, not proof a dealer or proprietary firm allowed orders at a given timestamp. Source-exact raw XAUUSD tick availability and historical quote gaps provide only observed quote readiness. A broker may send quotes when trading is disabled.

The attached `.mq5` is a **manual export script for an ONLINE MT5 chart**, **not a trading EA**. It uses MetaQuotes `CalendarValueHistory` and `CalendarEventById` to collect medium/high impact rows in server time, plus `SymbolInfoSessionTrade` and `SymbolInfoSessionQuote` to snapshot the terminal's **current** weekly template. It records `STATUS.tsv` and fails closed on provider errors. This source has NOT been compiled or run in a MetaEditor or connected Coinexx terminal here. It must not be claimed that historical event data has been collected.

The original four months Jan/Feb/June/July 2026 require **four separate** source-server-time export intervals, with exact broker historical UTC offset mapping independently checked against original tick files. Original R18 uses UTC -2h in Jan/Feb, -3h Jun/Jul and a June UTC calendar tail supplied by raw July monthly file; this source convention alone does not certify the calendar provider server's historical timezone. For historical *as-of* announcement-time features, the release schedule must be shown to have been known before the decision timestamp. A calendar database queried in November 2026 can include retroactively revised historical schedules, actual values and release time; do not include future information in the learner.

**Missing status is UNKNOWN, never zero-news.** No external prop-firm rules have been provided, so operational permission and holidays remain UNKNOWN; current `SymbolInfoSessionTrade` schedules are not historical attestation. Once the OWNER exports MT5 source, pair server time to validated UTC offset intervals, attach source sha256 and field-level availability, and use only pre-announcement fields in as-of features. Run point-in-time and DST tests before attribution by quarter and hour. Market-state and overlapping-session inference based on observed quotes and known IANA DST is permissible as a separate informational input and already supported in R24 features.

## Exact official references

- https://www.mql5.com/en/docs/calendar/calendarvaluehistory
- https://www.mql5.com/en/docs/calendar/calendareventbyid
- https://www.mql5.com/en/docs/constants/structures/mqlcalendar
- https://www.mql5.com/en/docs/marketinformation/symbolinfosessiontrade
- https://www.mql5.com/en/docs/marketinformation/symbolinfosessionquote
- https://www.mql5.com/en/book/advanced/calendar (notes Strategy Tester calendar API unavailable; export on online chart then load externally).
