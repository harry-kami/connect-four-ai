from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import math
import ai_engine as ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameRequest(BaseModel):
    board: list
    depth: int = 4

@app.post("/get-move")
async def get_move(request: GameRequest):
    board_array = np.array(request.board)
    board_array = np.flip(board_array, 0) 
    
    # 1. Run AI
    col, minimax_score = ai.minimax(board_array, request.depth, -math.inf, math.inf, True)
    
    # 2. Crash Prevention (The Fix)
    if col is None:
        # If AI returns None, it means no moves are possible (Draw) 
        # or the game state passed to it was already won.
        return {
            "column": -1, # Frontend will interpret -1 as "Game Over"
            "score": 0
        }
        
    return {
        "column": int(col),
        "score": float(minimax_score)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)