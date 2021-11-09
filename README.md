# Amulet-Operations

A collection of operation plugins for the Amulet Minecraft editor

**Amulet** - https://www.amuletmc.com/

# Plugins

## Remove Tile Entities

- `remove_tile_entities.py`

Takes a regex filter string and removes all TileEntites in the selection area that match the `id` tag. IDs are typically in the form `<namespace:basename>`.

The namespace for Minecraft in Amulet may be either `minecraft` or `universal_minecraft` so adjust your filter to cater for that.

Note that the regex filter must match the entire id, use the `.*` wildcard to match multiple ids. e.g. remove furaces and blast furnaces with:

- `(universal_)?minecraft:.*furnace`
