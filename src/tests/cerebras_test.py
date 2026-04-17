import flet as ft
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import AsyncCerebras
from typing import Optional

from tests.test_handler import setup_test
from components.text import DefaultText


load_dotenv()

try:
    api_key = os.environ["CEREBRAS_API_KEY"]
except KeyError:
    print("Error: Missing API Key!")

client = AsyncCerebras(api_key=api_key)

async def get_love_quote(theme: Optional[str] = None, language: str = "English") -> str:
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
        response = await client.chat.completions.create(
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

@setup_test("Love Quotes Generator")
def main(page: ft.Page) -> None:
    async def render_quote(_) -> None:
        print("Rendering a quote!\n")
        txt.value = "Generating a love quote..."
        txt.update()
        loading_ring.visible = True
        loading_ring.update()
        
        quote = await get_love_quote()
        quote.strip("\n").strip()
        
        print(f"Received quote: {quote}\n")
        txt.value = quote
        txt.update()
        loading_ring.visible = False
        loading_ring.update()
    
    txt = DefaultText("Press the heart for a love quote!")
    loading_ring = ft.AnimatedSwitcher(
        ft.ProgressRing(width=50, height=50),
        duration=100, reverse_duration=100, visible=False
    )
    
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FAVORITE, on_click=render_quote
    )
    page.add(
        ft.AnimatedSwitcher(txt, duration=100, reverse_duration=100),
        loading_ring,
        ft.Text("Powered by Cerebras", color=ft.Colors.SECONDARY, size=12)
    )

if __name__ == "__main__":
    ft.run(main)