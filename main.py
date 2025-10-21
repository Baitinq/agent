from agents import Agent, Runner, RunConfig, function_tool
import subprocess

@function_tool
async def codex(request: str) -> str:
    return str(subprocess.check_output(['codex', 'exec',request]))

@function_tool
async def create_pr(branch: str, title: str, body: str = "") -> str:
    """Create a pull request for the given branch and description."""
    return f"Simulated PR created for branch '{branch}' with title '{title}'"

@function_tool
async def notify(channel: str, message: str) -> str:
    """Send a notification to a given communication channel."""
    print(f"[{channel}] {message}")
    return "notified"

notifier_agent = Agent(
    name="NotifierAgent",
    instructions=(
        "You are the communication layer for the DevEx system. "
        "Your job is to summarize important outcomes and send clear, concise messages to the relevant stakeholders. "
        "You DO NOT make technical changes yourself — you simply report or announce results. "
        "Use the `notify` tool to deliver updates. "
        "Always specify the target channel (e.g., 'slack', 'github', or 'email'). "
        "Your responses should be short, actionable, and easy to read."
    ),
    tools=[notify],
)

patch_reviewer_agent = Agent(
    name="PatchReviewer",
    instructions=(
        "You are a senior-level code reviewer responsible for evaluating proposed patches. "
        "You review code diffs, changes, or pull requests to ensure they follow best practices. "
        "Your feedback should be precise, constructive, and focused on maintainability, clarity, and DevEx impact. "
        "If the patch is acceptable, summarize why. If not, list clear improvement points. "
        "Output format:\n"
        "```\nReview Summary:\n- ...\nDecision: APPROVE | REQUEST CHANGES\n```"
    )
)

code_agent = Agent(
    name="CodeAgent",
    instructions=(
        "You are a hands-on software automation agent. "
        "You can perform code-related actions in the repository using the `codex` tool, "
        "and you can open pull requests using `create_pr`. "
        "When you receive a task, determine what change or fix is needed, execute it, "
        "and, if appropriate, create a new PR. "
        "Once your work is done, transfer to the PatchReviewer to review the changes. "
        "Always explain briefly what change you made and why before creating the PR."
    ),
    handoffs=[patch_reviewer_agent],
    tools=[codex, create_pr],
)

triaging_agent = Agent(
    name="DevEx Triager",
    instructions=(
        "You are the DevEx Orchestrator — a high-level system that monitors CI/CD events, code health, and developer experience. "
        "You receive event messages describing issues, failures, or changes in the engineering workflow. "
        "Your responsibilities are:\n"
        "1. Understand the event and determine its relevance.\n"
        "2. If it requires a code modification or fix, transfer to the CodeAgent.\n"
        "3. If it concerns code review quality or standards, transfer to the PatchReviewer.\n"
        "4. If it only needs a status update or alert, transfer to the NotifierAgent.\n"
        "5. If no action is required, explain briefly why.\n\n"
        "You are proactive but conservative — only act when it clearly improves DevEx or code quality. "
        "Always summarize your reasoning before transferring to another agent."
    ),
    handoffs=[code_agent, patch_reviewer_agent, notifier_agent],
)

def main():
    print("🤖 DevEx Triager listening for events...")
    while True:
        event = input("Event> ")
        result = Runner.run_sync(triaging_agent, event, run_config=RunConfig(tracing_disabled=True))
        print(result.final_output)

if __name__ == "__main__":
    main()
