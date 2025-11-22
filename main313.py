# import os
# import uuid
# import time
# import logging
# import asyncio
# import random
# import string
# import base64
# import json
# import subprocess
# import platform
# from datetime import datetime, timedelta
# from typing import Optional, List, Dict
# from pathlib import Path
# from io import BytesIO
# from concurrent.futures import ThreadPoolExecutor

# import psutil
# import httpx
# import uvicorn
# from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# from pydantic import BaseModel
# from PIL import Image as PILImage
# from captcha.image import ImageCaptcha
# import pywhatkit as kit
# from googleapiclient.discovery import build
# from groq import Groq
# import bcrypt
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import webbrowser

# from dotenv import load_dotenv

# load_dotenv()
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("JarvisAI-v10")

# # === CONFIG ===
# CONFIG = {
#     "groq_key": os.getenv("GroqAPIKey", ""),
#     "hf_key": os.getenv("HuggingFaceAPIKey", ""),
#     "google_api": os.getenv("GoogleAPIKey", ""),
#     "google_cx": os.getenv("GoogleCX", ""),
#     "xai_key": os.getenv("XAI_API_KEY", ""),
#     "assistant_name": "Jarvis",
#     "creator": "AmmiAbbu",
#     "admin_email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
#     "email_user": os.getenv("EMAIL_USER", ""),
#     "email_pass": os.getenv("EMAIL_PASS", ""),
#     "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
#     "smtp_port": int(os.getenv("SMTP_PORT", "587")),
# }

# HF_MODEL = "black-forest-labs/FLUX.1-schnell"
# executor = ThreadPoolExecutor(max_workers=15)

# # === IN-MEMORY DB ===
# users = {}
# sessions = {}
# captchas = {}
# reset_codes = {}
# conversation_history = {}
# task_queue = {}

# # === PYDANTIC MODELS ===
# class ChatRequest(BaseModel):
#     text: str
#     user: str
#     session_id: str

# class RegisterModel(BaseModel):
#     username: str
#     password: str
#     captcha: str
#     captcha_id: str

# class LoginModel(BaseModel):
#     username: str
#     password: str
#     captcha: str
#     captcha_id: str

# # === SYSTEM CONTROLLER ===
# class SystemController:
#     @staticmethod
#     def get_system_info() -> Dict:
#         return {
#             "cpu": {"percent": psutil.cpu_percent(interval=1), "cores": psutil.cpu_count()},
#             "memory": {
#                 "percent": psutil.virtual_memory().percent,
#                 "total": psutil.virtual_memory().total / (1024**3),
#                 "used": psutil.virtual_memory().used / (1024**3)
#             },
#             "disk": {
#                 "percent": psutil.disk_usage('/').percent,
#                 "total": psutil.disk_usage('/').total / (1024**3),
#                 "used": psutil.disk_usage('/').used / (1024**3)
#             }
#         }
    
#     @staticmethod
#     def set_volume(level: int) -> Dict:
#         try:
#             system = platform.system()
#             if system == "Windows":
#                 subprocess.run(["nircmd.exe", "setsysvolume", str(int(level * 655.35))], check=False)
#             elif system == "Darwin":
#                 subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
#             else:
#                 subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"], check=False)
#             return {"success": True, "volume": level}
#         except Exception as e:
#             return {"success": False, "error": str(e)}
    
#     @staticmethod
#     def open_application(app_name: str) -> Dict:
#         try:
#             system = platform.system()
#             app_lower = app_name.lower()
            
#             if system == "Windows":
#                 apps = {
#                     "notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe",
#                     "chrome": "chrome.exe", "edge": "msedge.exe", "explorer": "explorer.exe",
#                     "cmd": "cmd.exe", "powershell": "powershell.exe", "word": "WINWORD.EXE",
#                     "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE"
#                 }
#                 if app_lower in apps:
#                     subprocess.Popen([apps[app_lower]], shell=True)
#                     return {"success": True, "app": app_name}
#             elif system == "Darwin":
#                 subprocess.Popen(["open", "-a", app_name])
#                 return {"success": True, "app": app_name}
#             else:
#                 subprocess.Popen([app_lower], shell=True)
#                 return {"success": True, "app": app_name}
            
#             return {"success": False, "error": "App not found"}
#         except Exception as e:
#             return {"success": False, "error": str(e)}

# # === CODE DEBUGGER & PROBLEM SOLVER ===
# class CodeDebugger:
#     def __init__(self):
#         self.groq = Groq(api_key=CONFIG["groq_key"]) if CONFIG["groq_key"] else None
    
#     async def debug_code(self, code: str, language: str) -> Dict:
#         if not self.groq:
#             return {"error": "Groq API not configured"}
        
#         try:
#             prompt = f"""You are an expert {language} debugger. Analyze this code and provide:
# 1. Syntax errors
# 2. Logic errors
# 3. Best practices violations
# 4. Performance issues
# 5. Corrected code with explanation

# Code:
# ```{language}
# {code}
# ```

# Provide detailed analysis and corrected code."""

#             response = self.groq.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=2000,
#                 temperature=0.3
#             )
            
#             return {"success": True, "analysis": response.choices[0].message.content}
#         except Exception as e:
#             return {"error": str(e)}
    
#     async def solve_math_problem(self, problem: str, subject: str = "general", language: str = "en") -> Dict:
#         if not self.groq:
#             return {"error": "Groq API not configured"}
        
#         try:
#             prompt = f"""You are an expert mathematics tutor specializing in {subject}. 
# Solve this problem step-by-step with detailed explanation in {language}:

# {problem}

# Provide:
# 1. Step-by-step solution
# 2. Key concepts used
# 3. Final answer
# 4. Alternative methods (if applicable)
# 5. Real-world application"""

#             response = self.groq.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=3000,
#                 temperature=0.5
#             )
            
#             return {"success": True, "solution": response.choices[0].message.content}
#         except Exception as e:
#             return {"error": str(e)}
    
#     async def solve_physics_problem(self, problem: str) -> Dict:
#         if not self.groq:
#             return {"error": "Groq API not configured"}
        
#         try:
#             prompt = f"""You are an expert physics teacher. Solve this physics problem with:
# 1. Given data identification
# 2. Relevant formulas
# 3. Step-by-step calculation
# 4. Final answer with units
# 5. Physical interpretation

# Problem: {problem}"""

#             response = self.groq.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=2500,
#                 temperature=0.4
#             )
            
#             return {"success": True, "solution": response.choices[0].message.content}
#         except Exception as e:
#             return {"error": str(e)}
    
#     async def solve_chemistry_problem(self, problem: str) -> Dict:
#         if not self.groq:
#             return {"error": "Groq API not configured"}
        
#         try:
#             prompt = f"""You are an expert chemistry teacher. Solve this chemistry problem:
# 1. Chemical equations (if needed)
# 2. Molar calculations
# 3. Stoichiometry
# 4. Step-by-step solution
# 5. Key concepts

# Problem: {problem}"""

#             response = self.groq.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=2500,
#                 temperature=0.4
#             )
            
#             return {"success": True, "solution": response.choices[0].message.content}
#         except Exception as e:
#             return {"error": str(e)}

# # === AUTOMATION SERVICE ===
# class AutomationService:
#     def __init__(self):
#         self.system = SystemController()
#         self.websites = {
#             "facebook": "https://facebook.com", "instagram": "https://instagram.com",
#             "twitter": "https://twitter.com", "x": "https://twitter.com",
#             "gmail": "https://mail.google.com", "youtube": "https://youtube.com",
#             "linkedin": "https://linkedin.com", "reddit": "https://reddit.com",
#             "github": "https://github.com", "stackoverflow": "https://stackoverflow.com",
#             "medium": "https://medium.com", "netflix": "https://netflix.com",
#             "amazon": "https://amazon.com", "whatsapp": "https://web.whatsapp.com",
#             "telegram": "https://web.telegram.org", "discord": "https://discord.com",
#             "spotify": "https://spotify.com", "spacex": "https://spacex.com",
#             "nasa": "https://nasa.gov", "google": "https://google.com",
#         }
    
#     async def execute_task(self, task: str) -> Dict:
#         try:
#             task_lower = task.lower().strip()
            
#             # Web navigation
#             for site_name, url in self.websites.items():
#                 if f"open {site_name}" in task_lower or site_name in task_lower:
#                     webbrowser.open(url)
#                     return {"name": f"Open {site_name.title()}", "status": "✓ Opened", "progress": 100}
            
#             # YouTube playback
#             if "play" in task_lower and "youtube" in task_lower:
#                 parts = task_lower.split("play")
#                 if len(parts) > 1:
#                     song = parts[1].replace("on youtube", "").replace("youtube", "").strip()
#                     if song:
#                         kit.playonyt(song)
#                         return {"name": f"Play '{song}'", "status": "▶ Playing", "progress": 100}
            
#             # System applications
#             if "open" in task_lower:
#                 apps = ["notepad", "calculator", "paint", "cmd", "powershell"]
#                 for app in apps:
#                     if app in task_lower:
#                         result = self.system.open_application(app)
#                         return {"name": f"Open {app.title()}", "status": "✓ Opened" if result["success"] else "✗ Failed", "progress": 100 if result["success"] else 0}
            
#             # Volume control
#             if "volume up" in task_lower:
#                 self.system.set_volume(80)
#                 return {"name": "Volume Up", "status": "✓ Set to 80%", "progress": 100}
#             elif "volume down" in task_lower:
#                 self.system.set_volume(30)
#                 return {"name": "Volume Down", "status": "✓ Set to 30%", "progress": 100}
#             elif "mute" in task_lower:
#                 self.system.set_volume(0)
#                 return {"name": "Mute", "status": "✓ Muted", "progress": 100}
            
#             # Letter writing
#             if "write letter" in task_lower or "letter to" in task_lower:
#                 recipient = task_lower.split("to")[-1].strip() if "to" in task_lower else "Recipient"
#                 return {"name": f"Write Letter to {recipient}", "status": "✓ Opened Notepad", "progress": 100}
            
#             return {"name": task, "status": "⚠ Unknown command", "progress": 0}
                
#         except Exception as e:
#             logger.error(f"Automation error: {e}")
#             return {"name": task, "status": f"✗ Error: {str(e)}", "progress": 0}

# # === SEARCH SERVICE ===
# class SearchService:
#     def __init__(self):
#         self.google = None
#         self.groq = None
        
#         if CONFIG["google_api"] and CONFIG["google_cx"]:
#             try:
#                 self.google = build("customsearch", "v1", developerKey=CONFIG["google_api"])
#             except Exception as e:
#                 logger.error(f"Google Search init error: {e}")
        
#         if CONFIG["groq_key"]:
#             try:
#                 self.groq = Groq(api_key=CONFIG["groq_key"])
#             except Exception as e:
#                 logger.error(f"Groq init error: {e}")
    
#     async def realtime_search(self, query: str) -> str:
#         results = []
        
#         # Google Custom Search
#         if self.google:
#             try:
#                 res = self.google.cse().list(q=query, cx=CONFIG["google_cx"], num=5).execute()
#                 items = res.get('items', [])
#                 if items:
#                     results.append("📊 **Google Search Results:**\n")
#                     for idx, item in enumerate(items[:5], 1):
#                         title = item.get('title', 'No title')
#                         snippet = item.get('snippet', 'No description')
#                         link = item.get('link', '')
#                         results.append(f"{idx}. **{title}**\n   {snippet}\n   🔗 {link}\n")
#             except Exception as e:
#                 logger.error(f"Google search error: {e}")
        
#         # Groq AI Analysis
#         if self.groq:
#             try:
#                 completion = self.groq.chat.completions.create(
#                     model="llama-3.3-70b-versatile",
#                     messages=[{
#                         "role": "user",
#                         "content": f"Provide real-time analysis about: {query}. Be specific and current."
#                     }],
#                     max_tokens=1000
#                 )
#                 grok_result = completion.choices[0].message.content
#                 results.append(f"\n🤖 **AI Analysis:**\n{grok_result}\n")
#             except Exception as e:
#                 logger.error(f"Groq analysis error: {e}")
        
#         if not results:
#             return "❌ No search engines configured."
        
#         return "\n".join(results)

# # === IMAGE GENERATION ===
# class HFImageService:
#     def __init__(self):
#         self.token = CONFIG["hf_key"]
#         if not self.token:
#             raise ValueError("HuggingFaceAPIKey not set")
    
#     async def generate_image(self, prompt: str) -> str:
#         try:
#             async with httpx.AsyncClient(timeout=120.0) as client:
#                 response = await client.post(
#                     f"https://api-inference.huggingface.co/models/{HF_MODEL}",
#                     headers={"Authorization": f"Bearer {self.token}"},
#                     json={"inputs": prompt}
#                 )
                
#                 if response.status_code != 200:
#                     error = response.json().get("error", response.text)
#                     raise Exception(f"HF API Error: {error}")
                
#                 return base64.b64encode(response.content).decode("utf-8")
#         except Exception as e:
#             logger.error(f"Image generation error: {e}")
#             raise

# # === CHAT SERVICE ===
# class ChatService:
#     def __init__(self):
#         self.groq = Groq(api_key=CONFIG["groq_key"]) if CONFIG["groq_key"] else None
#         self.hf = HFImageService() if CONFIG["hf_key"] else None
#         self.automation = AutomationService()
#         self.search = SearchService()
#         self.debugger = CodeDebugger()
    
#     async def chat(self, query: str, user: str, session_id: str, lang: str = "en") -> Dict:
#         if session_id not in conversation_history:
#             conversation_history[session_id] = []
        
#         # Automation
#         if query.lower().startswith("automate:"):
#             tasks = [t.strip() for t in query.split(":", 1)[1].split(",") if t.strip()]
#             if not tasks:
#                 return {"response": "⚠ No tasks specified."}
            
#             task_results = await asyncio.gather(*[self.automation.execute_task(t) for t in tasks[:15]])
#             return {
#                 "response": f"✓ Executed {len(task_results)} task(s).",
#                 "tasks": task_results,
#                 "session_id": session_id
#             }
        
#         # Real-time Search
#         if query.lower().startswith("search:") or query.lower().startswith("realtime search:"):
#             q = query.split(":", 1)[1].strip()
#             if not q:
#                 return {"response": "⚠ Please specify a search query."}
            
#             res = await self.search.realtime_search(q)
#             return {"response": res, "session_id": session_id}
        
#         # Code Debugging
#         if query.lower().startswith("debug code:"):
#             parts = query.split(":", 2)
#             if len(parts) < 3:
#                 return {"response": "⚠ Format: 'debug code: language: code'"}
            
#             language = parts[1].strip()
#             code = parts[2].strip()
#             result = await self.debugger.debug_code(code, language)
            
#             if "error" in result:
#                 return {"response": f"❌ Debug error: {result['error']}", "session_id": session_id}
            
#             return {"response": result["analysis"], "session_id": session_id}
        
#         # Math Problem Solving
#         if query.lower().startswith("solve math:"):
#             problem = query.split(":", 1)[1].strip()
#             result = await self.debugger.solve_math_problem(problem, "general", lang)
            
#             if "error" in result:
#                 return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
#             return {"response": result["solution"], "session_id": session_id}
        
#         # Physics Problem Solving
#         if query.lower().startswith("solve physics:"):
#             problem = query.split(":", 1)[1].strip()
#             result = await self.debugger.solve_physics_problem(problem)
            
#             if "error" in result:
#                 return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
#             return {"response": result["solution"], "session_id": session_id}
        
#         # Chemistry Problem Solving
#         if query.lower().startswith("solve chemistry:"):
#             problem = query.split(":", 1)[1].strip()
#             result = await self.debugger.solve_chemistry_problem(problem)
            
#             if "error" in result:
#                 return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
#             return {"response": result["solution"], "session_id": session_id}
        
#         # Image Generation
#         if query.lower().startswith("generate image"):
#             if not self.hf:
#                 return {"response": "❌ Image generation not configured.", "error": True}
            
#             prompt = query.replace("generate image", "").strip()
#             if not prompt:
#                 return {"response": "⚠ Please describe the image."}
            
#             try:
#                 img_b64 = await self.hf.generate_image(prompt)
#                 return {
#                     "image": f"data:image/png;base64,{img_b64}",
#                     "response": f"✓ Generated: {prompt}",
#                     "session_id": session_id
#                 }
#             except Exception as e:
#                 return {"response": f"❌ Image generation failed: {str(e)}", "error": True}
        
#         # Meme Generation
#         if query.lower().startswith("generate meme"):
#             if not self.hf:
#                 return {"response": "❌ Meme generation not configured.", "error": True}
            
#             try:
#                 meme_text = query.replace("generate meme", "").strip()
#                 prompt = f"Create a funny internet meme. {meme_text}. Bold white text, Impact font, black outline."
                
#                 img_b64 = await self.hf.generate_image(prompt)
#                 return {
#                     "meme": f"data:image/png;base64,{img_b64}",
#                     "response": "✓ Meme generated!",
#                     "session_id": session_id
#                 }
#             except Exception as e:
#                 return {"response": f"❌ Meme generation failed: {str(e)}", "error": True}
        
#         # Regular Chat
#         conversation_history[session_id].append({"role": "user", "content": query})
        
#         if len(conversation_history[session_id]) > 20:
#             conversation_history[session_id] = conversation_history[session_id][-20:]
        
#         system_prompt = f"""You are {CONFIG['assistant_name']}, an advanced AI assistant created by {CONFIG['creator']}. 
# You are helpful, friendly, and knowledgeable. Respond in {lang}. You can solve complex problems,
# debug code, generate images, search the web, and automate tasks. Always be accurate and provide detailed explanations."""

#         messages = [{"role": "system", "content": system_prompt}] + conversation_history[session_id][-10:]
        
#         if self.groq:
#             try:
#                 response = self.groq.chat.completions.create(
#                     model="llama-3.3-70b-versatile",
#                     messages=messages,
#                     max_tokens=2000,
#                     temperature=0.7
#                 )
                
#                 result = response.choices[0].message.content.strip()
#                 conversation_history[session_id].append({"role": "assistant", "content": result})
                
#                 return {"response": result, "session_id": session_id}
#             except Exception as e:
#                 logger.error(f"Chat error: {e}")
#                 return {"response": f"❌ Chat error: {str(e)}", "error": True}
        
#         return {"response": "❌ Chat service not configured.", "error": True}

# # Initialize services
# chat_service = ChatService()

# # === FASTAPI APP ===
# app = FastAPI(title="Jarvis AI v10.0", version="10.0")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_credentials=True
# )

# @app.get("/")
# async def root():
#     return {"message": "Jarvis AI v10.0 Online", "status": "active"}

# @app.get("/health")
# async def health():
#     system_info = SystemController.get_system_info()
#     return {
#         "status": "online",
#         "version": "10.0",
#         "timestamp": datetime.now().isoformat(),
#         "system": system_info,
#         "features": {
#             "chat": bool(CONFIG["groq_key"]),
#             "search": bool(CONFIG["google_api"]),
#             "images": bool(CONFIG["hf_key"]),
#             "automation": True,
#             "code_debugger": True,
#             "math_solver": True,
#             "physics_solver": True,
#             "chemistry_solver": True
#         }
#     }

# @app.get("/captcha")
# async def get_captcha():
#     captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     image = ImageCaptcha(width=280, height=90)
#     data = image.generate(captcha_text)
#     img_b64 = base64.b64encode(data.getvalue()).decode()
#     captcha_id = str(uuid.uuid4())
#     captchas[captcha_id] = captcha_text
    
#     if len(captchas) > 1000:
#         old_keys = list(captchas.keys())[:-500]
#         for key in old_keys:
#             del captchas[key]
    
#     return {"image": img_b64, "id": captcha_id}

# @app.post("/register")
# async def register(model: RegisterModel):
#     if model.captcha_id not in captchas:
#         return {"success": False, "message": "❌ Captcha expired."}
    
#     if model.captcha.upper() != captchas[model.captcha_id]:
#         return {"success": False, "message": "❌ Invalid captcha."}
    
#     if model.username in users:
#         return {"success": False, "message": "❌ Username exists."}
    
#     if len(model.password) < 6:
#         return {"success": False, "message": "❌ Password must be 6+ chars."}
    
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(model.password.encode('utf-8'), salt)
#     users[model.username] = {
#         "password_hash": hashed,
#         "created_at": datetime.now().isoformat()
#     }
    
#     del captchas[model.captcha_id]
#     logger.info(f"User registered: {model.username}")
    
#     return {"success": True, "message": "✓ Registration successful!"}

# @app.post("/login")
# async def login_endpoint(model: LoginModel):
#     if model.captcha_id not in captchas:
#         return {"success": False, "message": "❌ Captcha expired."}
    
#     if model.captcha.upper() != captchas[model.captcha_id]:
#         return {"success": False, "message": "❌ Invalid captcha."}
    
#     if model.username not in users:
#         return {"success": False, "message": "❌ Invalid credentials."}
    
#     user = users[model.username]
#     if not bcrypt.checkpw(model.password.encode('utf-8'), user["password_hash"]):
#         return {"success": False, "message": "❌ Invalid credentials."}
    
#     session_id = str(uuid.uuid4())
#     sessions[session_id] = {
#         "username": model.username,
#         "created_at": datetime.now().isoformat()
#     }
    
#     del captchas[model.captcha_id]
#     logger.info(f"User logged in: {model.username}")
    
#     return {
#         "success": True,
#         "message": "✓ Login successful!",
#         "session_id": session_id
#     }

# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     if request.session_id not in sessions:
#         return {"response": "❌ Invalid session.", "error": True}
    
#     result = await chat_service.chat(
#         request.text,
#         request.user,
#         request.session_id
#     )
    
#     return result

# @app.post("/logout")
# async def logout_endpoint(session_id: str):
#     if session_id in sessions:
#         del sessions[session_id]
#         if session_id in conversation_history:
#             del conversation_history[session_id]
#     return {"success": True, "message": "✓ Logged out."}

# @app.get("/system-info")
# async def system_info():
#     return SystemController.get_system_info()

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)






import os
import uuid
import time
import logging
import asyncio
import random
import string
import base64
import json
import subprocess
import platform
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

import psutil
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image as PILImage, ImageDraw, ImageFont
from captcha.image import ImageCaptcha
import pywhatkit as kit
from googleapiclient.discovery import build
from groq import Groq
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("JarvisAI-v10")

# === CONFIG ===
CONFIG = {
    "groq_key": os.getenv("GroqAPIKey", ""),
    "grok_key": os.getenv("GrokAPIKey", ""),
    "hf_key": os.getenv("HuggingFaceAPIKey", ""),
    "google_api": os.getenv("GoogleAPIKey", ""),
    "google_cx": os.getenv("GoogleCX", ""),
    "assistant_name": "Jarvis",
    "creator": "AmmiAbbu",
    "admin_email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
    "email_user": os.getenv("EMAIL_USER", ""),
    "email_pass": os.getenv("EMAIL_PASS", ""),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
}

HF_MODEL = "black-forest-labs/FLUX.1-schnell"
executor = ThreadPoolExecutor(max_workers=15)

# === IN-MEMORY DB ===
users = {}
sessions = {}
captchas = {}
reset_codes = {}
conversation_history = {}
task_queue = {}

# === PYDANTIC MODELS ===
class ChatRequest(BaseModel):
    text: str
    user: str
    session_id: str

class RegisterModel(BaseModel):
    username: str
    password: str
    captcha: str
    captcha_id: str

class LoginModel(BaseModel):
    username: str
    password: str
    captcha: str
    captcha_id: str

# === SYSTEM CONTROLLER ===
class SystemController:
    @staticmethod
    def get_system_info() -> Dict:
        return {
            "cpu": {"percent": psutil.cpu_percent(interval=1), "cores": psutil.cpu_count()},
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "total": psutil.virtual_memory().total / (1024**3),
                "used": psutil.virtual_memory().used / (1024**3)
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent,
                "total": psutil.disk_usage('/').total / (1024**3),
                "used": psutil.disk_usage('/').used / (1024**3)
            }
        }
    
    @staticmethod
    def set_volume(level: int) -> Dict:
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["nircmd.exe", "setsysvolume", str(int(level * 655.35))], check=False)
            elif system == "Darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
            else:
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"], check=False)
            return {"success": True, "volume": level}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def open_application(app_name: str) -> Dict:
        try:
            system = platform.system()
            app_lower = app_name.lower()
            
            if system == "Windows":
                apps = {
                    "notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe",
                    "chrome": "chrome.exe", "edge": "msedge.exe", "explorer": "explorer.exe",
                    "cmd": "cmd.exe", "powershell": "powershell.exe", "word": "WINWORD.EXE",
                    "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE"
                }
                if app_lower in apps:
                    subprocess.Popen([apps[app_lower]], shell=True)
                    return {"success": True, "app": app_name}
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
                return {"success": True, "app": app_name}
            else:
                subprocess.Popen([app_lower], shell=True)
                return {"success": True, "app": app_name}
            
            return {"success": False, "error": "App not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# === CODE DEBUGGER & PROBLEM SOLVER ===
class CodeDebugger:
    def __init__(self):
        self.groq = Groq(api_key=CONFIG["groq_key"]) if CONFIG["groq_key"] else None
    
    async def debug_code(self, code: str, language: str) -> Dict:
        if not self.groq:
            return {"error": "Groq API not configured"}
        
        try:
            prompt = f"""You are an expert {language} debugger. Analyze this code and provide:
1. Syntax errors
2. Logic errors
3. Best practices violations
4. Performance issues
5. Corrected code with explanation

Code:
```{language}
{code}
```

Provide detailed analysis and corrected code."""

            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            return {"success": True, "analysis": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
    
    async def solve_math_problem(self, problem: str, subject: str = "general", language: str = "en") -> Dict:
        if not self.groq:
            return {"error": "Groq API not configured"}
        
        try:
            prompt = f"""You are an expert mathematics tutor specializing in {subject}. 
Solve this problem step-by-step with detailed explanation in {language}:

{problem}

Provide:
1. Step-by-step solution
2. Key concepts used
3. Final answer
4. Alternative methods (if applicable)
5. Real-world application"""

            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.5
            )
            
            return {"success": True, "solution": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
    
    async def solve_physics_problem(self, problem: str) -> Dict:
        if not self.groq:
            return {"error": "Groq API not configured"}
        
        try:
            prompt = f"""You are an expert physics teacher. Solve this physics problem with:
1. Given data identification
2. Relevant formulas
3. Step-by-step calculation
4. Final answer with units
5. Physical interpretation

Problem: {problem}"""

            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.4
            )
            
            return {"success": True, "solution": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
    
    async def solve_chemistry_problem(self, problem: str) -> Dict:
        if not self.groq:
            return {"error": "Groq API not configured"}
        
        try:
            prompt = f"""You are an expert chemistry teacher. Solve this chemistry problem:
1. Chemical equations (if needed)
2. Molar calculations
3. Stoichiometry
4. Step-by-step solution
5. Key concepts

Problem: {problem}"""

            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.4
            )
            
            return {"success": True, "solution": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}

# === GROK AI (XAI) SERVICE ===
class GrokAIService:
    def __init__(self):
        self.api_key = CONFIG["grok_key"]
        if not self.api_key:
            logger.warning("Grok API key not configured")
    
    async def grok_search(self, query: str) -> str:
        """Real-time search with Grok AI"""
        if not self.api_key:
            return "❌ Grok API not configured"
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="grok-2-vision-1212",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": f"Provide real-time, current information about: {query}. Be specific, detailed and current."
                }]
            )
            
            return response.content[0].text if response.content else "No response"
        except Exception as e:
            logger.error(f"Grok search error: {e}")
            return f"⚠ Grok error: {str(e)}"
    
    async def grok_analyze(self, topic: str, depth: str = "detailed") -> str:
        """Deep analysis with Grok AI"""
        if not self.api_key:
            return "❌ Grok API not configured"
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            prompt = f"Provide a {depth} analysis of: {topic}. Include key points, implications, and current relevance."
            
            response = client.messages.create(
                model="grok-2-vision-1212",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text if response.content else "No response"
        except Exception as e:
            logger.error(f"Grok analysis error: {e}")
            return f"⚠ Grok error: {str(e)}"

# === AUTOMATION SERVICE ===
class AutomationService:
    def __init__(self):
        self.system = SystemController()
        self.websites = {
            "facebook": "https://facebook.com", "instagram": "https://instagram.com",
            "twitter": "https://twitter.com", "x": "https://twitter.com",
            "gmail": "https://mail.google.com", "youtube": "https://youtube.com",
            "linkedin": "https://linkedin.com", "reddit": "https://reddit.com",
            "github": "https://github.com", "stackoverflow": "https://stackoverflow.com",
            "medium": "https://medium.com", "netflix": "https://netflix.com",
            "amazon": "https://amazon.com", "whatsapp": "https://web.whatsapp.com",
            "telegram": "https://web.telegram.org", "discord": "https://discord.com",
            "spotify": "https://spotify.com", "spacex": "https://spacex.com",
            "nasa": "https://nasa.gov", "google": "https://google.com",
        }
    
    async def execute_task(self, task: str) -> Dict:
        try:
            task_lower = task.lower().strip()
            
            # Web navigation
            for site_name, url in self.websites.items():
                if f"open {site_name}" in task_lower or site_name in task_lower:
                    webbrowser.open(url)
                    return {"name": f"Open {site_name.title()}", "status": "✓ Opened", "progress": 100}
            
            # YouTube playback
            if "play" in task_lower and "youtube" in task_lower:
                parts = task_lower.split("play")
                if len(parts) > 1:
                    song = parts[1].replace("on youtube", "").replace("youtube", "").strip()
                    if song:
                        kit.playonyt(song)
                        return {"name": f"Play '{song}'", "status": "▶ Playing", "progress": 100}
            
            # System applications
            if "open" in task_lower:
                apps = ["notepad", "calculator", "paint", "cmd", "powershell"]
                for app in apps:
                    if app in task_lower:
                        result = self.system.open_application(app)
                        return {"name": f"Open {app.title()}", "status": "✓ Opened" if result["success"] else "✗ Failed", "progress": 100 if result["success"] else 0}
            
            # Volume control
            if "volume up" in task_lower:
                self.system.set_volume(80)
                return {"name": "Volume Up", "status": "✓ Set to 80%", "progress": 100}
            elif "volume down" in task_lower:
                self.system.set_volume(30)
                return {"name": "Volume Down", "status": "✓ Set to 30%", "progress": 100}
            elif "mute" in task_lower:
                self.system.set_volume(0)
                return {"name": "Mute", "status": "✓ Muted", "progress": 100}
            
            return {"name": task, "status": "⚠ Unknown command", "progress": 0}
                
        except Exception as e:
            logger.error(f"Automation error: {e}")
            return {"name": task, "status": f"✗ Error: {str(e)}", "progress": 0}

# === SEARCH SERVICE ===
class SearchService:
    def __init__(self):
        self.google = None
        self.grok = GrokAIService()
        
        if CONFIG["google_api"] and CONFIG["google_cx"]:
            try:
                self.google = build("customsearch", "v1", developerKey=CONFIG["google_api"])
            except Exception as e:
                logger.error(f"Google Search init error: {e}")
    
    async def realtime_search(self, query: str) -> str:
        results = []
        
        # Google Custom Search
        if self.google:
            try:
                res = self.google.cse().list(q=query, cx=CONFIG["google_cx"], num=5).execute()
                items = res.get('items', [])
                if items:
                    results.append("📊 **Google Search Results:**\n")
                    for idx, item in enumerate(items[:5], 1):
                        title = item.get('title', 'No title')
                        snippet = item.get('snippet', 'No description')
                        link = item.get('link', '')
                        results.append(f"{idx}. **{title}**\n   {snippet}\n   🔗 {link}\n")
            except Exception as e:
                logger.error(f"Google search error: {e}")
        
        # Grok AI Real-time Search
        try:
            grok_result = await self.grok.grok_search(query)
            results.append(f"\n🤖 **Grok AI Real-Time Analysis:**\n{grok_result}\n")
        except Exception as e:
            logger.error(f"Grok search error: {e}")
        
        if not results:
            return "❌ No search engines configured."
        
        return "\n".join(results)
    
    async def grok_deep_search(self, query: str) -> str:
        """Use Grok AI for deep analysis"""
        try:
            result = await self.grok.grok_analyze(query, "detailed")
            return f"🧠 **Grok Deep Analysis:**\n{result}"
        except Exception as e:
            return f"⚠ Grok error: {str(e)}"

# === IMAGE & MEME GENERATION ===
class ImageService:
    def __init__(self):
        self.hf_token = CONFIG["hf_key"]
        if not self.hf_token:
            logger.warning("HuggingFace API key not configured")
    
    async def generate_image(self, prompt: str) -> str:
        """Generate high-quality images using HuggingFace FLUX"""
        if not self.hf_token:
            raise ValueError("HuggingFaceAPIKey not set")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                    headers={"Authorization": f"Bearer {self.hf_token}"},
                    json={"inputs": prompt}
                )
                
                if response.status_code != 200:
                    error = response.json().get("error", response.text)
                    raise Exception(f"HF API Error: {error}")
                
                return base64.b64encode(response.content).decode("utf-8")
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            raise
    
    def create_meme_locally(self, text_top: str, text_bottom: str, style: str = "classic") -> str:
        """Create memes locally with PIL"""
        try:
            # Create image
            width, height = 800, 600
            img = PILImage.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use Impact font, fallback to default
            try:
                font_size = 60
                font = ImageFont.truetype("arial.ttf", font_size)
                small_font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Add meme style backgrounds
            if style == "classic":
                # White background with black text and white outline
                draw.rectangle([0, 0, width, height], fill='white')
                
                # Top text
                self._draw_text_with_outline(draw, text_top.upper(), (width//2, 50), font, 'black', 'white', 3)
                # Bottom text
                self._draw_text_with_outline(draw, text_bottom.upper(), (width//2, height-100), font, 'black', 'white', 3)
            
            elif style == "dark":
                draw.rectangle([0, 0, width, height], fill='#1a1a1a')
                self._draw_text_with_outline(draw, text_top.upper(), (width//2, 50), font, '#00d4ff', '#0a0e27', 2)
                self._draw_text_with_outline(draw, text_bottom.upper(), (width//2, height-100), font, '#00d4ff', '#0a0e27', 2)
            
            elif style == "colorful":
                draw.rectangle([0, 0, width, height], fill='#FF6B6B')
                self._draw_text_with_outline(draw, text_top.upper(), (width//2, 50), font, 'white', '#FF6B6B', 3)
                self._draw_text_with_outline(draw, text_bottom.upper(), (width//2, height-100), font, 'white', '#FF6B6B', 3)
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode()
        
        except Exception as e:
            logger.error(f"Meme creation error: {e}")
            raise
    
    def _draw_text_with_outline(self, draw, text, position, font, fill_color, outline_color, outline_width):
        """Draw text with outline"""
        x, y = position
        # Draw outline
        for adj_x in range(-outline_width, outline_width+1):
            for adj_y in range(-outline_width, outline_width+1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x+adj_x, y+adj_y), text, font=font, fill=outline_color, anchor="mm")
        # Draw main text
        draw.text(position, text, font=font, fill=fill_color, anchor="mm")
    
    async def generate_ai_meme(self, description: str) -> str:
        """Generate memes using AI"""
        try:
            prompt = f"Create a funny, hilarious internet meme. {description}. Make it visually appealing with bold Impact font text, professional design, viral worthy. High quality, sharp, clear."
            img_b64 = await self.generate_image(prompt)
            return img_b64
        except Exception as e:
            logger.error(f"AI meme generation error: {e}")
            raise

# === CHAT SERVICE ===
class ChatService:
    def __init__(self):
        self.groq = Groq(api_key=CONFIG["groq_key"]) if CONFIG["groq_key"] else None
        self.image_service = ImageService() if CONFIG["hf_key"] else None
        self.automation = AutomationService()
        self.search = SearchService()
        self.debugger = CodeDebugger()
        self.grok = GrokAIService()
    
    async def chat(self, query: str, user: str, session_id: str, lang: str = "en") -> Dict:
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Automation
        if query.lower().startswith("automate:"):
            tasks = [t.strip() for t in query.split(":", 1)[1].split(",") if t.strip()]
            if not tasks:
                return {"response": "⚠ No tasks specified."}
            
            task_results = await asyncio.gather(*[self.automation.execute_task(t) for t in tasks[:15]])
            return {
                "response": f"✓ Executed {len(task_results)} task(s).",
                "tasks": task_results,
                "session_id": session_id
            }
        
        # Real-time Search with Google & Grok
        if query.lower().startswith("search:") or query.lower().startswith("realtime search:"):
            q = query.split(":", 1)[1].strip()
            if not q:
                return {"response": "⚠ Please specify a search query."}
            
            res = await self.search.realtime_search(q)
            return {"response": res, "session_id": session_id}
        
        # Grok Deep Search
        if query.lower().startswith("grok:") or query.lower().startswith("grok search:"):
            q = query.split(":", 1)[1].strip()
            if not q:
                return {"response": "⚠ Please specify a topic."}
            
            res = await self.search.grok_deep_search(q)
            return {"response": res, "session_id": session_id}
        
        # Code Debugging
        if query.lower().startswith("debug code:"):
            parts = query.split(":", 2)
            if len(parts) < 3:
                return {"response": "⚠ Format: 'debug code: language: code'"}
            
            language = parts[1].strip()
            code = parts[2].strip()
            result = await self.debugger.debug_code(code, language)
            
            if "error" in result:
                return {"response": f"❌ Debug error: {result['error']}", "session_id": session_id}
            
            return {"response": result["analysis"], "session_id": session_id}
        
        # Math Problem Solving
        if query.lower().startswith("solve math:"):
            problem = query.split(":", 1)[1].strip()
            result = await self.debugger.solve_math_problem(problem, "general", lang)
            
            if "error" in result:
                return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
            return {"response": result["solution"], "session_id": session_id}
        
        # Physics Problem Solving
        if query.lower().startswith("solve physics:"):
            problem = query.split(":", 1)[1].strip()
            result = await self.debugger.solve_physics_problem(problem)
            
            if "error" in result:
                return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
            return {"response": result["solution"], "session_id": session_id}
        
        # Chemistry Problem Solving
        if query.lower().startswith("solve chemistry:"):
            problem = query.split(":", 1)[1].strip()
            result = await self.debugger.solve_chemistry_problem(problem)
            
            if "error" in result:
                return {"response": f"❌ Error: {result['error']}", "session_id": session_id}
            
            return {"response": result["solution"], "session_id": session_id}
        
        # Image Generation with AI
        if query.lower().startswith("generate image"):
            if not self.image_service:
                return {"response": "❌ Image generation not configured.", "error": True}
            
            prompt = query.lower().replace("generate image", "").replace("of", "").strip()
            if not prompt:
                return {"response": "⚠ Please describe the image."}
            
            try:
                img_b64 = await self.image_service.generate_image(prompt)
                return {
                    "image": f"data:image/png;base64,{img_b64}",
                    "response": f"✓ Generated: {prompt}",
                    "session_id": session_id
                }
            except Exception as e:
                return {"response": f"❌ Image generation failed: {str(e)}", "error": True}
        
        # AI-Powered Meme Generation
        if query.lower().startswith("generate meme"):
            if not self.image_service:
                return {"response": "❌ Meme generation not configured.", "error": True}
            
            try:
                meme_desc = query.lower().replace("generate meme", "").strip()
                if not meme_desc:
                    meme_desc = "Funny relatable meme"
                
                img_b64 = await self.image_service.generate_ai_meme(meme_desc)
                return {
                    "meme": f"data:image/png;base64,{img_b64}",
                    "response": "✓ AI Meme generated!",
                    "session_id": session_id
                }
            except Exception as e:
                return {"response": f"❌ Meme generation failed: {str(e)}", "error": True}
        
        # Local Meme Creation (text-based)
        if query.lower().startswith("meme:"):
            if not self.image_service:
                return {"response": "❌ Meme generation not configured.", "error": True}
            
            try:
                parts = query.split(":", 2)
                top_text = parts[1].strip() if len(parts) > 1 else "Top Text"
                bottom_text = parts[2].strip() if len(parts) > 2 else "Bottom Text"
                
                img_b64 = self.image_service.create_meme_locally(top_text, bottom_text, "classic")
                return {
                    "meme": f"data:image/png;base64,{img_b64}",
                    "response": "✓ Meme created!",
                    "session_id": session_id
                }
            except Exception as e:
                return {"response": f"❌ Meme creation failed: {str(e)}", "error": True}
        
        # Regular Chat
        conversation_history[session_id].append({"role": "user", "content": query})
        
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        system_prompt = f"""You are {CONFIG['assistant_name']}, an advanced AI assistant created by {CONFIG['creator']}. 
You are helpful, friendly, and knowledgeable. Respond in {lang}. You can solve complex problems,
debug code, generate images and memes, search the web with Grok AI, and automate tasks. 
Always provide detailed, accurate explanations. You have access to real-time information through Grok AI."""

        messages = [{"role": "system", "content": system_prompt}] + conversation_history[session_id][-10:]
        
        if self.groq:
            try:
                response = self.groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                conversation_history[session_id].append({"role": "assistant", "content": result})
                
                return {"response": result, "session_id": session_id}
            except Exception as e:
                logger.error(f"Chat error: {e}")
                return {"response": f"❌ Chat error: {str(e)}", "error": True}
        
        return {"response": "❌ Chat service not configured.", "error": True}

# Initialize services
chat_service = ChatService()

# === FASTAPI APP ===
app = FastAPI(title="Jarvis AI v10.0", version="10.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.get("/")
async def root():
    return {"message": "Jarvis AI v10.0 Online", "status": "active"}

@app.get("/health")
async def health():
    system_info = SystemController.get_system_info()
    return {
        "status": "online",
        "version": "10.0",
        "timestamp": datetime.now().isoformat(),
        "system": system_info,
        "features": {
            "chat": bool(CONFIG["groq_key"]),
            "grok_ai": bool(CONFIG["grok_key"]),
            "google_search": bool(CONFIG["google_api"]),
            "image_generation": bool(CONFIG["hf_key"]),
            "meme_generation": True,
            "automation": True,
            "code_debugger": True,
            "math_solver": True,
            "physics_solver": True,
            "chemistry_solver": True
        }
    }

@app.get("/captcha")
async def get_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = ImageCaptcha(width=280, height=90)
    data = image.generate(captcha_text)
    img_b64 = base64.b64encode(data.getvalue()).decode()
    captcha_id = str(uuid.uuid4())
    captchas[captcha_id] = captcha_text
    
    if len(captchas) > 1000:
        old_keys = list(captchas.keys())[:-500]
        for key in old_keys:
            del captchas[key]
    
    return {"image": img_b64, "id": captcha_id}

@app.post("/register")
async def register(model: RegisterModel):
    if model.captcha_id not in captchas:
        return {"success": False, "message": "❌ Captcha expired."}
    
    if model.captcha.upper() != captchas[model.captcha_id]:
        return {"success": False, "message": "❌ Invalid captcha."}
    
    if model.username in users:
        return {"success": False, "message": "❌ Username exists."}
    
    if len(model.password) < 6:
        return {"success": False, "message": "❌ Password must be 6+ chars."}
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(model.password.encode('utf-8'), salt)
    users[model.username] = {
        "password_hash": hashed,
        "created_at": datetime.now().isoformat()
    }
    
    del captchas[model.captcha_id]
    logger.info(f"User registered: {model.username}")
    
    return {"success": True, "message": "✓ Registration successful!"}

@app.post("/login")
async def login_endpoint(model: LoginModel):
    if model.captcha_id not in captchas:
        return {"success": False, "message": "❌ Captcha expired."}
    
    if model.captcha.upper() != captchas[model.captcha_id]:
        return {"success": False, "message": "❌ Invalid captcha."}
    
    if model.username not in users:
        return {"success": False, "message": "❌ Invalid credentials."}
    
    user = users[model.username]
    if not bcrypt.checkpw(model.password.encode('utf-8'), user["password_hash"]):
        return {"success": False, "message": "❌ Invalid credentials."}
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "username": model.username,
        "created_at": datetime.now().isoformat()
    }
    
    del captchas[model.captcha_id]
    logger.info(f"User logged in: {model.username}")
    
    return {
        "success": True,
        "message": "✓ Login successful!",
        "session_id": session_id
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if request.session_id not in sessions:
        return {"response": "❌ Invalid session.", "error": True}
    
    result = await chat_service.chat(
        request.text,
        request.user,
        request.session_id
    )
    
    return result

@app.post("/logout")
async def logout_endpoint(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        if session_id in conversation_history:
            del conversation_history[session_id]
    return {"success": True, "message": "✓ Logged out."}

@app.get("/system-info")
async def system_info():
    return SystemController.get_system_info()

@app.get("/grok-info")
async def grok_info():
    return {
        "grok_configured": bool(CONFIG["grok_key"]),
        "capabilities": [
            "Real-time web search",
            "Current events analysis",
            "Deep topic analysis",
            "Reasoning with real-time data"
        ]
    }

if __name__ == "__main__":
    print("🚀 Jarvis AI v10.0 Starting...")
    print("✓ Groq LLaMA 3.3 - Enabled" if CONFIG["groq_key"] else "✗ Groq - Disabled")
    print("✓ Grok AI (XAI) - Enabled" if CONFIG["grok_key"] else "✗ Grok AI - Disabled")
    print("✓ HuggingFace Images - Enabled" if CONFIG["hf_key"] else "✗ HuggingFace - Disabled")
    print("✓ Google Search - Enabled" if CONFIG["google_api"] else "✗ Google Search - Disabled")
    print("\n📡 Starting server on http://127.0.0.1:8000")
    print("📚 Docs available at http://127.0.0.1:8000/docs\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)




