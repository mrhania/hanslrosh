Hanslrosh
=========

A game I have created as my end-term project for *Creating Interactive Applications in Python* course. *Hanslrosh* name comes from *Hack ANd SLash ROguelike Survival Horror* which pretty much describes what I wanted to make. *Hack and slash* because of the "kill everything that moves" gameplay, *roguelike* because of the tile-based randomly generated dungeons and *survival horror* becuse of zombies trying to kill you.

You have couple of zombie types, couple of weapons and boring as hell randomly generated dungeons. Your only goal is to try staying alive as possible - which is not dead easy because of never ending hunger. Of course the game turned out to be not fun at all and I discovered that my game-designer-sense suck but still - its playable.

Controls are simple: move using `WSAD`, shoot using mouse, hit `F` to pick up a gun when standing above it, `R` to reload and `space` to skip to next level (introduced for debugging purposes).

Requires `python` with `pygame` library installed to run. Unfortunately, source code comments and docs are in Polish, so you have to live with that.


Credits
-------

While source is 100% my creation most of the graphics is not.
Splash and background screens has been found on [wallbase][wallbase], ground tiles has been dug in [The RPG Maker Resource Kit][rmrk] forums, characters are from great [ftorek's Rougelike RPG starter-pack][ftorek] and guns has been taken from [Counter Strike 2D][cs2d].
FOV implementation and level generation algorithms are based on [RogueBasin][roguebasin] articles.
Oh, and fonts... I have no idea where I found them.

[wallbase]: http://wallbase.cc/
[rmrk]: http://rmrk.net/index.php?topic=35095.0
[ftorek]: http://forum.warsztat.gd/index.php?topic=14626.0
[cs2d]: http://www.cs2d.com/
[roguebasin]: http://roguebasin.roguelikedevelopment.org/
