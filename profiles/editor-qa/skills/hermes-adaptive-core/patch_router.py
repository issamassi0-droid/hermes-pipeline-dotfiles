import re

with open("hermes_core.py", "r") as f:
    content = f.read()

target = '''    async def route_and_execute(self, skill_id: str, payload: dict) -> dict:
        """Routes payload to the target skill and returns execution results."""
        skill_module = self.registry.get_skill(skill_id)
        if not skill_module:
            return {"status": "error", "reason": f"Skill \'{skill_id}\' not found."}

        metadata = getattr(skill_module, "__skill_metadata__", {})
        timeout = metadata.get("timeout_seconds", 3.0)

        return await self.executor.execute_skill(skill_module, payload, timeout=timeout)'''

replacement = '''    async def route_and_execute(self, query_or_id: str, payload: Optional[dict] = None) -> dict:
        """Routes natural language queries or direct skill IDs to execution."""
        if payload is None:
            payload = {"query": query_or_id}
            
        skill_module = self.registry.get_skill(query_or_id)
        if not skill_module:
            for s_id, module in self.registry._index.items():
                if s_id.lower() in query_or_id.lower() or query_or_id.lower() in s_id.lower():
                    skill_module = module
                    break

        if not skill_module:
            return {"status": "error", "reason": f"Skill or intent matching '{query_or_id}' not found."}

        metadata = getattr(skill_module, "__skill_metadata__", {})
        timeout = metadata.get("timeout_seconds", 3.0)

        return await self.executor.execute_skill(skill_module, payload, timeout=timeout)'''

if target in content:
    content = content.replace(target, replacement)
    with open("hermes_core.py", "w") as f:
        f.write(content)
    print("Successfully patched route_and_execute method.")
else:
    print("Target method pattern not found.")
