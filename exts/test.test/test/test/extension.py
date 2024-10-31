import omni.ext
import omni.ui as ui
import omni.kit.app
import omni.kit.actions.core as actions
import omni.usd
from aodt.configuration.worker_manager import get_worker_manager_instance

# Ensure extensions enabled
app = omni.kit.app.get_app()
manager = app.get_extension_manager()
manager.set_extension_enabled("omni.services.core", True)

# API
from omni.services.core import main, routers
import omni.kit.pipapi
from typing import Optional
from pydantic import BaseModel, Field


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[test.test] some_public_function was called with x: ", x)
    return x ** x

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class TestTestExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.

    def on_startup(self, ext_id):
        print("[test.test] test test startup")

        usd_context = omni.usd.get_context()

        # UE count
        self.ue_count = 1

        def on_connect():
            get_worker_manager_instance().request_worker()

        def on_play():
            actions.execute_action(extension_id = "omni.kit.widget.toolbar", action_id = "toolbar::play")

        def on_dupe():
            # Open stage
            # result, error_str = usd_context.open_stage_async(stage_url)
            
            # Gets UsdStage handle
            stage = usd_context.get_stage()
            prim_path = '/UEs/ue_0001'
            self.ue_count = self.ue_count + 1
            path_to = f'/UEs/ue_{self.ue_count:04}'
            omni.usd.duplicate_prim(stage, prim_path, path_to)

            # Modify ID
            prim = omni.usd.get_prim_at_path(path_to)
            omni.usd.set_prop_val(prim.GetProperty('aerial:ue:user_id'), self.ue_count)

        def on_fill_ue():
            stage = usd_context.get_stage()
            prim_path_start = '/UEs/ue_0001'
            prim_start = omni.usd.get_prim_at_path(prim_path_start)
            prim_path_end = '/UEs/ue_0002'
            prim_end = omni.usd.get_prim_at_path(prim_path_end)

            # Get pos from first time sample
            start_pos_attr = prim_start.GetProperty('xformOp:translate')
            start_pos = start_pos_attr.Get(start_pos_attr.GetTimeSamples()[0])
            end_pos_attr = prim_end.GetProperty('xformOp:translate')
            end_pos = end_pos_attr.Get(end_pos_attr.GetTimeSamples()[0])

            diff_x = end_pos[0] - start_pos[0]
            diff_y = end_pos[1] - start_pos[1]
            diff_z = end_pos[2] - start_pos[2]

            fill_num = self.int_model.get_value_as_int()
            step_x = diff_x / (fill_num - 1)
            step_y = diff_y / (fill_num - 1)
            # step_z = diff_z / (fill_num - 1)

            cur_x = start_pos[0]
            cur_y = start_pos[1]
            # cur_z = start_pos[2]
            count = 1
            for i in range(fill_num):
                cur_x = start_pos[0]

                for j in range(fill_num):
                    path_to = f'/UEs/ue_{count:04}'
                    omni.usd.duplicate_prim(stage, prim_path_start, path_to)

                    # Modify ID
                    prim = omni.usd.get_prim_at_path(path_to)
                    omni.usd.set_prop_val(prim.GetProperty('aerial:ue:user_id'), count)

                    new_pos = (cur_x, cur_y, start_pos[2])
                    # new_pos = (cur_x, cur_y, cur_z)
                    pos_attr = prim.GetProperty('xformOp:translate')
                    times = pos_attr.GetTimeSamples()

                    # For UE attribute with TimeCode
                    if times:
                        omni.usd.set_prop_val(pos_attr, new_pos, times[0])
                    else:
                        omni.usd.set_prop_val(pos_attr, new_pos)
                    
                    count = count + 1
                    cur_x = cur_x + step_x
                
                cur_y = cur_y + step_y
                # cur_z = cur_z + step_z
            

        def on_reset_count():
            self.ue_count = 1

        # Window
        self._window = ui.Window("Test Extension", width=500, height=500)
        with self._window.frame:
            with ui.VStack():
                with ui.HStack(height = 100):
                    ui.Button("Connect/Disconnect", clicked_fn = on_connect)
                    ui.Button("Play", clicked_fn = on_play)

                ui.Spacer(height = 30)

                ui.Label('X | Fill X * X', height = 50)
                self.int_model = ui.SimpleIntModel(5, min = 0, max = 1000000000000000) # 10^15
                ui.IntField(self.int_model, name = 'fill_int_field', height = 50)

                ui.Spacer(height = 30)

                with ui.HStack(height = 100):
                    ui.Button('Dupe UE', clicked_fn = on_dupe)
                    ui.Button('Fill UE', clicked_fn = on_fill_ue)
                    ui.Button('Reset count', clicked_fn = on_reset_count)


        # API
        router = routers.ServiceAPIRouter()

        # Worker
        class WorkerResponse(BaseModel):

            success: bool = Field(
                default = False,
                title = 'Status',
                description = 'Status',
            )

            error_message: Optional[str] = Field(
                default = None,
                title = 'Error message',
                description = 'Optional error message in case the operation was not successful.',
            )

        @router.get(
            path = '/worker',
            summary = '',
            description = '',
            tags = ['placeholder'],
            response_model = WorkerResponse
        )

        async def request() -> WorkerResponse:
            get_worker_manager_instance().request_worker()
            return WorkerResponse(
                success = True,
            )

        # Play
        class PlayResponse(BaseModel):

            success: bool = Field(
                default = False,
                title = 'Status',
                description = 'Status',
            )

            error_message: Optional[str] = Field(
                default = None,
                title = 'Error message',
                description = "Optional error message in case the operation was not successful.",
            )

        @router.get(
            path = '/play',
            summary = '',
            description = '',
            tags = ['placeholder'],
            response_model = PlayResponse
        )

        async def request() -> PlayResponse:
            actions.execute_action(extension_id = "omni.kit.widget.toolbar", action_id = "toolbar::play")
            return PlayResponse(
                success = True,
            )
        
        main.register_router(router=router)

    def on_shutdown(self):
        print("[test.test] test test shutdown")