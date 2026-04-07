"""LLM Service layer for Groq API integration with retry logic."""

import logging
import time
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)


class LLMService:
    """Service class for LLM API interactions with built-in resilience."""

    def __init__(self, api_key: str, base_url: str, model: str, max_tokens: int = 1024, temperature: float = 0.7):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required. Set it in .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = 3
        self.retry_delay = 1

    def generate_response(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Generate a response from the LLM with retry logic.

        Args:
            prompt: User prompt text.
            system_prompt: Optional system-level instruction.

        Returns:
            dict with 'content', 'model', 'usage' keys.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

                latency = round(time.time() - start_time, 3)

                result = {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                    "latency_seconds": latency,
                }

                logger.info(
                    f"LLM response generated | model={response.model} | "
                    f"tokens={response.usage.total_tokens} | latency={latency}s"
                )
                return result

            except RateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    raise

            except APIConnectionError as e:
                logger.error(f"API connection failed (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    raise

            except APIError as e:
                logger.error(f"API error: {e}")
                raise

    def health_check(self) -> bool:
        """Verify API connectivity with a minimal request."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
