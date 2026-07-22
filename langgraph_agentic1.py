import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START,END,StateGraph
from dotenv import load_dotenv
from typing import *

load_dotenv()

class ExplainerState(TypedDict):
    topic:str
    explanation:str
    word_count:int
    need_simplication:bool
    attempts:int
    
llm=ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0
)

def create_explanation(state:ExplainerState):
    prompt=f"""You have given a {state['topic']} and
    you have to create a explanation regarding this 
    topic and if you dont know topic just give i dont know
    """
    response=llm.invoke(prompt)
    return {state["explanation"]:response.content}

def check_answer(state:ExplainerState):
    count=len(state["explanation"])
    if count>120:
        state["need_simplication"]=True
    return {state["word_count"]:count}

def simplify_answer(state:ExplainerState):
    prompt=f"You are the ai advisor only give {state['explanation']} under 120 words only "
    response=llm.invoke(prompt)
    return {state["explanation"]:response.content}

def route_after_check(state:ExplainerState):
    if not state["need_simplication"]:
        return END
    if state["attempts"]>=2:
        return END
    return state["explanation"]

builder=StateGraph(ExplainerState)
builder.add_node("create_explanation",create_explanation)
builder.add_node("check_answer",check_answer)
builder.add_node("create_explanation",create_explanation)
builder.add_edge(START,"create_explanation")
builder.add_edge("create_explanation","check_answer")
builder.add_conditional_edges(
    "check_answer",
    route_after_check,{
        "simplify_answer":simplify_answer,
        END:END
    }
    
)
builder.add_edge("check_answer","simplify_answer")
graph=builder.complile()

if __name__ == "__main__":
    topic = input("Enter a topic to explain: ").strip()
 
    initial_state = {
        # TODO: add initial values
         "topic":topic,
    "explanation":"",
    "word_count":0,
    "need_simplication":False,
    "attempts":2
    }
 
    result = graph.invoke(initial_state)
 
    print("\nFINAL EXPLANATION")
    print(result["explanation"])
    print("Word count:", result["word_count"])
    print("Simplification attempts:", result["attempts"])


