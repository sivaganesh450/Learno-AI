from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List
import json
from app.services.agents import roadmap_agent, resources_agent, summarizer_agent, quiz_agent, math_solver_agent, job_search_agent
from app.api.v1.deps import get_current_user
from app.models.user import UserInDB

router = APIRouter()

# Allowed file types for RAG
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.py', '.js', '.json', '.csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class AgentRequest(BaseModel):
    message: str
    topic: Optional[str] = None
    skill_level: Optional[str] = "beginner"
    duration: Optional[str] = "3 months"
    resource_type: Optional[str] = "all"
    skills_known: Optional[str] = ""
    session_id: Optional[str] = "default"


class QuizStartRequest(BaseModel):
    domain: str
    purpose: str  # interview, exam, knowledge
    difficulty: str  # easy, moderate, difficult
    session_id: Optional[str] = "default"


class QuizMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class MathProblemRequest(BaseModel):
    problem: str


class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = ""


class AgentResponse(BaseModel):
    agent: str
    response: str


# Streaming endpoint for roadmap
@router.post("/roadmap/stream")
async def generate_roadmap_stream(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate a personalized learning roadmap with streaming response
    """
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in roadmap_agent.generate_stream(
                message=request.message,
                topic=request.topic or request.message,
                skill_level=request.skill_level,
                duration=request.duration,
                skills_known=request.skills_known
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Streaming endpoint for resources
@router.post("/resources/stream")
async def get_resources_stream(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get curated learning resources with streaming response
    """
    # Use user ID + session_id for unique session tracking
    session_key = f"{current_user.id}_{request.session_id}"
    
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in resources_agent.get_resources_stream(
                message=request.message,
                topic=request.topic or request.message,
                resource_type=request.resource_type,
                session_id=session_key
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Streaming endpoint for Summarizer with RAG
@router.post("/qa/stream")
async def answer_question_stream(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Answer a question with streaming response using RAG if documents are uploaded
    """
    # Use user ID + session_id for unique session tracking
    session_key = f"{current_user.id}_{request.session_id}"
    
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in summarizer_agent.answer_stream(question=request.message, session_id=session_key):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/roadmap", response_model=AgentResponse)
async def generate_roadmap(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate a personalized learning roadmap
    """
    try:
        response = await roadmap_agent.generate(
            message=request.message,
            topic=request.topic or request.message,
            skill_level=request.skill_level,
            duration=request.duration,
            skills_known=request.skills_known
        )
        return AgentResponse(
            agent="Roadmap Generator",
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating roadmap: {str(e)}")


@router.post("/resources", response_model=AgentResponse)
async def get_resources(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get curated learning resources
    """
    try:
        response = await resources_agent.get_resources(
            message=request.message,
            topic=request.topic or request.message,
            resource_type=request.resource_type
        )
        return AgentResponse(
            agent="Resources Provider",
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {str(e)}")


@router.post("/qa", response_model=AgentResponse)
async def answer_question(
    request: AgentRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Answer a question using the QA agent
    """
    try:
        response = await summarizer_agent.answer(question=request.message)
        return AgentResponse(
            agent="Summarizer",
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@router.get("/list")
async def list_agents(current_user: UserInDB = Depends(get_current_user)):
    """
    List all available agents
    """
    return {
        "agents": [
            {
                "id": "roadmap",
                "name": "Roadmap Generator",
                "description": "Create personalized learning paths tailored to your goals and skill level.",
                "endpoint": "/api/v1/agents/roadmap"
            },
            {
                "id": "resources",
                "name": "Resources Provider",
                "description": "Access curated learning materials, tutorials, and resources.",
                "endpoint": "/api/v1/agents/resources"
            },
            {
                "id": "qa",
                "name": "Summarizer",
                "description": "Upload documents and get summaries, insights, and answers.",
                "endpoint": "/api/v1/agents/qa"
            },
            {
                "id": "quiz",
                "name": "Question Answering System",
                "description": "Interactive Q&A for interview prep, exam preparation, and knowledge testing.",
                "endpoint": "/api/v1/agents/quiz"
            },
            {
                "id": "math",
                "name": "Problem Solver",
                "description": "Solve complex math problems step-by-step using Chain of Thought reasoning.",
                "endpoint": "/api/v1/agents/math"
            },
            {
                "id": "jobs",
                "name": "Job Search",
                "description": "Search for recent job listings using Adzuna. Find opportunities worldwide.",
                "endpoint": "/api/v1/agents/jobs"
            }
        ]
    }


# ============= Quiz Agent Endpoints =============

@router.post("/quiz/start")
async def start_quiz_session(
    request: QuizStartRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Start a new quiz session with domain, purpose, and difficulty
    """
    session_key = f"{current_user.id}_{request.session_id}"
    
    response = quiz_agent.start_session(
        session_id=session_key,
        domain=request.domain,
        purpose=request.purpose,
        difficulty=request.difficulty
    )
    
    return AgentResponse(
        agent="Question Answering System",
        response=response
    )


@router.post("/quiz/stream")
async def quiz_message_stream(
    request: QuizMessageRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Process quiz message with streaming response
    """
    session_key = f"{current_user.id}_{request.session_id}"
    
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in quiz_agent.process_message_stream(
                message=request.message,
                session_id=session_key
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/quiz/message")
async def quiz_message(
    request: QuizMessageRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Process a quiz message (non-streaming)
    """
    session_key = f"{current_user.id}_{request.session_id}"
    
    response = await quiz_agent.process_message(
        message=request.message,
        session_id=session_key
    )
    
    return AgentResponse(
        agent="Question Answering System",
        response=response
    )


@router.get("/quiz/score/{session_id}")
async def get_quiz_score(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get current quiz score and progress
    """
    session_key = f"{current_user.id}_{session_id}"
    return {"score": quiz_agent.get_score(session_key)}


@router.delete("/quiz/session/{session_id}")
async def end_quiz_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    End quiz session and get final results
    """
    session_key = f"{current_user.id}_{session_id}"
    result = quiz_agent.end_session(session_key)
    return {"result": result}


@router.delete("/resources/history/{session_id}")
async def clear_resources_history(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Clear conversation history for resources agent session
    """
    session_key = f"{current_user.id}_{session_id}"
    resources_agent.clear_session_history(session_key)
    return {"message": "Session history cleared", "session_id": session_id}


# ============= Summarizer RAG Document Upload Endpoints =============

@router.post("/qa/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = "default",
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a document for RAG-based Summarizer
    Supported formats: PDF, DOCX, TXT, MD, PY, JS, JSON, CSV
    """
    # Validate file extension
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Process document
    session_key = f"{current_user.id}_{session_id}"
    result = await summarizer_agent.upload_document(content, file.filename, session_key)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to process document"))
    
    return {
        "message": "Document uploaded successfully",
        "filename": result["filename"],
        "chunks": result["chunks"],
        "characters": result["characters"]
    }


@router.get("/qa/documents/{session_id}")
async def get_uploaded_documents(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of uploaded documents for a session
    """
    session_key = f"{current_user.id}_{session_id}"
    documents = summarizer_agent.get_uploaded_documents(session_key)
    
    # Extract just filenames from document IDs
    filenames = [doc.split("_", 1)[1] if "_" in doc else doc for doc in documents]
    
    return {
        "session_id": session_id,
        "documents": filenames,
        "count": len(documents)
    }


@router.delete("/qa/session/{session_id}")
async def clear_qa_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Clear Summarizer session including documents and conversation history
    """
    session_key = f"{current_user.id}_{session_id}"
    summarizer_agent.clear_session(session_key)
    return {"message": "Summarizer session cleared", "session_id": session_id}


# ============= Math Problem Solver Endpoints =============

@router.post("/math/solve/stream")
async def solve_math_problem_stream(
    request: MathProblemRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Solve a math problem with Chain of Thought reasoning (streaming response)
    """
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in math_solver_agent.solve_stream(request.problem):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/math/solve", response_model=AgentResponse)
async def solve_math_problem(
    request: MathProblemRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Solve a math problem with Chain of Thought reasoning (non-streaming)
    """
    try:
        response = await math_solver_agent.solve(request.problem)
        return AgentResponse(
            agent="Math Problem Solver",
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error solving math problem: {str(e)}")


# Allowed image types for math problem upload
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/math/upload-image")
async def upload_math_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload an image of a math problem and return base64 encoded string
    """
    import os
    import base64
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Validate it's a valid image
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(content))
        img.verify()
        
        # Convert to base64
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        return {
            "success": True,
            "image_base64": image_base64,
            "message": "Image uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


@router.post("/math/solve-image/stream")
async def solve_math_image_stream(
    file: UploadFile = File(...),
    session_id: str = "default",
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload an image of a math problem and solve it using vision model with streaming response.
    Uses base64 encoding to send the image directly to the LLM.
    """
    import os
    import base64
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Validate it's a valid image
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(content))
        img.verify()
        
        # Convert to base64
        image_base64 = base64.b64encode(content).decode('utf-8')
        
    except Exception as e:
        async def error_generator():
            yield f"data: {json.dumps({'error': f'Invalid image file: {str(e)}'})}\n\n"
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )
    
    session_key = f"{current_user.id}_{session_id}"
    
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            # Send acknowledgment that image was received
            yield f"data: {json.dumps({'chunk': '📷 **Analyzing image...**\\n\\n'})}\n\n"
            
            # Solve the problem from the image using base64
            async for chunk in math_solver_agent.solve_from_image_stream(image_base64, session_key):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============= Job Search Agent Endpoints =============

@router.post("/jobs/search/stream")
async def search_jobs_stream(
    request: JobSearchRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Search for jobs with streaming response using Tavily
    """
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in job_search_agent.search_stream(
                query=request.query,
                location=request.location or ""
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/jobs/search", response_model=AgentResponse)
async def search_jobs(
    request: JobSearchRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Search for jobs using Tavily (non-streaming)
    """
    try:
        response = await job_search_agent.search_and_format(
            query=request.query,
            location=request.location or ""
        )
        return AgentResponse(
            agent="Job Search",
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")
