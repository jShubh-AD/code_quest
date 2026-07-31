from fastapi import APIRouter, HTTPException

q_router =  APIRouter(prefix="/questions", tags=["Questtions"])

@q_router.get("/")
async def get_questions():
    # get all questions
    pass 

@q_router.get("/{id}")
async def get_question_by_id(id: int, ans: bool = False):
    # get question by id with ans if True in query
    pass

@q_router.post("/")
async def create_question():
    # create question
    pass

@q_router.patch("/{id}")
async def update_question(id: int):
    # update question
    pass

@q_router.default("/{id}")
async def update_question(id: int):
    # delete question
    pass