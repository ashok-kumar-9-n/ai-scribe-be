from typing import Dict, Any, Optional, List
from openai import OpenAI
from app.constants.config import OPENAI_API_KEY
from app.services.logging_service import global_logger


class OpenAIUtil:
    """
    Utility class to manage prompt context and make OpenAI API calls.
    """
    _client = None  # Singleton OpenAI client

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenAIUtil with optional configuration.
        
        Args:
            config: Optional dictionary containing configuration settings.
        """
        # Create client singleton if not already created
        if not OpenAIUtil._client:
            OpenAIUtil._client = OpenAI(api_key=OPENAI_API_KEY)

        config = config or {}
        
        # Initialize message history
        system_prompt = config.get("system_prompt", "")
        user_prompt = config.get("user_prompt", "")
        
        self.messages: List[Dict[str, str]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        if user_prompt:
            self.messages.append({"role": "user", "content": user_prompt})
            
        # Set model parameters
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0)
        self.max_tokens = config.get("max_tokens", 4096)
        self.top_p = config.get("top_p", 1)
        self.response_format = config.get("response_format")

    def add_message(self, role: str, content: str) -> None:
        """
        Add a new message to the conversation.
        
        Args:
            role: The role of the message sender ('system', 'user', or 'assistant').
            content: The message content.
        """
        if role not in ["system", "user", "assistant"]:
            raise ValueError(f"Invalid role: {role}. Must be 'system', 'user', or 'assistant'.")
        
        self.messages.append({"role": role, "content": content})

    def clear_messages(self, keep_system_prompt: bool = True) -> None:
        """
        Clear the message history, optionally keeping the system prompt.
        
        Args:
            keep_system_prompt: Whether to keep the system prompt.
        """
        if keep_system_prompt:
            system_messages = [msg for msg in self.messages if msg["role"] == "system"]
            self.messages = system_messages if system_messages else []
        else:
            self.messages = []

    def update_params(self, custom: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update parameters with custom values.
        
        Args:
            custom: Dictionary of custom parameters to override defaults.
            
        Returns:
            Dictionary of updated parameters.
        """
        return {
            "messages": custom.get("messages", self.messages),
            "model": custom.get("model", self.model),
            "temperature": custom.get("temperature", self.temperature),
            "max_tokens": custom.get("max_tokens", self.max_tokens),
            "top_p": custom.get("top_p", self.top_p),
            "response_format": custom.get("response_format", self.response_format),
        }

    def get(self, custom_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a completion from the OpenAI API.
        
        Args:
            custom_params: Optional custom parameters to override defaults.
            
        Returns:
            The text response from the API.
            
        Raises:
            RuntimeError: If the API call fails.
        """
        params = self.update_params(custom_params or {})
        
        try:
            # Make the API call
            response = OpenAIUtil._client.chat.completions.create(
                model=params["model"],
                messages=params["messages"],
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],  # Use proper parameter name
                top_p=params["top_p"],
                response_format=params["response_format"] if params["response_format"] else None
            )
            
            content = response.choices[0].message.content
            if content is None:  # Check for None instead of truthiness
                raise ValueError("OpenAI returned empty content in response.")
            
            # Optionally add assistant's response to message history
            # self.add_message("assistant", content)
            
            return content
            
        except Exception as e:
            global_logger.log_event(
                {
                    "message": "error_in_openai_util_get",
                    "params": {
                        "model": params["model"],
                        "temperature": params["temperature"],
                        "max_tokens": params["max_tokens"],
                        "top_p": params["top_p"],
                        "response_format": params["response_format"]
                    },
                    "error": str(e)
                },
                level="error"
            )
            raise RuntimeError(f"Failed to get OpenAI completion: {e}") from e