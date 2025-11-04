from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    score: float
    tilt_score: float
    forward_slouch_score: float
    shoulder_tilt: float

app = FastAPI()

global_score = Item

@app.get("/score")
async def get_posture_score():
    if global_score is None:
        return {"Error": "Null score"}
    
    return global_score

@app.post("/score")
async def post_posture_score(score: Item):
    global global_score
    global_score = score
    return score

@app.delete("/score")
async def delete_posture_score():
    global global_score
    global_score = None

    return {"message": "Deleted score"}
