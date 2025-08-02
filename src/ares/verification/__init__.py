"""ARES Verification Components.

This package contains the five core verification components:
- CompletionVerifier: Task completion validation engine
- ToolCallValidator: MCP tool invocation verification
- TaskRollbackManager: State rollback and recovery
- ProofOfWorkCollector: Evidence collection and validation
- AgentBehaviorMonitor: Behavioral pattern analysis
"""

from .behavior_monitoring.monitor import AgentBehaviorMonitor
from .completion.verifier import CompletionVerifier
from .proof_of_work.collector import ProofOfWorkCollector
from .rollback.manager import TaskRollbackManager
from .tool_validation.validator import ToolCallValidator

__all__ = [
    "CompletionVerifier",
    "ToolCallValidator",
    "TaskRollbackManager",
    "ProofOfWorkCollector",
    "AgentBehaviorMonitor",
]
