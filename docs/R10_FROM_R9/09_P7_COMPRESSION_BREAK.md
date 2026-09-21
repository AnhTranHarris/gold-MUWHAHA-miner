# Checkpoint 09 — P7 Compression Break

P7 is restored as executable code rather than being omitted from the post-R9 stack.

Reconstructed mechanism:
1. measure a completed short-horizon compression range;
2. normalize that range by completed ATR;
3. reject ranges that are too dead or already too expanded;
4. require price to break outside the known range by an ATR-scaled buffer;
5. treat that break as an auction event;
6. pass it through the same CONTINUE / FADE / ABSTAIN action router, catastrophe memory and portfolio heat.

The exact original P7 Python coefficients were not preserved. Defaults are reconstructible architectural values cross-checked against the open-source GoldLondonBreakout ATR-normalized compression/breakout design and must be re-certified on our Jan-Jul REAL corpus.

P7 uses the 1-minute portfolio scale, so it cannot stack on top of another live 1-minute sleeve merely because it is a different signal name.
