import flet as ft
import flet.canvas as cv
import random, asyncio
from typing import Optional
from dataclasses import field

from tests.test_handler import setup_test

@ft.control
class TriangleWithText(ft.Stack):
    """A simple triangle render with text in the center."""
    initial_text: str = "PRESS TO ASK"
    triangle_offset: Optional[ft.OffsetValue] = field(
        default_factory=lambda: ft.Offset(x=0, y=-0.025)
    )
    text_color: ft.ColorValue = ft.Colors.WHITE
    bgcolor: ft.ColorValue = ft.Colors.INDIGO_900
    
    width: ft.Number = 160
    height: ft.Number = 140
    animate_opacity: Optional[ft.AnimationValue] = field(
        default_factory=lambda: ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT_CUBIC_EMPHASIZED)
    )
    animate_scale: Optional[ft.AnimationValue] = field(
        default_factory=lambda: ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT_CUBIC_EMPHASIZED)
    )
    
    def init(self):
        self.answer_text = ft.Text(
            value=self.initial_text, color=self.text_color, size=14,
            weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
            width=self.width * 0.5, opacity=1.0
        )
        
        triangle_path = cv.Path(
            elements=[
                cv.Path.MoveTo(self.width / 2, 0),
                cv.Path.LineTo(self.width, self.height),
                cv.Path.LineTo(0, self.height),
                cv.Path.Close()
            ],
            paint=ft.Paint(
                color=self.bgcolor,
                style=ft.PaintingStyle.FILL
            )
        )
        self.canvas = cv.Canvas(
            shapes=[triangle_path],
            width=self.width,
            height=self.height,
            offset=self.triangle_offset
        )
        
        self.shapes = [triangle_path]
        self.controls = [
            self.canvas, ft.Container(
                content=self.answer_text,
                width=self.width,
                height=self.height,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.only(top=35, left=15, right=15),
            )
        ]
    
    def update_answer(self, new_text: str) -> None:
        self.answer_text.value = new_text
        self.answer_text.update()

@ft.control
class EightBall(ft.Container):
    """
    An eight ball visual that is interactable.
    Change the `radius` for the dimensions.
    """
    
    radius: ft.Number = 400
    window_scale: float = 0.65
    triangle_base_scale: float = 1.5
    
    bgcolor: Optional[ft.ColorValue] = ft.Colors.INDIGO_900
    border_radius: Optional[ft.BorderRadiusValue] = radius / 2
    border: Optional[ft.Border] = field(
        default_factory=lambda: ft.Border.all(2, ft.Colors.INDIGO_ACCENT_700)
    )
    shadow: Optional[ft.BoxShadowValue] = field(
        default_factory=lambda: ft.BoxShadow(spread_radius=2, blur_radius=15, color=ft.Colors.BLACK_87)
    )
    animate_scale: Optional[ft.AnimationValue] = field(
        default_factory=lambda: ft.Animation(1000, ft.AnimationCurve.BOUNCE_OUT)
    )
    alignment: Optional[ft.Alignment] = field(default_factory=lambda: ft.Alignment.CENTER)
    
    async def get_answer(self, delay: float = 0.5) -> str:
        self.set_shake(True)
        await asyncio.sleep(delay)
        answer = random.choice(self.responses).upper()
        return answer
    
    def set_shake(self, value: bool) -> None:
        self.is_shaking = value
    
    def on_shake_end(self) -> None:
        self.set_shake(False)
    
    def init(self) -> None:
        self.responses = [
            "It is certain", "Reply hazy, try again", "Don't count on it",
            "Yes, definitely", "Ask again later", "My sources say no",
            "Without a doubt", "Cannot predict now", "Very doubtful"
        ]
        self.is_shaking = False
        
        self.triangle_thing = TriangleWithText(
            width=(self.radius * self.triangle_base_scale) * self.window_scale / 2,
            height=self.radius * self.window_scale / 2
        )
        
        self.window = ft.Container(
            content=self.triangle_thing, alignment=ft.Alignment.CENTER,
            width=self.radius * self.window_scale,
            height=self.radius * self.window_scale,
            bgcolor=ft.Colors.BLACK, border_radius=self.radius / 2,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=4, color=ft.Colors.BLACK_87)
        )
        
        self.content = self.window
        self.width = self.radius
        self.height = self.radius
        self.on_click = self.trigger_shake
        self.on_animation_end = self.on_shake_end
        
    async def trigger_shake(self, _) -> None:
        if self.is_shaking: return
        
        self.scale = 0.90
        self.triangle_thing.opacity = 0
        self.triangle_thing.scale = 0.5
        self.triangle_thing.update()
        self.update()
        
        answer = await self.get_answer()
        
        self.triangle_thing.update_answer(answer)
        self.scale = 1.0
        self.triangle_thing.opacity = 1
        self.triangle_thing.scale = 1
        self.triangle_thing.update()
        self.update()
        
        
@setup_test("Eight Ball Test")
def main(page: ft.Page):
    page.add(EightBall())


if __name__ == "__main__":
    ft.run(main)