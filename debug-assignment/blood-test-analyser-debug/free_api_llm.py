import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import Any, List, Optional, Iterator
import json
from urllib.parse import quote

class FreeAPIChatModel(BaseChatModel):
    """Custom chat model that uses the free API endpoint."""
    
    def __init__(self, email: str = "kabadeprasad9@gmail.com", model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(**kwargs)
        self._email = email
        self._model = model
        self._api_url = "http://195.179.229.119/gpt/api.php"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response using the free API."""
        
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        try:
            # Build the URL to call
            api_url = f'{self._api_url}?prompt={quote(prompt)}&api_key={quote(self._email)}&model={quote(self._model)}'
            
            # Execute the HTTP request
            response = requests.get(api_url)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract the response text
            if isinstance(data, dict) and 'response' in data:
                response_text = data['response']
            elif isinstance(data, str):
                response_text = data
            else:
                response_text = str(data)
            
            # Create the AI message
            ai_message = AIMessage(content=response_text)
            
            # Create the generation
            generation = ChatGeneration(message=ai_message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            # Return an error message if the API call fails
            error_message = f"API Error: {str(e)}"
            ai_message = AIMessage(content=error_message)
            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert a list of messages to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                prompt_parts.append(f"User: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                prompt_parts.append(f"{message.type}: {message.content}")
        
        return "\n".join(prompt_parts)
    
    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "free_api_chat" 