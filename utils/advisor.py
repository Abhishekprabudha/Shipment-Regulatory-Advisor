from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class AdvisoryResult:
    decision: str            # "SHIP" | "HOLD" | "DO_NOT_SHIP"
    risk_score: int
    reasons: List[str]
    next_steps: List[str]

def build_advisory(
    shipment: Dict[str, Any],
    destination: str,
    qty: float,
    unit_value: float,
    policy: Dict[str, Any],
) -> AdvisoryResult:
    reasons = []
    next_steps = []
    risk = 0

    # Base: destination screening
    high_risk = set(policy.get("high_risk_destinations", []))
    if destination in high_risk:
        risk += 70
        reasons.append(f"Destination '{destination}' is configured as high-risk (comprehensive controls/sanctions).")
        note = policy.get("destination_notes", {}).get(destination)
        if note:
            reasons.append(note)
        next_steps.extend([
            "Run sanctions screening (OFAC/denied parties) for all parties in the transaction.",
            "Confirm whether an export license or OFAC authorization is required before shipping.",
            "Escalate to compliance for a go/no-go determination."
        ])

    # Category rules
    cat = shipment.get("category", "Unknown")
    for rule in policy.get("category_risk_rules", []):
        if rule.get("category") == cat:
            risk += int(rule.get("risk_score_add", 0))
            reasons.append(rule.get("reason", f"Category risk: {cat}"))
            if rule.get("default_action") == "HOLD":
                next_steps.extend([
                    "Collect end-use + end-user statement.",
                    "Validate ECCN/HS classification and license requirements."
                ])
            break

    # Quantity/value heuristics (demo)
    total_value = qty * unit_value
    if total_value >= 25000:
        risk += 10
        reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny and documentation requirements.")
        next_steps.append("Ensure full commercial invoice, export documentation, and internal approvals are complete.")

    # Decide
    thresholds = policy.get("risk_thresholds", {"do_not_ship": 80, "hold": 45})
    if risk >= thresholds.get("do_not_ship", 80):
        decision = "DO_NOT_SHIP"
        next_steps.insert(0, "Stop shipment creation until compliance clearance is documented.")
    elif risk >= thresholds.get("hold", 45):
        decision = "HOLD"
        next_steps.insert(0, "Place shipment on compliance hold pending review.")
    else:
        decision = "SHIP"
        next_steps.insert(0, "Proceed with shipping, subject to standard screening and paperwork.")

    # Clean up duplicates
    next_steps = list(dict.fromkeys(next_steps))
    reasons = list(dict.fromkeys(reasons))

    return AdvisoryResult(
        decision=decision,
        risk_score=risk,
        reasons=reasons,
        next_steps=next_steps
    )
