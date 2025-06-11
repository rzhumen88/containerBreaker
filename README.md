### Using

- Install latest version of the Python
- `git clone https://github.com/rzhumen88/containerBreaker.git`
- Launch **cB.py**

### Adding external scripts
- Open **gamelist.txt** and append a new line containing:
	*Gamename* (**.extention*);*python module path* 
	Example: `Ren'py Archive (*.rpa);scripts/renpy/RPA.py`
	
- Create a script file *(python module path)*
- In script you should create `class Container` with following functions:
	For container exploring you should create `__init__(self, filename)` function that
	accepts path to container file, you'll be able to read all necessary file data for
	further work.
	
- Next function `getTable(self)`  gives our tool all the information about files, such as 
	filename, offset, size, compressed size, args(if no args just pass the '-' string).
	Function **should return dictionary int:tuple** with int as file ***id*** and tuple as
	***(filename, offset, size, csize, args)***
	With this you can explore your container, but not work with files.

- To extract files you should create 
	`getFile(self, fname, offset, size, csize, time)` function.
	This is simple, you get the file info and **should return
	file as bytes object.**
	
- To build the file create `buildContainer(self, iterator, saveDir)`
	function. Here you creating file in **saveDir** directory and
	generate it with  **iterator** of each 
	`(filename, bytes, compressed size, args)`.
####For more information read `scripts/example.py`
