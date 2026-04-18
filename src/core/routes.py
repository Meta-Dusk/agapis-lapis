from dataclasses import dataclass

@dataclass
class AppRoutes:
    root = "/"
    love_quotes_generator = "/love-quotes-generator"
    magic_eight_ball = "/magic-eight-ball"

APP_ROUTES_DICT = {
    0: AppRoutes.root,
    1: AppRoutes.love_quotes_generator,
    2: AppRoutes.magic_eight_ball
}