# Amulet-Operations

A collection of operation plugins for the Amulet Minecraft editor

**Amulet** - https://www.amuletmc.com/

# Plugins

## Remove Tile Entities

- `remove_tile_entities.py`

Removes all TileEntites in the selection area that have an `id` that matches a given regex string. The block is also repaced with a given block type. IDs are typically in the form `<namespace>:<basename>`.

The namespace for Minecraft in Amulet may be either `minecraft` or `universal_minecraft` so adjust your filter to cater for that.

Note that the regex filter must match the entire ID. You can use the `.*` wildcard (`.`: Any character, `*`: Zero to many times) to match multiple IDs. e.g. To remove furaces and blast furnaces:

- `(universal_)?minecraft:.*furnace`
  The `?` makes the preceding character or group optional

or

- `(universal_)?minecraft:(blast_furnace|furnace)`
  The `|` separates multiple options for a match
  Using options is faster than using `.*` and you don't run the risk of removing more TileEntities than you wanted to
