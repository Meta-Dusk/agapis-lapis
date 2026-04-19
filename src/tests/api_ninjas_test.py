import flet as ft
import os, httpx
from typing import Optional, TypeAlias, Literal
from dotenv import load_dotenv

from tests.test_handler import setup_test
from components.text import DefaultText

ResponseType: TypeAlias = Literal["author", "quote", "work"]
ResponseData: TypeAlias = list[dict[ResponseType, str]]

load_dotenv()

try:
    api_key = os.environ["NINJAS_API_KEY"]
except KeyError:
    print("Error: Missing API Key!")
    api_key = None

async def fetch_love_quote() -> Optional[str]:
    if not api_key: return
    
    api_url = "https://api.api-ninjas.com/v2/randomquotes?categories=love"
    headers = {"X-Api-Key": api_key}
    
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
            print(formatted_quote)
            
            return formatted_quote
                
        except Exception as e:
            print(f"Oops! Something went wrong: {e}")
            return

@setup_test("Love Quotes Generator")
def test(page: ft.Page) -> None:
    async def render_quote(_) -> None:
        print("Rendering a quote!")
        txt.value = "Generating a love quote..."
        txt.update()
        loading_ring.visible = True
        loading_ring.update()
        
        quote = await fetch_love_quote()
        if quote is None: quote = "Error"
        
        txt.value = quote
        txt.update()
        loading_ring.visible = False
        loading_ring.update()
    
    txt = DefaultText("Press the heart for a love quote!")
    loading_ring = ft.ProgressRing(width=50, height=50, visible=False)
    
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FAVORITE,
        on_click=render_quote
    )
    page.add(
        ft.AnimatedSwitcher(txt, duration=100, reverse_duration=100),
        loading_ring,
        ft.Text("Powered by API Ninjas", color=ft.Colors.SECONDARY, size=12)
    )

if __name__ == "__main__":
    ft.run(test)