from dotenv import load_dotenv
import aisuite as ai
import hashlib
from typing import Dict

# Local imports
from tools import *
from ConversationBuilder import CnvBuilder 

# Setup
load_dotenv()          
client = ai.Client() 
cnv = CnvBuilder(
    max_history=20,        
    important_messages=6   
)

# Cache for frequently asked questions (provides API calls)
_question_cache = {}

# ================================
def askAI(question: str) -> str:
    """
    Sends a user question to the AI and returns its response.
    Keeps a limited conversation history in `history.json`.

    Args:
        question (str): The user's input.
    
    Returns:
        str: The AI-generated response.
    """
    
    # 1. فحص الكاش للأسئلة المكررة (توفير API calls)
    question_hash = _hash_question(question)
    if question_hash in _question_cache:
        cached_answer = _question_cache[question_hash]
        print("🔄 تم استرجاع إجابة من الكاش")
        return cached_answer
    
    conversation = cnv.get_past_conversation()
    conversation.append({"role": "user", "content": question})
    
    optimized_messages = cnv.get_messages_for_model(conversation)
    
    messages_for_model = [
        {"role": "system", "content": cnv.build_prompt()}
    ] + optimized_messages
    
    response = client.chat.completions.create(
        model="openai:gpt-4o-mini", 
        messages=messages_for_model,
        tools=[
            get_services,
            update_service_prices,
            fill_template
        ],
        max_turns=10
    ) 
    
    ai_message = response.choices[0].message.content
    
    conversation.append({"role": "assistant", "content": ai_message})
    
    cnv.save_conversation(conversation)
    
    # save to cache
    _question_cache[question_hash] = ai_message
    _cleanup_cache_if_needed()
    
    return ai_message


# ================================
# Helper Functions
# ================================

def _hash_question(question: str) -> str:
    """
    Create a unique hash for the question (to detect duplicates)

    Args:
    question: Question text

    Returns:
    16-character hash string
    """
    cleaned = question.strip().lower()
    return hashlib.md5(cleaned.encode('utf-8')).hexdigest()[:16]


def _cleanup_cache_if_needed():
    """
    تنظيف الكاش تلقائياً عند تجاوز 50 سؤال
    (يحتفظ بآخر 30 فقط)
    """
    global _question_cache
    
    if len(_question_cache) > 50:
        # حذف أقدم 20 سؤال
        keys = list(_question_cache.keys())
        for key in keys[:20]:
            del _question_cache[key]
        print("🧹 تم تنظيف الكاش (حُذف 20 سؤال قديم)")


def clear_cache():
    """
    Manually clear the cache
    """
    global _question_cache
    print("✅ Cache cleared successfully")


def clear_conversation_history() -> Dict:    
    try:
        # 1. Delete history.json
        cnv.clear_history()
        
        # 2. Delete cache
        clear_cache()
        
        # 3. Delete conversation metadata
        import os
        if os.path.exists('conversation_metadata.json'):
            os.remove('conversation_metadata.json')
        
        print("✅ Conversation history cleared successfully")
        
        return {
            "status": "success",
            "message": "✅ Delete successful",
            "cleared_items": {
                "history": True,
                "cache": True,
                "metadata": True
            }
        }
        
    except Exception as e:
        error_msg = f"❌ Failed to Delete {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
