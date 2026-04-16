from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from agent import compiled_graph

print('Running quick RAG intent test...')
state = {"messages": [HumanMessage(content="Hi, what are your pricing plans?")]} 
res = compiled_graph.invoke(state, config={"configurable": {"thread_id": "quick-test-1"}})
print('Result keys:', list(res.keys()))
print('Messages:')
for m in res.get('messages', []):
    print(type(m), getattr(m, 'content', None)[:100])

# Print rag_context and intent if present
print('\nState returned:')
for k in ('intent','rag_context','lead_info','lead_captured'):
    if k in res:
        print(f"{k}: {res[k]}")
