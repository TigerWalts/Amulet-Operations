from typing import TYPE_CHECKING, Tuple
import wx
import re

from amulet_map_editor.api.wx.ui.base_select import EVT_PICK
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor import log

from amulet.api.selection import SelectionGroup
from amulet.api.block import Block
from amulet.api.data_types import Dimension, OperationReturnType

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas

def remove_tiles_and_blocks(
    world: "BaseLevel",
    dimension: Dimension,
    target_box: SelectionGroup,
    regex_filter: str,
    fill_block: Block,
) -> OperationReturnType:
    if not isinstance(fill_block, Block):
        raise Exception("Remove Tile Entities was not given a replacement Block object")

    iter_count = 0
    for chunk, _, _ in world.get_chunk_slice_box(dimension, target_box, True):
        for tile in chunk.block_entities:
            tile_id = f"{tile.namespace}:{tile.base_name}"
            if target_box.contains_block(tile.location) and re.match(regex_filter, tile_id):
                iter_count += 1

    count = 0

    for chunk, _, _ in world.get_chunk_slice_box(dimension, target_box, True):
        keys = []
        for tile in chunk.block_entities:
            tile_id = f"{tile.namespace}:{tile.base_name}"
            if not target_box.contains_block(tile.location):
                continue
            log.info(f"Found {tile_id} at {tile.location}")
            if re.match(regex_filter, tile_id):
                log.info(f"    Matched {regex_filter}, removing")
                keys.append(tile.location)
                chunk.set_block(tile.x % 16, tile.y, tile.z % 16, fill_block)
                chunk.changed = True
                count += 1
                yield count / iter_count
        for key in keys:
            chunk._block_entities.__delitem__(key)
        log.info(f"Removed {count} Tile Entities")

class RemoveTileEntities(wx.Panel, DefaultOperationUI):
    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.Freeze()
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        options = self._load_options({})

        self._regex_filter_label = wx.StaticText(
            self,
            label="ID Filter (regex match): "
        )
        self._sizer.Add(self._regex_filter_label, 0, wx.ALL | wx.CENTER, 5)
        self._regex_filter = wx.TextCtrl(
            self,
            name="ID Filter (regex)",
            value=options.get("regex_filter") or "^namespace:basename$"
        )
        self._sizer.Add(self._regex_filter, 0, wx.ALL | wx.CENTER, 5)

        self._block_define = BlockDefine(
            self,
            world.translation_manager,
            wx.VERTICAL,
            show_pick_block=True,
            **(options.get("fill_block_options") or {"platform": world.level_wrapper.platform, "block_name": "air"})
        )
        self._block_define.Bind(EVT_PICK, self._on_pick_block_button)
        self._sizer.Add(self._block_define, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self._run_button = wx.Button(self, label="Run Operation")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self.Layout()
        self.Thaw()

    @property
    def wx_add_options(self) -> Tuple[int, ...]:
        return (1,)

    def _on_pick_block_button(self, evt):
        """Set up listening for the block click"""
        self._show_pointer = True

    def _on_box_click(self):
        if self._show_pointer:
            self._show_pointer = False
            x, y, z = self._pointer.pointer_base
            self._block_define.universal_block = (
                self.world.get_block(x, y, z, self.canvas.dimension),
                None,
            )

    def _get_fill_block(self):
        return self._block_define.universal_block[0]

    def disable(self):
        self._save_options(
            {
                "regex_filter": self._regex_filter.GetLineText(0),
                "fill_block": self._get_fill_block(),
                "fill_block_options": {
                    'platform': self._block_define.platform,
                    'version_number': self._block_define.version_number,
                    'force_blockstate': self._block_define.force_blockstate,
                    'namespace': self._block_define.namespace,
                    'block_name': self._block_define.block_name,
                    'properties': self._block_define.properties,
                },
            }
        )

    def _run_operation(self, _):
        regex_filter = self._regex_filter.GetLineText(0)
        log.info(f"Starting Remove Tile Entities Operation ({regex_filter})")
        self.canvas.run_operation(
            lambda: remove_tiles_and_blocks(
                self.world,
                self.canvas.dimension,
                self.canvas.selection.selection_group,
                regex_filter,
                self._get_fill_block(),
            )
        )


export = {
    "name": "Remove Tile Entities",  # the name of the plugin
    "operation": RemoveTileEntities,  # the actual function to call when running the plugin
}