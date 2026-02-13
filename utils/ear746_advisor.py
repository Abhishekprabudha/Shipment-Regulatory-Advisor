from dataclasses import dataclass
from typing import List


@dataclass
class Advisory:
    decision: str        # "SHIP" | "HOLD" | "DO_NOT_SHIP"
    risk_score: int
    reasons: List[str]


def advisory_from_ear746(
    destination: str,
    product: str,
    quantity: float,
    unit_value: float,
    ear746_text: str,
) -> Advisory:
    """
    EAR Part 746-only demo advisory logic.

    NOTE: This is intentionally simplified for demo:
    - Comprehensive controls destinations => DO_NOT_SHIP
    - Special controls destinations => HOLD
    - Everything else => SHIP

    You can later replace this with clause-aware rules + OFAC + SDN screening.
    """
    dest = destination.strip().lower()

    # Baseline sets for a credible demo narrative (EAR 746 focus)
    comprehensive = {"cuba", "iran", "syria"}
    special = {"north korea", "russia", "belarus", "crimea", "donetsk", "luhansk"}

    reasons = []
    risk = 0

    total_value = quantity * unit_value

    # Destination screening
    if dest in comprehensive:
        risk += 85
        reasons.append(f"Destination '{destination}' aligns with comprehensive controls referenced under EAR Part 746.")
        reasons.append("Treat as embargo-style controls for demo: stop shipment and route to compliance for authorization.")
        if total_value >= 25000:
            reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny and documentation requirements.")
        return Advisory(decision="DO_NOT_SHIP", risk_score=risk, reasons=reasons)

    if dest in special:
        risk += 65
        reasons.append(f"Destination '{destination}' is covered by special controls referenced in EAR Part 746 sections.")
        reasons.append("Place shipment on hold pending compliance review and any required licensing determination.")
        if total_value >= 25000:
            reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny and documentation requirements.")
        return Advisory(decision="HOLD", risk_score=risk, reasons=reasons)

    # Product heuristic (pure demo)
    product_l = product.lower()
    if any(k in product_l for k in ["drone", "uav", "flight controller", "encryption", "satellite"]):
        risk += 20
        reasons.append("Product appears potentially export-controlled (demo heuristic). Consider classification and end-use review.")

    # Default
    risk += 15
    if total_value >= 25000:
        risk += 10
        reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny and documentation requirements.")

    if not reasons:
        reasons.append("No direct EAR Part 746 match found in this demo phase. Continue with standard screening.")

    return Advisory(decision="SHIP", risk_score=risk, reasons=reasons)
