from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Advisory:
    decision: str
    risk_score: int
    reasons: List[str]
    components: Dict[str, int]

def advisory_from_ear746(destination: str, product: str, quantity: float, unit_value: float, ear746_text: str) -> Advisory:
    """
    EAR Part 746-only demo advisory logic.
    Returns a risk score + component breakdown for plotting.
    """
    dest = destination.strip().lower()
    product_l = product.lower()
    total_value = quantity * unit_value

    comprehensive = {"cuba", "iran", "syria"}
    special = {"north korea", "russia", "belarus", "crimea", "donetsk", "luhansk"}

    reasons: List[str] = []
    components: Dict[str, int] = {"Destination": 0, "Product": 0, "Value": 0, "Base": 0}

    # Destination scoring
    if dest in comprehensive:
        components["Destination"] = 85
        reasons.append(f"Destination '{destination}' aligns with comprehensive controls referenced under EAR Part 746 (demo rule).")
        reasons.append("Stop shipment and route to compliance for authorization.")
        if total_value >= 25000:
            components["Value"] = 10
            reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny.")
        risk = sum(components.values())
        return Advisory("DO_NOT_SHIP", risk, reasons, components)

    if dest in special:
        components["Destination"] = 65
        reasons.append(f"Destination '{destination}' is covered by special controls referenced in EAR Part 746 (demo rule).")
        reasons.append("Place shipment on hold pending compliance review.")
        if total_value >= 25000:
            components["Value"] = 10
            reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny.")
        risk = sum(components.values())
        return Advisory("HOLD", risk, reasons, components)

    # Product heuristics (demo)
    if any(k in product_l for k in ["drone", "uav", "flight controller", "satellite"]):
        components["Product"] += 25
        reasons.append("Product appears defense-adjacent/high-tech (demo heuristic). Classification/end-use review recommended.")

    if any(k in product_l for k in ["encrypted", "encryption", "router", "wi-fi"]):
        components["Product"] += 15
        reasons.append("Product includes encryption/telecom (demo heuristic). Classification review recommended.")

    if "lithium" in product_l:
        components["Product"] += 10
        reasons.append("Lithium batteries may have carrier/dangerous goods constraints (demo heuristic).")

    # Base + Value
    components["Base"] = 15

    if total_value >= 25000:
        components["Value"] = 10
        reasons.append(f"High declared value (${total_value:,.0f}) increases scrutiny.")

    if not reasons:
        reasons.append("No direct EAR Part 746 match found in this demo phase. Continue standard screening.")

    risk = sum(components.values())
    return Advisory("SHIP", risk, reasons, components)
