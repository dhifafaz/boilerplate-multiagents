import os
from textwrap import dedent
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from eb_labs.agent import Agent

from source.config import settings
from source.agents.case_name_extractor.prompt import PROMPTS
from source.agents.base import BaseAgent

class CaseNamingOutput(BaseModel):
	case_name: str = Field(..., description="A concise, human-readable case name in Bahasa Indonesia.")


class CaseNamingAgent(BaseAgent):
	def __init__(
		self,
		human_prompt: str = "{report}",
	):
		super().__init__(
			agent_name="Case Naming Agent",
			temperature=0.3,
			max_tokens=1000,
			reasoning_effort='low'
		)
		self.human_prompt = human_prompt
		self.agent = Agent(
			model=self.model,
			instructions=dedent(PROMPTS['case_naming_system_prompt']),
			use_json_mode=True,
			debug_mode=True,
			output_schema=CaseNamingOutput
		)

	async def run(self, report: str) -> str:
		full_prompt = self.human_prompt.format(report=report)
		response = await self.agent.arun(full_prompt)
		return response.content.case_name