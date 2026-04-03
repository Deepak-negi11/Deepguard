from app.database import SessionLocal, Base, engine
from app.models import User, VerificationRequest
from app.services.verification import VerificationTaskInput, run_request_analysis

# Setup test db
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    user = User(email="debug@example.com", password_hash="pw")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    req = VerificationRequest(user_id=user.id, request_type="news", status="pending", payload_excerpt="test")
    db.add(req)
    db.commit()
    db.refresh(req)
    
    task_input = VerificationTaskInput(
        task_id=req.id,
        request_id=req.id,
        request_type="news",
        text="Breaking exclusive leaked report claims a secret urgent event is unfolding right now."
    )
    
    run_request_analysis(task_input)
    
    db.refresh(req)
    print(f"Final status: {req.status}")
    from app.services.job_store import job_store
    job = job_store.get(req.id)
    print(f"Final step: {job.current_step if job else 'no job'}")
finally:
    db.close()
