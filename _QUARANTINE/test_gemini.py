import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Executor, Node, Workflow

load_dotenv()
os.environ['GEMINI_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')
init()

test_agent = Node.agent('Test', 'Say hello', llm_config=LlmConfig.gemini('gemini-2.5-flash'))
wf = Workflow('test')
wf.add_node(test_agent)

try:
    Executor(LlmConfig.gemini('gemini-2.5-flash')).execute(wf)
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
