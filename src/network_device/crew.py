from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from dotenv import load_dotenv
load_dotenv()

import panel as pn
import time

chat_interface = pn.chat.ChatInterface()

from crewai.tasks.task_output import TaskOutput

def print_output(output: TaskOutput):

    message = output.raw
    #chat_interface.send(message, user=output.agent, respond=False)


@CrewBase
class NetworkDevice():
	"""NetworkDevice crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools

	@agent
	def input_formatter(self) -> Agent:
		return Agent(
			config=self.agents_config['input_formatter'],
			verbose=True
		)

	@agent
	def network_troubleshooter(self) -> Agent:
		return Agent(
			config=self.agents_config['network_troubleshooter'],
			verbose=True
		)
	'''
	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)
	'''
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task

	@task
	def formatting_task(self) -> Task:
		return Task(
			config=self.tasks_config['formatting_task'],
			output_file="formatting_task.txt"
		)

	@task
	def troubleshooting_task(self) -> Task:
		return Task(
			config=self.tasks_config['troubleshooting_task'],
			callback=print_output,
			human_input=True
		)
	
	'''
	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)
	'''
	@crew
	def crew(self) -> Crew:
		"""Creates the NetworkDevice crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
