import asyncio
from temporalio.client import Client

# We import the workflow class just for typing/reference, or we can use string name
from swarm_workflow import VectorSwarmWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    print("Pushing 'Sprint-12-Regression' to the Temporal cluster...")
    
    # Start the workflow asynchronously
    handle = await client.start_workflow(
        VectorSwarmWorkflow.run,
        "Sprint-12-Regression",
        id="sprint-12-run-001",
        task_queue="hosteva-swarm-queue",
    )
    
    print(f"✅ Workflow started successfully!")
    print(f"Workflow ID: {handle.id}")
    print(f"Run ID: {handle.result_run_id}")

if __name__ == "__main__":
    asyncio.run(main())
