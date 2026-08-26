import json
import redis
import os

class RedisStateManager:
    def __init__(self):
        # Connect to the local Redis container running on port 6379
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.state_key = "hosteva_swarm_state"

    def get_state(self):
        state_str = self.redis_client.get(self.state_key)
        if state_str:
            return json.loads(state_str)
        # Default initial state
        return {"strike_registry": {}, "kickback_context": None, "skills": {}}

    def save_state(self, state_dict):
        self.redis_client.set(self.state_key, json.dumps(state_dict))

    def get_strike_count(self, agent_name):
        state = self.get_state()
        return state.get("strike_registry", {}).get(agent_name, 0)

    def increment_strike(self, agent_name):
        state = self.get_state()
        registry = state.get("strike_registry", {})
        registry[agent_name] = registry.get(agent_name, 0) + 1
        state["strike_registry"] = registry
        self.save_state(state)
        return registry[agent_name]

    def clear_kickback(self):
        state = self.get_state()
        state["kickback_context"] = None
        self.save_state(state)

    def clear_all(self):
        self.redis_client.delete(self.state_key)
