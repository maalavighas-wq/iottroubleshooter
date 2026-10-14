"""
FastAPI application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="IoT Troubleshooter API",
    description="Smart IoT Device Troubleshooting Chatbot — IBM Mini Project",
    version="1.0.0",
)

# CORS — allow the Vite dev server and production build
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "IoT Troubleshooter API is running.",
        "docs": "/docs",
        "health": "/health",
    }
