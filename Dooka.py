# import os
# os.environ.setdefault("KIVY_GL_BACKEND", "angle_sdl2")
# os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
# if os.environ.get("KIVY_GL_BACKEND") == "angle_sdl2":
#     try:
#         import importlib
#         importlib.import_module("kivy_deps.angle")
#     except Exception:
#         os.environ["KIVY_GL_BACKEND"] = "sdl2"
from user_interface.ui_dooka_kivy import DookaApp

if __name__ == "__main__":
    DookaApp().run()