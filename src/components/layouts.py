import flet as ft

@ft.control
class CenteredColumn(ft.Column):
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER

@ft.control
class CenteredRow(ft.Row):
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER
    vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER