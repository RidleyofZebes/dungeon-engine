# Dungeon Engine

Dungeon Engine is the base for a dungeon-crawl style RPG experience with roguelike inspirations. It is written in Python with PyGame.

![Title Screen](https://i.imgur.com/eWYknKa.png)

[More Screenshots...](https://imgur.com/gallery/vY8L8dL)

## Controls

Key   | Action
----- | -----------------
`W, S` | Forward, Backward
`A, D` | Turn left, right
`A, D + Shift` | Strafe left, right
`Z` | Rest
`Space` | Activate
`Ctrl + R` | Reset dungeon
`Ctrl + Z` | Save
`Ctrl + X` | Load
`Mouse` | Inventory, equipment, and most other basic controlls

---

## Changelog

### [v0.3.3-dev](https://github.com/RidleyofZebes/dungeon-engine/releases/tag/v0.3.3-dev) | `09-20-2019`

* Stable testing release
* Kinda forgot to keep track of changelog
* Changelog will only be updated on releases
* Check git commits for detailed changes
  
#### v0.2.2-dev | `03-24-2019`

* Added monsters with limited A* pathfinding
* Added descriptions for tiles, mobs, and items
* Added an information panel for character traits and inventory.
* Code cleanup, bugfixes, and quality of life improvements
  
#### v0.2.1-dev | `01-24-2019`

* Renamed project to `Dungeon Engine`
* Added (disableable) intro, main menu, game states
* Implemented a raycasting method to determine player view area
* Integrated map editor into main game, accessible by pressing the tilde key
  
#### v0.2.0-dev | `01-10-2019`

* Massive re-write of entire game
* Basic tile-based dungeon crawl experience
* Skeletal map editor

---

`11/16/2018`

*It was at this point that the original development for my beginner's project, [`hero-simulator`](https://github.com/RidleyofZebes/hero-simulator), was halted and work began on a total re-write keeping only the game logic intact, codenamed `dungeon-test`.*

---
  
### Credits

#### Design and Programming

* Douglas J. "RidleyofZebes" Honeycutt

#### Playtesters

* Serenity67
* Jillian H. Garrison
* Hans "InfernalistGamer" Watts
* GrayKitsune

**Pygame Text Input Module** by [Silas "Nearoo" Gyger](https://github.com/Nearoo)
