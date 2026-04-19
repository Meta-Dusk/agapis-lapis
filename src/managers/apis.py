import httpx
from typing import Optional, Literal, TypeAlias
from dataclasses import dataclass

SourceTypes: TypeAlias = Literal["ninja", "cerebras"]
NinjaData: TypeAlias = dict[Literal["success", "quote", "author", "source"], bool | str]
CerebrasData: TypeAlias = dict[Literal["success", "text"], bool | str]

@dataclass
class QuoteData:
    quote: str
    author: str
    source: str | SourceTypes

@dataclass
class ProxyURL:
    base: str
    
    def get_quote(self, endpoint: SourceTypes) -> str:
        return f"{self.base}/generate-quote/{endpoint}"

class APIManager:
    def __init__(self):
        self.proxy = ProxyURL("https://agapis-lapis-proxy.onrender.com")
        print("[APIManager] Connected to proxy server.")
    
    async def get_ninja_quote(self) -> Optional[QuoteData]:
        endpoint = self.proxy.get_quote("ninja")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(endpoint)
                response.raise_for_status()
                
                data: NinjaData = response.json()
                
                if data.get("success"):
                    return QuoteData(
                        quote=data.get("quote"),
                        author=data.get("author"),
                        source=data.get("source", "api-ninjas")
                    )
                return None
            except httpx.TimeoutException:
                print("[Timeout] Server took too long to wake up.")
                return QuoteData(
                    quote="The oracle is waking from a deep slumber... Please try again in a moment.",
                    author="System",
                    source="error"
                )
            except httpx.HTTPError as e:
                print(f"[Ninja Proxy Error]: {e}")
                return None

    async def get_cerebras_quote(
        self, vibe: str = "general love", language: str = "English"
    ) -> Optional[QuoteData]:
        endpoint = self.proxy.get_quote("cerebras")
        
        # httpx handles passing these variables into the URL automatically
        params = {
            "vibe": vibe,
            "language": language
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data: CerebrasData = response.json()
                
                if data.get("success"):
                    # The server returns the AI's raw text: "Quote" \n— Author
                    raw_text: str = data.get("text", "")
                    
                    if "—" in raw_text:
                        parts = raw_text.rsplit("—", 1)
                        quote_part = parts[0].strip().strip('"').strip() # Removes the quotes and spaces
                        author_part = parts[1].strip()
                    else:
                        quote_part = raw_text.strip().strip('"').strip()
                        author_part = "Unknown"

                    return QuoteData(
                        quote=quote_part,
                        author=author_part,
                        source="cerebras"
                    )
                return None
            except httpx.TimeoutException:
                print("[Timeout] Server took too long to wake up.")
                return QuoteData(
                    quote="The stars are aligning... give the oracle just a moment to wake up, then try again.",
                    author="System",
                    source="error"
                )
            except httpx.HTTPError as e:
                print(f"[Cerebras Proxy Error]: {e}")
                return None