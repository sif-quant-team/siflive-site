from dotenv import load_dotenv; load_dotenv()
from app.ingest import run_ingest_once

if __name__ == "__main__":
    run_ingest_once()
    print("Ingest complete.")