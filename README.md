# zmpl
Out of process plotting with zeromq and matplotlib. 

zmpl implements a poor's man RPC between a client (your python script) and a server (process where the acutal plotting occurs) to make matplotlib more interactive. I built this tool out of frustration of not being able to visualize data while debugging with [PTVS](https://github.com/Microsoft/PTVS).
