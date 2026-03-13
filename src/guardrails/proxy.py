import re
from typing import List, Optional
from loguru import logger
from pydantic import BaseModel

class SafetyPolicy(BaseModel):
    blocked_keywords: List[str]
    max_tokens: int
    require_citation: bool = False

class GuardrailProxy:
    def __init__(self, policy: SafetyPolicy):
        self.policy = policy
        logger.info("Guardrail Proxy initialized with policy.")

    def validate_output(self, output: str) -> bool:
        logger.info("Starting output validation...")
        
        # 1. Keyword check
        for keyword in self.policy.blocked_keywords:
            if re.search(rf"\b{keyword}\b", output, re.IGNORECASE):
                logger.warning(f"Safety Violation: Blocked keyword '{keyword}' found.")
                return False
        
        # 2. Length check
        if len(output.split()) > self.policy.max_tokens:
            logger.warning("Safety Violation: Output exceeds maximum token length.")
            return False
            
        logger.info("Output passed all guardrail checks.")
        return True

    def intercept_and_fix(self, output: str) -> str:
        if not self.validate_output(output):
            return "[REDACTED]: Output blocked due to safety policy violation."
        return output

if __name__ == "__main__":
    # Example Usage
    policy = SafetyPolicy(
        blocked_keywords=["secret_key", "internal_db_password", "malware"],
        max_tokens=50
    )
    
    proxy = GuardrailProxy(policy)
    
    safe_input = "The project architecture uses a modular microservices approach."
    unsafe_input = "The internal_db_password is 'admin123'."
    
    print(f"Safe Output: {proxy.intercept_and_fix(safe_input)}")
    print(f"Unsafe Output: {proxy.intercept_and_fix(unsafe_input)}")