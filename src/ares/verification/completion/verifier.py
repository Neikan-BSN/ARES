"""Task Completion Verification Engine for ARES.

This module implements the primary task completion validation system that ensures
agent tasks are properly completed according to defined requirements and quality standards.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...models.agent import Agent
from ...models.reliability import ReliabilityMetric
from .schemas import (
    TaskCompletionRequest,
    TaskCompletionResult,
    CompletionStatus,
    VerificationEvidence,
    QualityMetrics,
)

logger = logging.getLogger(__name__)


class CompletionVerifier:
    """Primary task completion verification engine.

    Validates that agent tasks are completed according to:
    - Defined success criteria
    - Quality standards and metrics
    - Evidence requirements
    - Performance benchmarks
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the completion verifier.

        Args:
            db_session: Async database session for persistence
        """
        self.db_session = db_session
        self.verification_strategies: Dict[str, Any] = {}
        self._quality_thresholds = {
            "code_quality_min": 0.8,
            "test_coverage_min": 0.9,
            "performance_threshold": 1000,  # ms
            "security_score_min": 0.85,
        }

    async def verify_task_completion(
        self,
        agent_id: str,
        task_id: str,
        completion_request: TaskCompletionRequest,
    ) -> TaskCompletionResult:
        """Verify that a task has been completed successfully.

        Args:
            agent_id: Unique identifier for the agent
            task_id: Unique identifier for the task
            completion_request: Details of the completion claim

        Returns:
            TaskCompletionResult with verification status and evidence
        """
        logger.info(f"Starting task completion verification for agent {agent_id}, task {task_id}")

        try:
            # Step 1: Validate input requirements
            validation_result = await self._validate_completion_request(completion_request)
            if not validation_result.is_valid:
                return TaskCompletionResult(
                    task_id=task_id,
                    agent_id=agent_id,
                    status=CompletionStatus.INVALID,
                    message=validation_result.error_message,
                    quality_metrics=QualityMetrics(),
                    evidence=[],
                    verification_timestamp=datetime.now(timezone.utc),
                )

            # Step 2: Gather and analyze evidence
            evidence = await self._collect_verification_evidence(
                agent_id, task_id, completion_request
            )

            # Step 3: Execute verification strategies
            verification_results = await self._execute_verification_strategies(
                completion_request, evidence
            )

            # Step 4: Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                completion_request, evidence, verification_results
            )

            # Step 5: Determine final completion status
            final_status = await self._determine_completion_status(
                verification_results, quality_metrics
            )

            # Step 6: Update agent reliability metrics
            await self._update_reliability_metrics(
                agent_id, final_status, quality_metrics
            )

            # Step 7: Create completion result
            result = TaskCompletionResult(
                task_id=task_id,
                agent_id=agent_id,
                status=final_status,
                message=self._generate_completion_message(final_status, verification_results),
                quality_metrics=quality_metrics,
                evidence=evidence,
                verification_timestamp=datetime.now(timezone.utc),
                verification_details=verification_results,
            )

            logger.info(f"Task completion verification completed: {final_status}")
            return result

        except Exception as e:
            logger.error(f"Error during task completion verification: {str(e)}")
            return TaskCompletionResult(
                task_id=task_id,
                agent_id=agent_id,
                status=CompletionStatus.ERROR,
                message=f"Verification failed: {str(e)}",
                quality_metrics=QualityMetrics(),
                evidence=[],
                verification_timestamp=datetime.now(timezone.utc),
            )

    async def _validate_completion_request(
        self, request: TaskCompletionRequest
    ) -> Dict[str, Any]:
        """Validate the completion request format and content."""
        try:
            # Basic validation
            if not request.task_description:
                return {"is_valid": False, "error_message": "Task description is required"}

            if not request.completion_evidence:
                return {"is_valid": False, "error_message": "Completion evidence is required"}

            # Validate required fields are present
            required_fields = ["outputs", "tool_calls", "performance_metrics"]
            for field in required_fields:
                if field not in request.completion_evidence:
                    return {
                        "is_valid": False,
                        "error_message": f"Missing required evidence field: {field}"
                    }

            return {"is_valid": True, "error_message": None}

        except Exception as e:
            logger.error(f"Request validation error: {str(e)}")
            return {"is_valid": False, "error_message": f"Validation error: {str(e)}"}

    async def _collect_verification_evidence(
        self,
        agent_id: str,
        task_id: str,
        request: TaskCompletionRequest,
    ) -> List[VerificationEvidence]:
        """Collect evidence for task completion verification."""
        evidence = []

        try:
            # Collect output evidence
            if "outputs" in request.completion_evidence:
                output_evidence = VerificationEvidence(
                    evidence_type="output_analysis",
                    source="agent_outputs",
                    data=request.completion_evidence["outputs"],
                    timestamp=datetime.now(timezone.utc),
                    confidence_score=0.9,
                )
                evidence.append(output_evidence)

            # Collect tool usage evidence
            if "tool_calls" in request.completion_evidence:
                tool_evidence = VerificationEvidence(
                    evidence_type="tool_usage",
                    source="mcp_logs",
                    data=request.completion_evidence["tool_calls"],
                    timestamp=datetime.now(timezone.utc),
                    confidence_score=0.95,
                )
                evidence.append(tool_evidence)

            # Collect performance evidence
            if "performance_metrics" in request.completion_evidence:
                perf_evidence = VerificationEvidence(
                    evidence_type="performance_metrics",
                    source="system_monitoring",
                    data=request.completion_evidence["performance_metrics"],
                    timestamp=datetime.now(timezone.utc),
                    confidence_score=0.98,
                )
                evidence.append(perf_evidence)

            logger.info(f"Collected {len(evidence)} pieces of verification evidence")
            return evidence

        except Exception as e:
            logger.error(f"Evidence collection error: {str(e)}")
            return evidence

    async def _execute_verification_strategies(
        self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
    ) -> Dict[str, Any]:
        """Execute different verification strategies based on task type."""
        results = {}

        try:
            # Strategy 1: Output Quality Verification
            results["output_quality"] = await self._verify_output_quality(request, evidence)

            # Strategy 2: Requirements Matching
            results["requirements_match"] = await self._verify_requirements_match(request, evidence)

            # Strategy 3: Performance Verification
            results["performance"] = await self._verify_performance_standards(request, evidence)

            # Strategy 4: Security Compliance
            results["security"] = await self._verify_security_compliance(request, evidence)

            return results

        except Exception as e:
            logger.error(f"Verification strategy execution error: {str(e)}")
            return {"error": str(e)}

    async def _verify_output_quality(
        self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
    ) -> Dict[str, Any]:
        """Verify the quality of task outputs."""
        try:
            output_evidence = next(
                (e for e in evidence if e.evidence_type == "output_analysis"), None
            )

            if not output_evidence:
                return {"passed": False, "score": 0.0, "reason": "No output evidence available"}

            # Analyze output quality metrics
            outputs = output_evidence.data
            quality_score = 0.0
            quality_factors = []

            # Check completeness
            if outputs.get("completeness_score", 0) >= 0.8:
                quality_score += 0.3
                quality_factors.append("completeness_good")

            # Check accuracy
            if outputs.get("accuracy_score", 0) >= 0.85:
                quality_score += 0.3
                quality_factors.append("accuracy_good")

            # Check format compliance
            if outputs.get("format_compliance", False):
                quality_score += 0.2
                quality_factors.append("format_compliant")

            # Check error handling
            if outputs.get("error_handling_score", 0) >= 0.8:
                quality_score += 0.2
                quality_factors.append("error_handling_good")

            passed = quality_score >= self._quality_thresholds["code_quality_min"]

            return {
                "passed": passed,
                "score": quality_score,
                "factors": quality_factors,
                "threshold": self._quality_thresholds["code_quality_min"],
            }

        except Exception as e:
            logger.error(f"Output quality verification error: {str(e)}")
            return {"passed": False, "score": 0.0, "reason": f"Verification error: {str(e)}"}

    async def _verify_requirements_match(
        self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
    ) -> Dict[str, Any]:
        """Verify that outputs match the original task requirements."""
        try:
            # Extract requirements from task description
            requirements = self._extract_requirements(request.task_description)

            # Analyze outputs against requirements
            output_evidence = next(
                (e for e in evidence if e.evidence_type == "output_analysis"), None
            )

            if not output_evidence:
                return {"passed": False, "score": 0.0, "reason": "No output evidence available"}

            outputs = output_evidence.data
            matched_requirements = []
            total_requirements = len(requirements)

            for req in requirements:
                if self._check_requirement_fulfillment(req, outputs):
                    matched_requirements.append(req)

            match_score = len(matched_requirements) / max(total_requirements, 1)
            passed = match_score >= 0.9  # 90% requirements must be met

            return {
                "passed": passed,
                "score": match_score,
                "matched_requirements": matched_requirements,
                "total_requirements": total_requirements,
                "missing_requirements": [r for r in requirements if r not in matched_requirements],
            }

        except Exception as e:
            logger.error(f"Requirements matching error: {str(e)}")
            return {"passed": False, "score": 0.0, "reason": f"Matching error: {str(e)}"}

    async def _verify_performance_standards(
        self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
    ) -> Dict[str, Any]:
        """Verify that task performance meets standards."""
        try:
            perf_evidence = next(
                (e for e in evidence if e.evidence_type == "performance_metrics"), None
            )

            if not perf_evidence:
                return {"passed": False, "score": 0.0, "reason": "No performance evidence available"}

            metrics = perf_evidence.data
            performance_score = 1.0
            issues = []

            # Check execution time
            execution_time = metrics.get("execution_time_ms", float('inf'))
            if execution_time > self._quality_thresholds["performance_threshold"]:
                performance_score -= 0.3
                issues.append(f"Execution time {execution_time}ms exceeds threshold")

            # Check memory usage
            memory_usage = metrics.get("memory_usage_mb", 0)
            if memory_usage > 500:  # 500MB threshold
                performance_score -= 0.2
                issues.append(f"Memory usage {memory_usage}MB is high")

            # Check error rate
            error_rate = metrics.get("error_rate", 0)
            if error_rate > 0.05:  # 5% error rate threshold
                performance_score -= 0.3
                issues.append(f"Error rate {error_rate} exceeds 5%")

            performance_score = max(0.0, performance_score)
            passed = performance_score >= 0.7

            return {
                "passed": passed,
                "score": performance_score,
                "execution_time_ms": execution_time,
                "memory_usage_mb": memory_usage,
                "error_rate": error_rate,
                "issues": issues,
            }

        except Exception as e:
            logger.error(f"Performance verification error: {str(e)}")
            return {"passed": False, "score": 0.0, "reason": f"Performance error: {str(e)}"}

    async def _verify_security_compliance(
        self, request: TaskCompletionRequest, evidence: List[VerificationEvidence]
    ) -> Dict[str, Any]:
        """Verify that task execution meets security standards."""
        try:
            # Security verification logic
            security_score = 1.0
            security_issues = []

            # Check for sensitive data exposure
            output_evidence = next(
                (e for e in evidence if e.evidence_type == "output_analysis"), None
            )

            if output_evidence:
                outputs = output_evidence.data
                if self._contains_sensitive_data(outputs):
                    security_score -= 0.4
                    security_issues.append("Potential sensitive data exposure detected")

            # Check tool usage compliance
            tool_evidence = next(
                (e for e in evidence if e.evidence_type == "tool_usage"), None
            )

            if tool_evidence:
                tool_calls = tool_evidence.data
                if self._has_unauthorized_tool_usage(tool_calls):
                    security_score -= 0.3
                    security_issues.append("Unauthorized tool usage detected")

            security_score = max(0.0, security_score)
            passed = security_score >= self._quality_thresholds["security_score_min"]

            return {
                "passed": passed,
                "score": security_score,
                "issues": security_issues,
                "threshold": self._quality_thresholds["security_score_min"],
            }

        except Exception as e:
            logger.error(f"Security verification error: {str(e)}")
            return {"passed": False, "score": 0.0, "reason": f"Security error: {str(e)}"}

    async def _calculate_quality_metrics(
        self,
        request: TaskCompletionRequest,
        evidence: List[VerificationEvidence],
        verification_results: Dict[str, Any],
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics for the task completion."""
        try:
            # Extract scores from verification results
            output_quality_score = verification_results.get("output_quality", {}).get("score", 0.0)
            requirements_score = verification_results.get("requirements_match", {}).get("score", 0.0)
            performance_score = verification_results.get("performance", {}).get("score", 0.0)
            security_score = verification_results.get("security", {}).get("score", 0.0)

            # Calculate overall quality score
            overall_score = (
                output_quality_score * 0.3 +
                requirements_score * 0.3 +
                performance_score * 0.2 +
                security_score * 0.2
            )

            # Calculate confidence based on evidence quality
            evidence_confidence = sum(e.confidence_score for e in evidence) / max(len(evidence), 1)

            return QualityMetrics(
                overall_score=overall_score,
                output_quality_score=output_quality_score,
                requirements_match_score=requirements_score,
                performance_score=performance_score,
                security_score=security_score,
                evidence_confidence=evidence_confidence,
                verification_completeness=self._calculate_completeness(verification_results),
            )

        except Exception as e:
            logger.error(f"Quality metrics calculation error: {str(e)}")
            return QualityMetrics()

    async def _determine_completion_status(
        self, verification_results: Dict[str, Any], quality_metrics: QualityMetrics
    ) -> CompletionStatus:
        """Determine the final task completion status."""
        try:
            # Check if all critical verifications passed
            critical_checks = ["output_quality", "requirements_match"]
            for check in critical_checks:
                if not verification_results.get(check, {}).get("passed", False):
                    return CompletionStatus.FAILED

            # Check overall quality score
            if quality_metrics.overall_score < 0.7:
                return CompletionStatus.PARTIAL

            # Check individual component scores
            if (quality_metrics.performance_score < 0.6 or
                quality_metrics.security_score < 0.8):
                return CompletionStatus.PARTIAL

            return CompletionStatus.COMPLETED

        except Exception as e:
            logger.error(f"Status determination error: {str(e)}")
            return CompletionStatus.ERROR

    async def _update_reliability_metrics(
        self, agent_id: str, status: CompletionStatus, quality_metrics: QualityMetrics
    ) -> None:
        """Update agent reliability metrics based on verification results."""
        try:
            # This would integrate with the existing ReliabilityMetric model
            # Implementation would depend on the specific database schema
            logger.info(f"Updating reliability metrics for agent {agent_id}: {status}")

            # Placeholder for database update logic
            # await self.db_session.execute(...)
            # await self.db_session.commit()

        except Exception as e:
            logger.error(f"Reliability metrics update error: {str(e)}")

    def _extract_requirements(self, task_description: str) -> List[str]:
        """Extract requirements from task description."""
        # Simple requirements extraction - could be enhanced with NLP
        requirements = []

        # Look for bullet points, numbered lists, etc.
        lines = task_description.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•')) or any(line.startswith(f"{i}.") for i in range(1, 10)):
                requirements.append(line.lstrip('-*•0123456789. '))

        # If no structured requirements found, treat whole description as one requirement
        if not requirements:
            requirements.append(task_description.strip())

        return requirements

    def _check_requirement_fulfillment(self, requirement: str, outputs: Dict[str, Any]) -> bool:
        """Check if a specific requirement is fulfilled by the outputs."""
        # Simple keyword matching - could be enhanced with semantic analysis
        requirement_lower = requirement.lower()
        outputs_str = str(outputs).lower()

        # Look for key terms from requirement in outputs
        key_terms = [word for word in requirement_lower.split() if len(word) > 3]
        matches = sum(1 for term in key_terms if term in outputs_str)

        return matches >= len(key_terms) * 0.6  # 60% of key terms must be present

    def _contains_sensitive_data(self, outputs: Dict[str, Any]) -> bool:
        """Check if outputs contain sensitive data."""
        outputs_str = str(outputs).lower()
        sensitive_patterns = [
            'password', 'secret', 'token', 'key', 'credential',
            'ssn', 'social security', 'credit card', 'api_key'
        ]

        return any(pattern in outputs_str for pattern in sensitive_patterns)

    def _has_unauthorized_tool_usage(self, tool_calls: List[Dict[str, Any]]) -> bool:
        """Check for unauthorized tool usage."""
        # Define authorized tools (this could be configurable)
        authorized_tools = {
            'read_file', 'write_file', 'list_directory', 'run_command',
            'search_code', 'analyze_code', 'format_code'
        }

        for call in tool_calls:
            tool_name = call.get('tool_name', '')
            if tool_name not in authorized_tools:
                return True

        return False

    def _calculate_completeness(self, verification_results: Dict[str, Any]) -> float:
        """Calculate verification completeness score."""
        expected_verifications = ["output_quality", "requirements_match", "performance", "security"]
        completed_verifications = [
            v for v in expected_verifications
            if v in verification_results and "error" not in verification_results[v]
        ]

        return len(completed_verifications) / len(expected_verifications)

    def _generate_completion_message(
        self, status: CompletionStatus, verification_results: Dict[str, Any]
    ) -> str:
        """Generate a human-readable completion message."""
        if status == CompletionStatus.COMPLETED:
            return "Task completed successfully with all quality standards met."
        elif status == CompletionStatus.PARTIAL:
            issues = []
            for check, result in verification_results.items():
                if not result.get("passed", True):
                    issues.append(f"{check}: {result.get('reason', 'Failed')}")
            return f"Task partially completed. Issues: {'; '.join(issues)}"
        elif status == CompletionStatus.FAILED:
            return "Task completion verification failed critical requirements."
        else:
            return "Task completion verification encountered an error."

    async def get_verification_history(
        self, agent_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get verification history for analysis."""
        # Placeholder for database query to retrieve verification history
        # This would integrate with the database models
        return []

    async def update_quality_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update quality thresholds for verification."""
        self._quality_thresholds.update(new_thresholds)
        logger.info(f"Updated quality thresholds: {self._quality_thresholds}")
