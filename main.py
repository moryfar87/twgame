from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models
from typing import List


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/posts/{post_id}/vote")
def vote_post(post_id: int, vote_type: str, user_id: int, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if vote_type == "upvote":
        db_post.upvotes += 1
    elif vote_type == "downvote":
        db_post.downvotes += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    db.commit()
    return {"message": "Vote recorded successfully"}

@app.post("/comments/{comment_id}/vote")
def vote_comment(comment_id: int, vote_type: str, user_id: int, db: Session = Depends(get_db)):
    db_comment = db.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if vote_type == "upvote":
        db_comment.upvotes += 1
    elif vote_type == "downvote":
        db_comment.downvotes += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    db.commit()
    return {"message": "Vote recorded successfully"}

