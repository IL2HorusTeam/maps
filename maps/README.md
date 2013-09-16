This directory contains information about game maps (locations). Each map is described in a separate subdirectory.

Each subdirectory typically contains the following files:

  1. *info.json* has information about location's code name, it's size, list of positioned geographical labels,
    towns and airfields; information about location variants (winter, summer, same season in different years, etc).
    Each variant can contain different set of towns and airfields, it contain personal mission loader name, weather
    conditions info, codename and title. This information is obtained from 'labels.txt' and mission loader '*.ini' files
    from unpacked game's SFS archives.
  2. *topographical.png* is a location's map which is extrached from SFS archive and is used as real map in game. Each
    pixel represents 100x100 square meters area.
  3. *plains.png* is the result of marking plain areas (which has equal elevation) on the topographical map.
  4. *jet.png*, *terrain.png* are the height maps in blue-to-red and green-to-brown color ranges respectively. They
    have isolines, which are placed with a step of 400 meters elevation. If a map has no isolines, it means that it has
    no points equal or above 400m.
  5. *heights* is a binary array of 16-bit unsigned integers which represent heights of the map with a step of 100m.
  {plains, jet, terrain}.png were rendered using this array. The array itself was created by [heightmap creator](https://github.com/IL2HorusTeam/il2-heightmap-creator).
