# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class AgentClaimJudge(gl.Contract):
    claim: str
    builder_label: str
    verdict: str
    settled: bool

    def __init__(self, claim: str, builder_label: str):
        self.claim = claim
        self.builder_label = builder_label
        self.verdict = "pending"
        self.settled = False

    @gl.public.view
    def get_claim(self) -> str:
        return self.claim

    @gl.public.view
    def get_builder_label(self) -> str:
        return self.builder_label

    @gl.public.view
    def get_verdict(self) -> str:
        return self.verdict

    @gl.public.view
    def get_settled(self) -> bool:
        return self.settled

    @gl.public.write
    def judge_claim(self) -> None:
        if self.settled:
            return

        prompt = f"""
You are an impartial GenLayer adjudicator for an incentivized builder program.
Evaluate whether this builder claim is specific, testable, and credible.

Builder: {self.builder_label}
Claim: {self.claim}

Rules:
- Accept only if the claim names a concrete deliverable (contract, repo, demo, tutorial).
- Reject vague hype with no artifact.
- Be strict but fair.

Respond using ONLY this JSON format:
{{
"reasoning": str,
"verdict": "accept" | "reject"
}}
Nothing else. No markdown. Must be valid JSON.
"""

        def nondet():
            res = gl.nondet.exec_prompt(prompt)
            backticks = "``" + "`"
            res = res.replace(backticks + "json", "").replace(backticks, "").strip()
            print(res)
            dat = json.loads(res)
            verdict = str(dat["verdict"]).strip().lower()
            if verdict not in ("accept", "reject"):
                raise Exception("invalid verdict")
            return verdict

        result = gl.eq_principle.strict_eq(nondet)
        assert isinstance(result, str)
        self.verdict = result
        self.settled = True
