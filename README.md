A CMS used to control a video wall installed in a public lobby.  It serves the dual purposes of sending and receiving control commands to the physical video equipment and providing a web accessible UI that can be used to add content, setup playlists, schedule playlists and directly control the wall.  It maintains a connection to a redis server that it uses to store and retrieve playlists and scheduled item times.  

Requirements:

	Redis and redis-py, redis python module - https://github.com/andymccurdy/redis-py.  

Running:

	Start the redis server first.  The run the code/delta.py file.  The site can be accessed at http://localhost:8080.

Files by directory

code:
	
	delta.py - The main server file.  Responsible for serving the UI templates as well as communicating with the external video equipment over UDP.  

	playlist.py - This module contains the classes neccessary to create, modify and manage playlists.

	sceduler.py - Classes to create and check for scheduled events.

	settings.py - Default values for control commands and machine addresses.

code/templates:

	All of the template files for the UI.

code/static:
	
	All static files used by the CMS; javascript, css, images and fonts.

	js/delta.js - The main javascript file used to communicate between the UI and the server.

code/utils:
	
	A few scripts useful for batch loading playlists and cues from variously formatted files.

loadDB:

	load_db.py - Batch load playlists, cues and scheduled items into the database.  Will check for a file called input.txt or whatever is specified on the command line.

	.bat - The batch used by windows to run