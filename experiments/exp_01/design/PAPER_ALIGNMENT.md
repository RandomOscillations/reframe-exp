# Paper Alignment

## Thesis

In directionally uncertain autoresearch states, continued local search eventually reaches a frontier. At that point, a structural reframe may produce better research progress than more local edits.

## Base Phase

The base phase must establish the ordinary local-search frontier. It should not stop at first success. It must show how far a strong agent can go with normal autoresearch under the fixed problem framing.

## Control Phase

The control branch starts from the same stuck state and asks the agent to continue normally. This measures whether ordinary continuation after exhaustion can still make meaningful progress.

## Reframe Phase

The reframe branch starts from the same stuck state and gives a structural reframe prompt. This tests whether a changed lens or cross-domain structure helps more than ordinary continuation.

## Why ED Fire Fits

The ED fire testbed has:

- a mechanistic model target,
- real benchmark data,
- global and regional metrics,
- interpretable constraints,
- obvious local-search temptations,
- unresolved regional/fire-regime structure.

This makes it suitable for studying whether reframing helps autoresearch reason beyond local metric hacking.

