# ATM simulation system

## description

&emsp;  It's an ATM simulation system with function of</br>
check balance, deposit, withdrawal, transter accounts print receipt, and login, logout.</br>

&emsp;  The client and server communicate with socket.

## client

&emsp;  The client ui is written in QT using Python, and I use the PyQt4 library.

## server

&emsp;  The server processes the connection of client with multithread. And the database I use is MySql with a table of accountinfo consists of account, password, and balance.