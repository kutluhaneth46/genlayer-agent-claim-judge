# Agent Claim Judge · GenLayer Intelligent Contract

Builder: **KutluhanETH**

LLM claim adjudicator. Consensus on accept/reject via Equivalence Principle.

## Live Studio

- Contract: https://explorer-studio.genlayer.com/address/0x8a2C9881F8700aF25EE6150621abe21fd3cDfcC1
- Deploy tx: https://explorer-studio.genlayer.com/tx/0x2651957b839f99a47b3de76ccabfca9df946ec5579e562aa0967bb9bb632fff0
- Result: get_verdict → "accept" after judge_claim

## Why not Hello World

- gl.nondet.exec_prompt + JSON allowlisted verdicts
- gl.eq_principle.strict_eq on normalized verdict
- Persistent state + one-shot settled latch

## File

- agent_claim_judge.py
