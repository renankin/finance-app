def calculate_npv(irr, cash_flows, years) -> float:
    """
    Calculates the net present value (NPV) of a series of cash flows.
    """
    return sum(cash_flows / (1 + irr) ** years)
