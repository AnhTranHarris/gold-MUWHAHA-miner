# DELTA-B USD Scheduled Event Taxonomy V1

Status: **FROZEN RESEARCH INPUT — NOT A UNIVERSAL MARKET-IMPACT STANDARD**

## Purpose

This taxonomy gives Grid Layer 1 a reproducible, causal scheduled-event state for January-July 2026 without depending on a live calendar API during historical replay.

Official release timestamps are taken from primary schedules where available. The DELTA-B `HIGH` / `MEDIUM` severity label is a project research classification, not a claim that all third-party calendars use the same impact label.

## Timestamp Authority

Primary sources:

- BLS 2026 release calendar: https://www.bls.gov/schedule/2026/
- Census 2026 Economic Indicator calendar: https://www.census.gov/economic-indicators/calendar-listview.html
- BEA full 2026 release schedule: https://www.bea.gov/news/schedule/full
- Federal Reserve FOMC calendars / monthly calendars: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- U.S. Department of Labor ETA weekly claims archive: https://www.dol.gov/newsroom/releases/eta

All listed source times are interpreted in U.S. Eastern Time when the source states Eastern Time. The frozen cache stores both Eastern wall-clock and normalized UTC.

## HIGH

DELTA-B treats these event families as HIGH:

- FOMC policy decision / statement
- FOMC press conference
- Employment Situation
- CPI
- JOLTS Job Openings
- Initial Jobless Claims
- Advance Retail Sales
- Personal Income and Outlays / PCE
- GDP Advance Estimate

Rationale: these directly affect rates, inflation, employment, growth, or broad USD repricing and can materially change XAUUSD spread, velocity, and directional persistence.

## MEDIUM

DELTA-B treats these event families as MEDIUM:

- FOMC Minutes
- Federal Reserve Beige Book
- Producer Price Index
- Employment Cost Index
- GDP updated / second / third estimates
- U.S. international trade balance
- Advance Durable Goods Orders
- New Residential Construction / Housing Starts
- New Residential Sales

These events do not own direction. They only alter Grid context and operating authority.

## Intentionally Not Encoded as Direction

No calendar row contains:

- expected BUY/SELL direction
- actual-vs-consensus surprise sign as a pre-release feature
- future post-event return
- future spread widening
- future MFE/MAE

A later event specialist may consume actual released values only after a causally observable timestamp and under a separate contract.

## Scope Boundary

V1 is a **core scheduled USD macro cache** built from official primary schedules plus the frozen DELTA-B impact taxonomy. It is not yet an exhaustive clone of every third-party calendar's Medium/High list.

Examples intentionally deferred from V1 unless independently sourced into a later version:

- every Federal Reserve governor speech
- private-sector ISM / ADP / Conference Board releases
- every regional Fed survey
- Treasury auctions
- energy inventory releases

This is deliberate. V1 is for measuring whether the grid's session/event adaptation works mechanically and economically before increasing calendar breadth.

## Weekly Claims Rule

Initial Jobless Claims are scheduled each Thursday at 08:30 U.S. Eastern in the research interval. Individual DOL release pages are the timestamp authority; V1 encodes the Thursday schedule for January 8 through July 30, 2026.

## Versioning

Any change to:

- event membership,
- severity,
- timestamp,
- timezone interpretation,
- or event family

requires a new taxonomy/cache version. Do not silently edit V1 after a result has been produced from it.

August 2026 remains SEALED and is excluded.
