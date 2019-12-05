
Basic message boards server and client
======================================

Prereqesites
------------
1. Have a version of python3 installed
2. Ensure your version of python3 has the module: socket, sys, json, os, * from _thread, threading

Server
------
1. To run the server type **python server.py <serverip> <port>** into the command line. Or use **python3**.
2. The server will not run if the socket is busy.
3. The server will not run if there is no **board** foler in the directory that it is run from.
4. The server will not run if there are no subdirectories in the **board** folder.
5. Try not to modify the file system manually while running the server this could produce unexpected behavior.

To run the server successfully make sure to specify all the required arguments accurately, make sure you are using an idle socket/port, **DON'T MODIFY THE FILE SYSTEM** while the server is running, make sure there is a **board** folder in the same directory as **server.py**, and make sure there is atleast one subdirectory in the **board** folder. 

Client
------
1. To run the client type python **client.py <serverip> <port>** into the command line. Or use **python3**.
2. The client will stop running at any time if it cannot connect to the server, or the connection request timeouts.
3. The client will stop running if the server does not run as expected during the inital connection request (GET_BOARDS).
4. If the inital connection is successful any subsequent bad responses from the server will not cause the client to stop running.

To run the client successfully make sure you specify all teh required arguments accurately, and make sure the server is running on the socket you have specified.