# pyturtle

A simple turtle implementation in Python.

This is intended for both interactive sessions and keyboard control.
It came about when I was preparing a Python class and wanted to try a
few things.

There are three ways pyturtle can be used:

1. Interactively using the cursor keys to move the turtle.
   From the command line, simply call pyturtle as an application:
   
        $ python3 pyturtle.py
        
2. As a library so that the turtle can be programmed using Python.
   These are the commands that should be run when used as a library:
   
        import pyturtle as pyt  
        pyt.start()  
        my_turtle = pyt.Turtle()  
        my_turtle.move(10)  
        pyt.end()
        
3. Interactively using IDLE or a Python interactive session
   From inside IDLE (the Python interactive shell):
   
        >>> import pyturtle as pyt  
        >>> pyt.start()  
        >>> my_turtle = pyt.Turtle()  
        
   At this point you can continue to control the turtle using Python
   To end the turtle session:
   
        >>> pyt.end()
        
   Because an event handler needs to be called every so often so that
   PyGame knows that the application is alive, using PyTurtle in IDLE
   will occasionally give you a you a warning such as:
   
        "" is not responding.
   
   In that case, simply send another turtle command or ignore it.

Copyright (c) 2014-2022, Kevin (penniesfromkevin@)
