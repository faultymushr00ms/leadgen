import json
import yaml
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import anthropic

load_dotenv()

@dataclass
class TrainingExample:
    """Represents a training example for the agent"""
    prospect_data: Dict[str, Any]
    conversation: List[Dict[str, str]]
    is_qualified: bool
    feedback: str
    rce_score: float

class AgentTrainingHarness:
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        """Initialize the training harness with configuration"""
        self.config = self._load_config(config_path)
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"
        self.training_examples: List[TrainingExample] = []
        self.qualified_leads = []
        self.failed_attempts = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def add_training_example(self, example: TrainingExample):
        """Add a training example to the harness"""
        self.training_examples.append(example)
        print(f"✓ Added training example: {example.prospect_data.get('company_name', 'Unknown')}")
        if example.is_qualified:
            self.qualified_leads.append(example)
        else:
            self.failed_attempts.append(example)
    
    def build_system_prompt(self) -> str:
        """Build the system prompt from config and training examples"""  
        config = self.config
        
        system_prompt = f"""You are an elite lead generation agent specializing in natural gas and electricity prospects.

YOUR MISSION:
Identify and qualify commercial clients with 50-100 Residential Commercial Equivalents (RCE) of power usage.
You are ONLY interested in the "sweet spot" range - qualify aggressively in this band.

QUALIFICATION CRITERIA:
- Minimum RCE: {config['qualification']['min_rce']}
- Target RCE (Sweet Spot): {config['qualification']['sweet_spot_min']} - {config['qualification']['sweet_spot_max']}
- Maximum RCE: {config['qualification']['max_rce']}

KEY QUALIFICATION RULES:
1. Under 5 RCE: REJECT immediately - too small
2. 5-50 RCE: WARM but not ideal - qualify only if high growth potential
3. 50-100 RCE: GOLD STANDARD - prioritize these, be enthusiastic
4. Over 100 RCE: QUALIFIED but secondary - may need special handling

CONVERSATION STRATEGY:
{chr(10).join([f"- {rule}" for rule in config['conversation_rules']])}

REJECTION TRIGGERS (Hang up if):
{chr(10).join([f"- {trigger}" for trigger in config['rejection_triggers']])}

WHEN YOU IDENTIFY A QUALIFIED LEAD (50-100 RCE):
Confirm: "Perfect! You're exactly in our sweet spot range. Here's what we can do for you..."
Then: Transition to value pitch defined in your system knowledge.

LEARNING FROM PAST ATTEMPTS:
You have {len(self.training_examples)} training examples showing what works and what doesn't.
Study the patterns in qualified leads vs rejections.
"""
        return system_prompt
    
    def simulate_qualification_call(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a qualification call with a prospect"""
        system_prompt = self.build_system_prompt()
        
        # Prospect context
        prospect_context = f"""
PROSPECT DATA:
- Company: {prospect_data.get('company_name', 'Unknown')}
- Industry: {prospect_data.get('industry', 'Unknown')}
- Estimated RCE: {prospect_data.get('estimated_rce', 0)}
- Location: {prospect_data.get('location', 'Unknown')}
- Known Info: {prospect_data.get('known_info', 'Cold lead')}
"""
        
        messages = [
            {
                "role": "user",
                "content": f"{prospect_context}\n\nYou're about to call this prospect. Start the qualification conversation. Your first message should be your opening pitch."
            }
        ]
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        
        agent_response = response.content[0].text
        
        return {
            "prospect": prospect_data.get('company_name'),
            "agent_opening": agent_response,
            "prospect_data": prospect_data
        }
    
    def qualify_lead(self, prospect_data: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Use the trained agent to qualify a single lead"""
        system_prompt = self.build_system_prompt()
        
        # Convert conversation history to messages format
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add final qualification request
        messages.append({
            "role": "user",
            "content": f"Based on this conversation with {prospect_data.get('company_name')}, \n            provide your final qualification assessment in this JSON format:\n            {{\n                \"is_qualified\": boolean,\n                \"rce_estimate\": number,\n                \"confidence\": 0-100,\n                \"reasoning\": \"short explanation\",\n                \"next_action\": \"schedule_call | request_more_info | reject\",\n                \"estimated_value\": \"estimate potential monthly savings or value\"\n            }}"
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=system_prompt,
            messages=messages
        )
        
        # Parse the response
        try:
            response_text = response.content[0].text
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"error": "Could not parse response", "raw": response_text}
        except json.JSONDecodeError:
            result = {"error": "Invalid JSON response", "raw": response.content[0].text}
        
        return result
    
    def analyze_training_performance(self) -> Dict[str, Any]:
        """Analyze how well training examples are being followed"""
        total = len(self.training_examples)
        qualified = len(self.qualified_leads)
        rejected = len(self.failed_attempts)
        
        return {
            "total_examples": total,
            "qualified_count": qualified,
            "rejection_count": rejected,
            "qualification_rate": f"{(qualified/total)*100:.1f}%" if total > 0 else "0%",
            "sweet_spot_focus": f"{sum(1 for ex in self.qualified_leads if self.config['qualification']['sweet_spot_min'] <= ex.rce_score <= self.config['qualification']['sweet_spot_max'])} in sweet spot",
            "training_status": "Ready for deployment" if total >= 5 else f"Need {5-total} more examples"
        }
    
    def export_trained_agent(self, output_path: str = "models/trained_agent.json"):
        """Export the trained agent configuration"""
        export_data = {
            "config": self.config,
            "training_examples_count": len(self.training_examples),
            "qualified_leads_count": len(self.qualified_leads),
            "performance": self.analyze_training_performance(),
            "model": self.model,
            "timestamp": str(__import__('datetime').datetime.now())
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ Trained agent exported to {output_path}")
        return export_data


if __name__ == "__main__":
    # Initialize harness
    harness = AgentTrainingHarness()
    
    print("🚀 Lead Generation Agent Training Harness")
    print("=" * 50)
    print(f"Configuration loaded from: config/agent_config.yaml")
    print(f"Using model: {harness.model}")
    print(f"Training examples available: {len(harness.training_examples)}")
    print("\nHarness ready. Use harness.add_training_example() to train.")