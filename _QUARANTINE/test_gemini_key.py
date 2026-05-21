import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Executor, Node, Workflow

load_dotenv()
key = os.environ.get('GOOGLE_API_KEY', '')
init()

try:
    config = LlmConfig.gemini('gemini-2.5-flash', api_key=key)
    test_agent = Node.agent('Test', 'Say hello', llm_config=config)
    wf = Workflow('test')
    wf.add_node(test_agent)
    Executor(config).execute(wf)
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
