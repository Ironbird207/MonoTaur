from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from time import monotonic
from typing import Optional

from . import schemas


async def _run_ping(target: str, timeout_ms: int) -> schemas.CheckResult:
    """Execute a single ping and summarize the result.

    This intentionally uses the system `ping` binary for simplicity in the prototype. The
    measured latency is derived from wall-clock elapsed time, which is sufficient for the
    lightweight checks exercised in tests.
    """

    start = monotonic()
    timeout_seconds = max(1, int(timeout_ms / 1000))
    try:
        process = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            "1",
            "-W",
            str(timeout_seconds),
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        latency_ms = (monotonic() - start) * 1000
        message_bytes: Optional[bytes] = stderr or stdout
        message = message_bytes.decode().strip() if message_bytes else None
        status = "up" if process.returncode == 0 else "down"
        return schemas.CheckResult(
            status=status,
            latency_ms=latency_ms,
            message=message,
            checked_at=datetime.now(timezone.utc),
        )
    except FileNotFoundError:
        return schemas.CheckResult(
            status="unknown",
            latency_ms=None,
            message="ping binary not available",
            checked_at=datetime.now(timezone.utc),
        )


async def run_check(check: schemas.Check) -> schemas.CheckResult:
    """Run a single check based on its type."""

    if check.type == "icmp":
        return await _run_ping(check.target, check.timeout_ms)

    return schemas.CheckResult(
        status="unknown",
        latency_ms=None,
        message=f"unsupported check type: {check.type}",
        checked_at=datetime.now(timezone.utc),
    )
