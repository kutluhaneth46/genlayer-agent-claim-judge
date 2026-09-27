# Agent Claim Judge Â· Evidence Court (v2)

Builder: **KutluhanETH**

Multi-step GenLayer Intelligent Contract:
filing â†’ evidence (1-3 URLs) â†’ optional challenge â†’ deliberate
(programmatic gate + LLM consensus).

## Mechanism

1. Deploy with concrete claim + builder_label
2. submit_evidence(https://...) up to 3 times
3. optional file_challenge(reason)
4. deliberate(): deterministic checks, then LLM accept/reject/insufficient
5. settled locks accept/reject; insufficient allows more evidence

## Lint

UTF-8 **without BOM**. Depends comment is byte 0 of the file.

## Studio demo

Use contract + evidence links from your new deploy after v2 ship.