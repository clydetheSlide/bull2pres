bull2pres.py
Is a python script that generates an OpenSong set file
from a bulletin text file.

It is not terribly smart. It looks for character strings that are typical in our
worship service bulletin, ie Hymn, Sermon, Anthem
and generates a new slide for them.
The OpenSong set file is an .xml file.
Some headings, like Hymn, refer to external files. 
The file structure to find those external files is declared in the script.

There is a simple GUI built with TKinter. 
When you start up the script without any arguments it look like this
![GUI startup](startUp.png)
There are several options available for Communion liturgy. 
