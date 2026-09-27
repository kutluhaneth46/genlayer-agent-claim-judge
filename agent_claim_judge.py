# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class AgentClaimJudge(gl.Contract):
    claim: str
    builder_label: str
    evidence_1: str
    evidence_2: str
    evidence_3: str
    evidence_count: u256
    challenge_reason: str
    challenged: bool
    phase: str
    verdict: str
    check_summary: str

    def __init__(self, claim: str, builder_label: str):
        self.claim = claim
        self.builder_label = builder_label
        self.evidence_1 = ""
        self.evidence_2 = ""
        self.evidence_3 = ""
        self.evidence_count = u256(0)
        self.challenge_reason = ""
        self.challenged = False
        self.phase = "filing"
        self.verdict = "pending"
        self.check_summary = ""

    def _https_ok(self, url: str) -> bool:
        return len(url) >= 12 and (url.startswith("https://") or url.startswith("http://"))

    @gl.public.view
    def get_claim(self) -> str:
        return self.claim

    @gl.public.view
    def get_builder_label(self) -> str:
        return self.builder_label

    @gl.public.view
    def get_phase(self) -> str:
        return self.phase

    @gl.public.view
    def get_verdict(self) -> str:
        return self.verdict

    @gl.public.view
    def get_evidence_count(self) -> u256:
        return self.evidence_count

    @gl.public.view
    def get_challenged(self) -> bool:
        return self.challenged

    @gl.public.view
    def get_challenge_reason(self) -> str:
        return self.challenge_reason

    @gl.public.view
    def get_check_summary(self) -> str:
        return self.check_summary

    @gl.public.view
    def get_evidence_1(self) -> str:
        return self.evidence_1

    @gl.public.view
    def get_evidence_2(self) -> str:
        return self.evidence_2

    @gl.public.view
    def get_evidence_3(self) -> str:
        return self.evidence_3

    @gl.public.write
    def submit_evidence(self, url: str) -> None:
        if self.phase == "settled":
            return
        if not self._https_ok(url):
            raise Exception("evidence must be http(s) URL")
        if self.evidence_count >= u256(3):
            raise Exception("max 3 evidence links")

        if self.evidence_count == u256(0):
            self.evidence_1 = url
        elif self.evidence_count == u256(1):
            self.evidence_2 = url
        else:
            self.evidence_3 = url

        self.evidence_count = self.evidence_count + u256(1)
        self.phase = "evidence"
        if self.verdict == "insufficient":
            self.verdict = "pending"

    @gl.public.write
    def file_challenge(self, reason: str) -> None:
        if self.phase == "settled":
            return
        if self.evidence_count < u256(1):
            raise Exception("need evidence before challenge")
        if len(reason.strip()) < 12:
            raise Exception("challenge reason too short")
        self.challenge_reason = reason.strip()
        self.challenged = True
        self.phase = "challenged"

    @gl.public.write
    def deliberate(self) -> None:
        if self.phase == "settled":
            return
        if self.evidence_count < u256(1):
            raise Exception("submit evidence before deliberate")

        claim_ok = len(self.claim.strip()) >= 40
        label_ok = len(self.builder_label.strip()) >= 3
        e1_ok = self.evidence_count == u256(0) or self._https_ok(self.evidence_1)
        e2_ok = self.evidence_count < u256(2) or self._https_ok(self.evidence_2)
        e3_ok = self.evidence_count < u256(3) or self._https_ok(self.evidence_3)
        gate_ok = claim_ok and label_ok and e1_ok and e2_ok and e3_ok

        summary = (
            "claim_len="
            + str(len(self.claim.strip()))
            + ";evidence="
            + str(self.evidence_count)
            + ";challenged="
            + ("yes" if self.challenged else "no")
            + ";gate="
            + ("pass" if gate_ok else "fail")
        )
        self.check_summary = summary

        if not gate_ok:
            self.verdict = "insufficient"
            self.phase = "evidence"
            return

        evidence_blob = self.evidence_1
        if self.evidence_count >= u256(2):
            evidence_blob = evidence_blob + " | " + self.evidence_2
        if self.evidence_count >= u256(3):
            evidence_blob = evidence_blob + " | " + self.evidence_3

        challenge_blob = self.challenge_reason if self.challenged else "(none)"

        prompt = f"""
You are a GenLayer adjudication panel for an incentivized builder program.

Builder: {self.builder_label}
Claim: {self.claim}
Evidence URLs: {evidence_blob}
Challenge: {challenge_blob}
Programmatic gate: PASS ({summary})

Decide using ALL of:
1) Is the claim concrete (names a deliverable: contract, repo, demo, tutorial)?
2) Do evidence URLs plausibly support that deliverable?
3) If a challenge exists, does it undermine the claim enough to reject?

Verdicts (pick exactly one):
- accept: claim concrete AND evidence supportive AND challenge does not defeat it
- reject: claim vague OR evidence irrelevant OR challenge succeeds
- insufficient: claim OK but evidence too weak / incomplete to decide

Respond using ONLY this JSON:
{{
"reasoning": str,
"verdict": "accept" | "reject" | "insufficient"
}}
No markdown. Valid JSON only.
"""

        def nondet():
            res = gl.nondet.exec_prompt(prompt)
            backticks = "``" + "`"
            res = res.replace(backticks + "json", "").replace(backticks, "").strip()
            print(res)
            dat = json.loads(res)
            verdict = str(dat["verdict"]).strip().lower()
            if verdict not in ("accept", "reject", "insufficient"):
                raise Exception("invalid verdict")
            return verdict

        result = gl.eq_principle.strict_eq(nondet)
        assert isinstance(result, str)
        self.verdict = result

        if result == "insufficient":
            self.phase = "evidence"
        else:
            self.phase = "settled"