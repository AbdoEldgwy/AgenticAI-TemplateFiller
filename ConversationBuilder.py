import json
import os
from datetime import datetime
from typing import List, Dict


class CnvBuilder:
    def __init__(self, max_history: int = 20, important_messages: int = 6) -> None:
        self.path = 'history.json'
        self.max_history = max_history
        self.important_messages = important_messages
        self.metadata_path = 'conversation_metadata.json'
    
    def build_prompt(self) -> str:
        return """
        - أنت مساعد ذكي متخصص في إنشاء قوالب مستندات مخصصة للعملاء.
        - مهمتك ملء القالب المقدم بالمعلومات ذات الصلة بناءً على مدخلات المستخدم.
        - إذا كان طلب المستخدم غير واضح، اطلب التوضيح قبل المتابعة.
        - لغتك الافتراضية هي العربية السعودية.
        
        قواعد مهمة:
        - لا تكرر الإجابات على أسئلة تم الرد عليها سابقاً
        - استخدم السياق من المحادثات السابقة
        - إذا سأل المستخدم عن شيء سبق وأجبت عليه، أشر إلى إجابتك السابقة
        """

    def get_past_conversation(self) -> list:
        
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                conversation = json.load(f)
        else:
            conversation = []
            self._save_to_file(self.path, conversation)

        return conversation

    def save_conversation(self, conversation: List[Dict]):
        if len(conversation) > self.max_history:
            # Save the first two messages (context) + the last two messages
            important_start = conversation[:2]
            recent = conversation[-(self.max_history - 2):]
            conversation = important_start + recent
        
        self._save_to_file(self.path, conversation)
        self._update_metadata(len(conversation))

    def get_messages_for_model(self, conversation: List[Dict]) -> List[Dict]:
        if len(conversation) <= self.important_messages:
            return conversation
        
        # Old messages (summary)
        old_messages = conversation[:-self.important_messages]
        # Recent messages (full)
        recent_messages = conversation[-self.important_messages:]
        
        # Create summary for old messages
        summary = self._create_summary(old_messages)
        
        # Merge summary with recent messages
        messages_with_summary = [
            {
                "role": "system", 
                "content": f"ملخص المحادثات السابقة:\n{summary}\n\n---\nالمحادثة الحالية تبدأ الآن:"
            }
        ] + recent_messages
        
        return messages_with_summary
    

    def _create_summary(self, messages: List[Dict]) -> str:
        if not messages:
            return "لا توجد محادثات سابقة"
        
        summary_parts = []
        
        # Extract essential information from messages
        user_questions = [m['content'][:100] for m in messages if m['role'] == 'user']
        ai_responses = [m['content'][:100] for m in messages if m['role'] in ['system', 'assistant']]
        
        if user_questions:
            summary_parts.append(f"أسئلة المستخدم السابقة ({len(user_questions)}): {' | '.join(user_questions[:3])}")
        
        if ai_responses:
            summary_parts.append(f"إجابات سابقة ({len(ai_responses)}): {' | '.join(ai_responses[:3])}")
        
        return "\n".join(summary_parts) if summary_parts else "محادثات عامة"


    def _save_to_file(self, path: str, data):
        ''' saves data to json file '''
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


    def _update_metadata(self, conversation_length: int):
        """
        Update the metadata for the conversation (statistics).
        """
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "total_messages": conversation_length,
            "session_info": {
                "max_history": self.max_history,
                "important_messages": self.important_messages
            }
        }
        self._save_to_file(self.metadata_path, metadata)


    def clear_history(self):
        self._save_to_file(self.path, [])
        print("✅ تم مسح تاريخ المحادثات")


    def get_statistics(self) -> Dict:
        """
        Get conversation statistics

        Returns:
        Dictionary containing statistics
        """
        conversation = self.get_past_conversation()
        
        user_messages = [m for m in conversation if m['role'] == 'user']
        ai_messages = [m for m in conversation if m['role'] in ['system', 'assistant']]
        
        return {
            "total_messages": len(conversation),
            "user_messages": len(user_messages),
            "ai_messages": len(ai_messages),
            "average_user_length": sum(len(m['content']) for m in user_messages) / len(user_messages) if user_messages else 0,
            "average_ai_length": sum(len(m['content']) for m in ai_messages) / len(ai_messages) if ai_messages else 0
        }