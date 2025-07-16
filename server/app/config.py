import os
import logging

DATA_DIR = "./data"
RAG_STORE_DIR = "./store_rag"
RESEARCH_STORE_DIR = "./store_research"  # for future extension

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAG_STORE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")
