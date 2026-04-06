from scipy import optimize


def compute_irr(values, time, initial_guess=0):
    """
    Returns the internal rate of return (IRR) based on values
    of transactions and the elapsed time.
    Purchase values need to be negative and sales positive.
    Elapsed time is the difference between first purchase and subsequent
    transactions in years.
    """

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(values / (1 + irr) ** time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return solver.x[0]
