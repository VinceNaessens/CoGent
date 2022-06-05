from typing import Dict, List

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.get_synonyms import get_synonyms
from api.get_art import get_art

app = FastAPI()
origins = [
    "http://localhost:4200",        # put here our frontend site to fix cors
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_endpoint() -> Dict[str, str]:
    return {"message": "test succeeded"}


@app.get("/synonyms")
def synonym_endpoint(basis_word: str) -> Dict[str, List[str]]:
    res = get_synonyms(basis_word=basis_word)
    return {"message": res}

@app.get("/art")
def art_endpoint(basis_word: str) -> Dict[str, List[str]]:
    res = get_art(basis_word=basis_word)
    return {"message": res}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000)
