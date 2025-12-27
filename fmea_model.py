class FMEAEntry:
    def __init__(
        self,
        component,
        failure_mode,
        effect,
        cause,
        controls,
        severity,
        occurrence,
        detectability
    ):
        self.component = component
        self.failure_mode = failure_mode
        self.effect = effect
        self.cause = cause
        self.controls = controls
        self.severity = severity
        self.occurrence = occurrence
        self.detectability = detectability

    def compute_rpn(self):
        return self.severity * self.occurrence * self.detectability
