#!/usr/bin/env python3
"""
Hermes Core v3.6 - System Verification Suite
Path: ~/.hermes/skills/hermes-adaptive-core/test_runner.py
"""

import asyncio
import logging
import time
from hermes_core import MicroRoutedAdaptiveRouter

logging.basicConfig(level=logging.ERROR)


async def run_system_verification():
 print("=" * 70)
 print(" HERMES CORE V3.7 - SYSTEM VERIFICATION AND BENCHMARK SUITE")
 print("=" * 70)

 router = MicroRoutedAdaptiveRouter()
 await asyncio.sleep(0.5)

 # Test 1: Routing
 print("\n[Test 1: Skill Routing]")
 for q in ["pandas", "Check KernelSU root modules"]:
 res = await router.route_and_execute(q)
 print(f" '{q}' -> {res.get('status')} ({res['latency_ms']:.3f}ms)")

 # Test 2: Circuit breaker
 print("\n[Test 2: Circuit Breaker]")
 entry = router.registry.get_skill("pandas")
 if entry:
 for _ in range(3):
 entry.health.record_failure()
 print(f" After 3 failures: circuit_open={entry.health.circuit_open}")
 res = await router.route_and_execute("pandas")
 print(f" Routed with open circuit: {res.get('status')} - {res.get('reason')}")

 # Test 3: Concurrency
 print("\n[Test 3: Concurrency]")

 async def burst(n):
 tasks = [router.route_and_execute("pandas") for _ in range(n)]
 return await asyncio.gather(*tasks)

 t0 = time.perf_counter()
 results = await burst(200)
 elapsed = (time.perf_counter() - t0) * 1000
 success = sum(1 for r in results if r.get("status") in ("success", "completed"))
 print(f" {success}/200 in {elapsed:.1f}ms ({200/(elapsed/1000):.0f} req/s)")

 # Test 4: Index info
 print("\n[Test 4: Index]")
 skills = router.registry.list_skills()
 print(f" {len(skills)} skills indexed")
 with_meta = router.registry.list_with_metadata()
 print(f" Metadata available: {len(with_meta)} entries")

 router.stop_watcher()
 print("\n" + "=" * 70)
 print(" VERIFICATION COMPLETE")
 print("=" * 70)


if __name__ == "__main__":
 asyncio.run(run_system_verification())