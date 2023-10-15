# HomuraMC [![Discord](https://img.shields.io/discord/1141329766889300070.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/967gvTTEWc)
HomuraMC is Open Source Minecraft Server Software written in Python.  
[Join Our Discord](https://discord.gg/967gvTTEWc)

## Screen Shots
![Chunk send test](https://cdn.discordapp.com/attachments/1141329767858196522/1163013839932112987/image.png?ex=653e080b&is=652b930b&hm=7dcf4c7fb4ccfb8c7143032305758ab179d690f00d7ee3ac2684f9cfdefa9476&)  
![plugin test](https://cdn.discordapp.com/attachments/1141329767858196522/1162564910253879416/image.png?ex=653c65f2&is=6529f0f2&hm=d92e2095fad488ea43bb54c094ea6edfc968a84b865283ed6d1b3d85821c6ee9&)
![plugin test 2](https://cdn.discordapp.com/attachments/1141329767858196522/1162565031901282324/image.png?ex=653c660f&is=6529f10f&hm=48022d707ae097bc4c75a2df44efb9cf0be58272471aec67d92002d34cb65cf6&)

## How To Run This Program
First, clone this repository.  
```
git clone https://github.com/HomuraMC/Homura.git
``` 
Next, execute the following command in the repository directory
```
# Linux, Mac
python3 -m pip install -r requirements.txt
# Windows
pip install -r requirements.txt
```
Finally, run this command in the repository directory
```
# Linux, Mac
python3 main.py
# Windows
py main.py
```
## Trouble Shooting
### how to fix "Auth failed: [<twisted.python.failure.Failure OpenSSL.SSL.Error: [('STORE routines', '', 'unregistered scheme'), ('STORE routines', '', ' unsupported'), ('STORE routines', '', 'unregistered scheme'), ('system library', '', ''), ('STORE routines', '', 'unregistered scheme'), ('STORE routines', '', 'unsupported'), ('STORE routines', '', 'unregistered scheme'), ('system library', '', ''), ('STORE routines', '', 'unregistered scheme'), ('STORE routi nes', '', 'unsupported'), ('STORE routines', '', 'unregistered scheme'), ('system library', '', ''), ('STORE rou tines', '', 'unregistered scheme') 'unregistered scheme'), ('STORE routines', '', 'unsupported'), ('SSL routines', '', 'certificate ver ify failed')]>]"
If your operating system is Windows, run it from WSL; if you are on Linux, run the following command
```
sudo apt install openssl
```
### how to fix "[WinError 2] The system cannot find the file specified"
Java (JDK) is required to use the Vanilla jar for world generation.
[Install Java(JDK) from here. ( https://www.oracle.com/java/technologies/downloads/ )](https://www.oracle.com/java/technologies/downloads/)

### My friend can't connect server
Check that the IP address (leave 0.0.0.0) and port (default is 25565) in the Homura.ini file match and that the port is open. If you absolutely cannot get the port open, you can use [playit( https://playit.gg )](https://playit.gg/).

### I need help with something not mentioned here
[Issues](https://github.com/HomuraMC/Homura/issues) or [Discord](https://discord.gg/967gvTTEWc).

## Special Thanks
- [https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7](https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7)
- [https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509](https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509)