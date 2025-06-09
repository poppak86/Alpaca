class Brain:
    """Simple structure to store advice history and update confidence/priority."""

    def __init__(self):
        self.history = {}

    def compare_advice_with_trade(self, advice_id, advice_action, profit):
        """Adjust confidence and priority based on trade outcome.

        Parameters
        ----------
        advice_id : hashable
            Identifier for the advice or rule.
        advice_action : str
            Either ``"buy"`` or ``"sell"``.
        profit : float
            The profit (positive or negative) from acting on the advice.
        """
        record = self.history.get(advice_id, {"confidence": 1.0, "priority": 1})

        was_correct = (profit > 0 and advice_action == "buy") or (
            profit < 0 and advice_action == "sell"
        )

        if was_correct:
            record["confidence"] += 0.1
            record["priority"] += 1
        else:
            record["confidence"] = max(0.0, record["confidence"] - 0.1)
            record["priority"] = max(1, record["priority"] - 1)

        self.history[advice_id] = record
        return record
