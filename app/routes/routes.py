# app/routes/routes.py
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from fastapi import HTTPException
from autogen_agentchat.conditions import TextMentionTermination,MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from app.agents.hr_agents import hr_assistant,policy_retriever,policy_content_maker,finance_agent
from app.app_generalize_settings import model_client
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TaskResult

router = APIRouter()


@router.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join("./frontend/dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend build not found"}


class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:

        user_query = request.question

        # Set up termination condition
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(max_messages=10)
        termination = text_mention_termination | max_messages_termination

        # Create the AutoGen team
        agent_team = SelectorGroupChat(
            [hr_assistant,policy_retriever,policy_content_maker],
            model_client=model_client,
            termination_condition=termination,
            max_turns=5,
            allow_repeated_speaker=True,
            selector_prompt=
            f"""
            Select an agent to perform task.

            select an agent from {[hr_assistant,policy_retriever,policy_content_maker,finance_agent]} to perform the next task.
            Make sure the hr_assistant agent has assigned tasks before other agents start working.
            Only select one agent.
            """
        )
            
        # Run the team with the user input and display results
        stream = agent_team.run_stream(task=user_query)
        # await Console(stream)

        final_result = None
        final_answer = ""
        async for message in stream:
            if getattr(message, "source", None) == "hr_assistant":
                # print(f"\n{message.source}: {message.content}\n")
                final_answer = message.content
                final_answer = final_answer.replace("TERMINATE", "").strip()

        # async for message in stream:
        #     if isinstance(message, TaskResult):
        #         final_result = message

        # if final_result:
        #     # Option 1: get last message content
        #     if final_result.messages:
        #         print("Final Answer:", final_result.messages[-1].content)
        #         final_answer = final_result.messages[-1].content

        # Print the assistant’s response
        print("\n=== Assistant’s Response ===")
        print(final_answer)
        print("============================\n")

        return {"answer": final_answer}

    except Exception as e:
        print('e',e)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
