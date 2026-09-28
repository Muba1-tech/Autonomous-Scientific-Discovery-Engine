class RuleEngine:
    def __init__(self):
        self.min_length = 50
        self.max_risk = 0.8
        self.dynamic_rules = [
            lambda ctx: len(ctx.get("hypothesis", "")) > self.min_length,
            lambda ctx: ctx.get("risk_score", 0.0) < self.max_risk
        ]
        self.custom_rules = []
        
    def adapt(self, success_rate: float):
        # If passing is too easy, tighten the rules for higher quality
        if success_rate > 0.8:
            self.min_length = 100
            self.max_risk = 0.6
        # If rules are too strict, loosen them to foster more innovation
        elif success_rate < 0.3:
            self.min_length = 30
            self.max_risk = 0.95

    def add_rule(self, rule_func):
        self.custom_rules.append(rule_func)
        
    def evaluate(self, context: dict) -> bool:
        all_rules = self.dynamic_rules + self.custom_rules
        for rule in all_rules:
            if not rule(context):
                return False
        return True
