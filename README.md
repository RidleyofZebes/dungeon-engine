# Dungeon Engine
Dungeon Engine is the base for a dungeon-crawl style RPG experience with roguelike inspirations. It is written in Python
with PyGame.


### changelog:
##### v0.2.2-dev | `03-24-2019`
  * Added monsters with limited A* pathfinding
  * Added descriptions for tiles, mobs, and items
  * Added an information panel for character traits and inventory. 
  * Code cleanup, bugfixes, and quality of life improvements
  
##### v0.2.1-dev | `01-24-2019`
  * Renamed project to `Dungeon Engine`
  * Added (disableable) intro, main menu, game states
  * Implemented a raycasting method to determine player view area
  * Integrated map editor into main game, accessible by pressing the tilde key
  
##### v0.2.0-dev | `01-10-2019`
  * Massive re-write of entire game
  * Basic tile-based dungeon crawl experience
  * Skeletal map editor
   
---

`11/16/2018`

*At this point, the original development for `hero-simulator` was halted and work began on a total re-write keeping only
the game logic intact, codenamed `dungeon-test`.*

---
   
##### v0.1.2-dev | `10-19-2018`
  * Your hero will now level up with XP. 
    * This is a very ham-fisted implementation, but it has laid the groundwork for more detailed character creation with
     stats.
  * Hero now has maximum hp and ability to gain bonus hp
  * Resting now has the chance to trigger an encounter
  * Added an in-game calendar and the passage of time
  * Fixed some combat dialogue not displaying
  * Fixed repeated capital letters when entering player name

##### v0.1.1-dev | `10-13-2018`
  * Added ability to take a rest to recover HP
  * Added detailed hero stats to screen between quests
  * Added hero and monster stats to combat screen
  * Fixed bug where end stats would not display on save and quit
	  
##### v0.1.0-dev | `10-12-2018`
  * Converted entire code over to pygame! Massive overhaul deserving of a version bump. May still contain bugs, but core
   game is working.
	  
##### v0.0.5-dev | `09-30-2018`
  * Rebalanced combat, better but still needs work.
  * Added chests and another monster(!) (Nothing in chests yet...)
  * Misc code cleanup

##### v0.0.4-dev | `09-30-2018`
  * Save feature is here!
  * Minor bugfixes and code cleanup
	  
##### v0.0.3-dev | `09-29-2018`
  * You can now die.
  * You have a score measured in number of monsters killed and XP earned
  * Monsters health is reset after killing so you can continue killing monsters until you run out of health.
	  
##### v0.0.2-dev | `09-28-2018`
  * Monsters can attack you now!
	  
##### v0.0.1-dev | `09-28-2018`
  * Initial upload to GitHub
  * You can attack and kill monsters until you've killed each one once.
  
### Credits

##### Design and Programming

  * Douglas J. "RidleyofZebes" Honeycutt

##### Playtesters:

  * Serenity67
  * Jillian H. Garrison
  * Hans "InfernalistGamer" Watts
  * GrayKitsune

**Pygame Text Input Module** by [Silas "Nearoo" Gyger](https://github.com/Nearoo)