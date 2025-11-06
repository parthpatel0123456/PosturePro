from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import asyncio

class Item(BaseModel):
    score: float
    tilt_score: float
    forward_slouch_score: float
    shoulder_tilt: float

app = FastAPI()

global_score = None

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

@app.websocket("/score/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        if global_score is not None:
            await websocket.send_json(global_score.model_dump())
        await asyncio.sleep(0.2)
