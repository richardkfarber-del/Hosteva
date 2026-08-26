import os
import subprocess
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

load_dotenv()
init()

def execute_tests(state):
    try:
        # Run pytest specifically on the backend tests where the timeout is happening
        result = subprocess.run(['/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/pytest', '/home/rdogen/OpenClaw_Factory/projects/Hosteva/tests/'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return "SUCCESS: All tests passed.\n" + result.stdout
        else:
            return "FAILED: Tests failed.\n" + result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return "CRITICAL FAILURE: TIMEOUT. The tests took too long to run. This is usually caused by an unclosed database connection or an infinite loop."
    except Exception as e:
        return f"CRITICAL FAILURE: ERROR: {str(e)}"

qa_node = Node.agent('QA Swarm', 'Run the tests and report the results.', llm_config=LlmConfig.ollama('llama3.1-orchestrator'), tools=[execute_tests])

def coulson_evaluation(state):
    out = state.node_outputs.get('QA Swarm', '').lower()
    if 'fail' in out or 'error' in out or 'timeout' in out:
        return 'Rocket Raccoon'
    return 'Deployment'

coulson_node = Node.condition('Coulson Router', coulson_evaluation)
rocket_node = Node.agent('Rocket Raccoon', 'The tests failed or timed out. Read the test files and the app code, figure out what is causing the failure (e.g. missing mock, unclosed db session, invalid import), and fix the code.', llm_config=LlmConfig.ollama('qwen2.5-coder:7b'))

deploy_node = Node.agent('Deployment', 'The tests passed. We are ready for deployment. Output a success message.', llm_config=LlmConfig.ollama('llama3.1-orchestrator'))

workflow = Workflow('Hosteva_Sprint_Loop')

ids = {
    'QA': workflow.add_node(qa_node),
    'Coulson': workflow.add_node(coulson_node),
    'Rocket': workflow.add_node(rocket_node),
    'Deploy': workflow.add_node(deploy_node)
}

workflow.connect(ids['QA'], ids['Coulson'])
workflow.connect(ids['Rocket'], ids['QA'])

if __name__ == '__main__':
    print("Igniting Phoenix Engine at QA Node...")
    workflow.set_graph_metadata('allow_cycles', True)
    executor = Executor(LlmConfig.ollama('llama3.1-orchestrator'), timeout_seconds=3600)
    # Start execution at QA node
    final_state = executor.execute(workflow, start_node_id=ids['QA'])
    print('Workflow executed successfully.')
    print('Final State:', final_state.node_outputs.get('Deployment', final_state.node_outputs.get('QA Swarm', '')))
