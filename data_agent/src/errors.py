class DataAgentError(Exception):
    """Base exception for Data Agent runtime errors."""


class AuditQueryError(DataAgentError):
    """Invalid audit replay query parameters."""


class NLAdapterError(DataAgentError):
    """NL adapter returned invalid normalization payload."""
