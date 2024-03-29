from openai import OpenAI
import os
from pinecone import Pinecone, ServerlessSpec
import yaml
from dotenv import load_dotenv
from instacart import order_medicine, order_coffee
import threading

# Load default environment variables (.env)
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-4"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV")
DEBUG=False

pc = Pinecone(api_key=PINECONE_API_KEY)


# Prompt Initialization
with open('prompts.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

def generate(prompt):
    completion = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": "You are an intelligent agent with thoughts and memories. You have a memory which stores your past thoughts and actions and also how other users have interacted with you."},
        {"role": "system", "content": "Keep your thoughts relatively simple and concise"},
        {"role": "system", "content": data["boyfriend-role"]},
        {"role": "user", "content": prompt},
        ]
    )

    return completion.choices[0].message.content


#PINECONE_API_ENV = "asia-southeast1-gcp"


# Counter Initialization
with open('memory_count.yaml', 'r') as f:
    counter = yaml.load(f, Loader=yaml.FullLoader)

# internalThoughtPrompt = data['internal_thought']
# externalThoughtPrompt = data['external_thought']
# internalMemoryPrompt = data['internal_thought_memory']
# externalMemoryPrompt = data['external_thought_memory']

# Thought types, used in Pinecone Namespace
THOUGHTS = "Thoughts"
QUERIES = "Queries"
INFORMATION = "Information"
ACTIONS = "Actions"

# Top matches length
k_n = 3

# initialize pinecone
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)

# initialize openAI
client = OpenAI(api_key=OPENAI_API_KEY)

def get_ada_embedding(text):
        text = text.replace("\n", " ")
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )

        return response.data[0].embedding

def read_txtFile(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

class Agent():
    def __init__(self, table_name=None) -> None:
        self.table_name = table_name
        self.memory = None
        self.thought_id_count = int(counter['count'])
        self.last_message = ""

    # Keep Remebering!
    # def __del__(self) -> None:
    #     with open('memory_count.yaml', 'w') as f:
    #         yaml.dump({'count': str(self.thought_id_count)}, f)
    
    

    def giveMemory(self):
        list_indexes = pc.list_indexes().indexes
        for index in list_indexes:
            if(self.table_name == index['name']):
                self.memory = pc.Index(self.table_name)
                return
            
        pc.create_index(
            name=self.table_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-west-2'
            )
        ) 
        self.memory = pc.Index(self.table_name)
        

    
    # Adds new Memory to agent, types are: THOUGHTS, ACTIONS, QUERIES, INFORMATION
    def updateMemory(self, new_thought, thought_type):
        with open('memory_count.yaml', 'w') as f:
             yaml.dump({'count': str(self.thought_id_count)}, f)

        if thought_type==INFORMATION:
            new_thought = "This is information fed to you by the user:\n" + new_thought
        elif thought_type==QUERIES:
            new_thought = "The user has said to you before:\n" + new_thought
        elif thought_type==THOUGHTS:
            # Not needed since already in prompts.yaml
            # new_thought = "You have previously thought:\n" + new_thought
            pass
        elif thought_type==ACTIONS:
            # Not needed since already in prompts.yaml as external thought memory
            pass

        vector = get_ada_embedding(new_thought)
        upsert_response = self.memory.upsert(
        vectors=[
            {
            'id':f"thought-{self.thought_id_count}", 
            'values':vector, 
            'metadata':
                {"thought_string": new_thought
                }
            }],
	    namespace=thought_type,
        )

        self.thought_id_count += 1

    # Agent thinks about given query based on top k related memories. Internal thought is passed to external thought
    def internalThought(self, query) -> str:
        query_embedding = get_ada_embedding(query)
        query_results = self.memory.query(vector=query_embedding, top_k=2, include_metadata=True, namespace=QUERIES)
        thought_results = self.memory.query(vector=query_embedding, top_k=2, include_metadata=True, namespace=THOUGHTS)
        results = query_results.matches + thought_results.matches
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        top_matches = "\n\n".join([(str(item.metadata["thought_string"])) for item in sorted_results])
        if DEBUG:
            print("------------TOP MATCHES------------")
            print(top_matches)
        
        internalThoughtPrompt = data['internal_thought']
        internalThoughtPrompt = internalThoughtPrompt.replace("{query}", query).replace("{top_matches}", top_matches).replace("{last_message}", self.last_message)
        if DEBUG:
            print("------------INTERNAL THOUGHT PROMPT------------")
            print(internalThoughtPrompt)
        internal_thought = generate(internalThoughtPrompt) # OPENAI CALL: top_matches and query text is used here
        
        # Debugging purposes
        if DEBUG:
            print("------------INTERNAL THOUGHT PROMPT------------")
            print(internal_thought)

        internalMemoryPrompt = data['internal_thought_memory']
        internalMemoryPrompt = internalMemoryPrompt.replace("{query}", query).replace("{internal_thought}", internal_thought).replace("{last_message}", self.last_message)
        self.updateMemory(internalMemoryPrompt, THOUGHTS)
        return internal_thought, top_matches

    def action(self, query) -> str:
        internal_thought, top_matches = self.internalThought(query)
        
        externalThoughtPrompt = data['external_thought']
        externalThoughtPrompt = externalThoughtPrompt.replace("{query}", query).replace("{top_matches}", top_matches).replace("{internal_thought}", internal_thought).replace("{last_message}", self.last_message)
        if DEBUG:
            print("------------EXTERNAL THOUGHT PROMPT------------")
            print(externalThoughtPrompt)
        external_thought = generate(externalThoughtPrompt) # OPENAI CALL: top_matches and query text is used here

        externalMemoryPrompt = data['external_thought_memory']
        externalMemoryPrompt = externalMemoryPrompt.replace("{query}", query).replace("{external_thought}", external_thought)
        self.updateMemory(externalMemoryPrompt, THOUGHTS)
        request_memory = data["request_memory"]
        self.updateMemory(request_memory.replace("{query}", query), QUERIES)
        self.last_message = query
        if DEBUG:
            print("------------EXTERNAL THOUGHT------------")
            print(external_thought)
        if "[ORDER_COFFEE]" in external_thought:
            # Launch order_coffee in a separate thread
            coffee_thread = threading.Thread(target=order_coffee)
            coffee_thread.start()
            return "Don't worry, I'll order you some coffee" + external_thought

        if "[ORDER_MEDICINE]" in external_thought:
            medicine_thread = threading.Thread(target=order_medicine)
            medicine_thread.start()
            return "Don't worry, I'll order you some medicine" + external_thought
        
        return external_thought
        
    # Make agent think some information
    def think(self, text) -> str:
        self.updateMemory(text, THOUGHTS)


    # Make agent read some information
    def read(self, text) -> str:
        texts = text_splitter.split_text(text)
        vectors = []
        for t in texts:
            t = "This is information fed to you by the user:\n" + t
            vector = get_ada_embedding(t)
            vectors.append({
                'id':f"thought-{self.thought_id_count}", 
                'values':vector, 
                'metadata':
                    {"thought_string": t, 
                     }
                })
            self.thought_id_count += 1

        upsert_response = self.memory.upsert(
        vectors,
	    namespace=INFORMATION,
        )
    # Make agent read a document
    def readDoc(self, text) -> str:
        texts = text_splitter.split_text(read_txtFile(text))
        vectors = []
        for t in texts:
            t = "This is a document fed to you by the user:\n" + t
            vector = get_ada_embedding(t)
            vectors.append({
                'id':f"thought-{self.thought_id_count}", 
                'values':vector, 
                'metadata':
                    {"thought_string": t, 
                     }
                })
            self.thought_id_count += 1

        upsert_response = self.memory.upsert(
        vectors,
	    namespace=INFORMATION,
        )
