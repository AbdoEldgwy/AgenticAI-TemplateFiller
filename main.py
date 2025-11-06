from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# import uvicorn

# Local imports
from ConversationBuilder import CnvBuilder
from Agentai import askAI, clear_conversation_history
# Initialize & Setup 
app = FastAPI(title="AI Template Assistant")
templates = Jinja2Templates(directory="templateweb")
cnv = CnvBuilder()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Allows all origins for deployment
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# ================================
# Routes
# ================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    main page - displays the chatbot interface
    """
    history = cnv.get_past_conversation()
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "history": history,
            "answer": None
        }
    )

@app.post("/")
async def chat(request: Request, question: str = Form(...)):
    """
    to send a question to the chatbot and get the answer
    Args:
        user question 
    """
    answer = askAI(question)

    history = cnv.get_past_conversation()
    
    return RedirectResponse(url="/", status_code=303)

 
@app.get("/services")
async def get_services():

    from tools import get_services
    return get_services()

@app.post("/clear")
async def clear_history():

    clear_conversation_history()
    return {
        "status": "success",
        "message": "Deleted successfully"
    }


# ================================
# Error Handlers
# ================================

# @app.exception_handler(404)
# async def not_found_handler(request: Request, exc):
#     """Error 404"""
#     return templates.TemplateResponse(
#         "404.html",
#         {"request": request},
#         status_code=404
#     )


# @app.exception_handler(500)
# async def server_error_handler(request: Request, exc):
#     """معالج 500"""
#     return {
#         "status": "error",
#         "message": "حدث خطأ في الخادم",
#         "detail": str(exc)
#     }


# ================================
# Startup/Shutdown Events
# ================================

@app.on_event("startup")
async def startup_event():
    """عند بدء التشغيل"""
    print("🚀 AI Assistant Server Started")
    print("📊 Loading conversation history...")
    history = cnv.get_past_conversation()
    print(f"✅ Loaded {len(history)} messages")

