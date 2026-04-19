import httpx, os
from dotenv import load_dotenv
from typing import TypeAlias, Optional, Literal
from dataclasses import dataclass
from cerebras.cloud.sdk import AsyncCerebras

ResponseType: TypeAlias = Literal["author", "quote", "work"]
ResponseData: TypeAlias = list[dict[ResponseType, str]]

@dataclass
class APIKeyType:
    ninja: Optional[str] = None
    cerebras: Optional[str] = None

class APIManager:
    def __init__(self):
        self.api_keys = APIKeyType()
        self.client: AsyncCerebras = None
    
    def start(self) -> None:
        load_dotenv()
        
        try:
            self.api_keys.ninja = os.environ["NINJAS_API_KEY"]
        except KeyError:
            print("Error: Missing Ninjas API Key!")
        
        try:
            self.api_keys.cerebras = os.environ["CEREBRAS_API_KEY"]
        except KeyError:
            print("Error: Missing Cerebras API Key!")
        
        self.client = AsyncCerebras(api_key=self.api_keys.cerebras)
        print("[APIManager] Finished setup.")
    
    async def get_ninja_quote(self) -> Optional[str]:
        if self.api_keys.ninja is None: return
        
        api_url = "https://api.api-ninjas.com/v2/randomquotes?categories=love"
        headers = {"X-Api-Key": self.api_keys.ninja}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(api_url, headers=headers, timeout=3.0)
                response.raise_for_status()
                data: ResponseData = response.json()
                
                if not data:
                    print("No quotes found for this category.")
                    return
                
                quote = data[0].get("quote", "Missing quote")
                author = data[0].get("author", "Unknown")
                
                formatted_quote = f"\"{quote}\"\n— {author}"
                print(f"[Ninjas] {formatted_quote}")
                
                return formatted_quote
                    
            except Exception as e:
                print(f"Oops! Something went wrong: {e}")
                return
    
    async def get_cerebras_quote(self, theme: Optional[str] = None, language: str = "English") -> str:
        if self.api_keys.cerebras is None: return "[Cerebras] Missing API Key!"
        
        vibe = theme if theme else "general love"
        
        system_prompt = f"""
        You are a modern world-class curator of romantic literature and a poetic translator.
        Your goal is to provide a beautiful, short love quote in {language}.
        The quotes should be short like a one-liner for maximum impact.
        An example of a quote you could make would be: "I want to be your favorite hello and your hardest goodbye."
        
        RULES:
        1. If a famous quote exists for the theme "{vibe}", provide it with the author's name.
        2. If no famous quote fits, generate an original, soul-stirring quote in the style of 19th-century or modern poets.
        3. The quote MUST be in {language}. If there are no quotes in {language}, then you can just translate it.
        4. FORMAT: "Quote text" \n— Author Name (or 'Unknown' if you wrote it).
        """
        
        user_prompt = f"Give me one heart-touching quote about {vibe}."
        try:
            response = await self.client.chat.completions.create(
                model="llama3.1-8b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=1.0,
                top_p=0.9,
                max_tokens=600,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return str(e)