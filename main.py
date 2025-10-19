from agents import Agent, Runner, RunConfig

def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.", run_config=RunConfig(tracing_disabled=True))
    print(result.final_output)

if __name__ == "__main__":
    main()
