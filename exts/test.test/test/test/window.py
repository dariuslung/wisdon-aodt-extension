# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ExampleWindow"]

import omni.ui as ui

LABEL_WIDTH = 120
SPACING = 4


class ExampleWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        # Set the function that is called to build widgets when the window is
        # visible
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        # It will destroy all the children
        super().destroy()

    def _build_collapsable_header(self, collapsed, title):
        """Build a custom title of CollapsableFrame"""
        with ui.HStack():
            ui.Label(title, name="collapsable_name")

            if collapsed:
                image_name = "collapsable_opened"
            else:
                image_name = "collapsable_closed"
            ui.Image(name=image_name, width=20, height=20)

    def _build(self):
        with ui.VStack():
            with ui.HStack(height = 100):
                ui.Button("Connect/Disconnect", clicked_fn = on_connect)
                ui.Button("Play", clicked_fn = on_play)

            ui.Spacer(height = 30)

            ui.Label('X | Fill X * X', height = 50)
            self.int_model = ui.SimpleIntModel(5, min=0)
            ui.IntField(self.int_model, name = 'fill_int_field', height = 50)

            ui.Spacer(height = 30)

            with ui.HStack(height = 100):
                ui.Button('Dupe UE', clicked_fn = on_dupe)
                ui.Button('Fill UE', clicked_fn = on_fill_ue)
                ui.Button('Reset count', clicked_fn = on_reset_count)

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        self._build()