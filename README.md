# HomuraMC [![Discord](https://img.shields.io/discord/1141329766889300070.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/967gvTTEWc)
English | [日本語](README_JA.md)

HomuraMC is Open Source Minecraft Server Software written in Python.  

[Join Our Discord](https://discord.gg/967gvTTEWc)
## How To (Server Admins)
> [!WARNING]  
> Homura is a pre-alpha version with most features not yet implemented! We recommend that you do not use it in a production environment. 
### Require
* Python3
* Java16 (Homura uses vanilla jar for chunk sending)
* Git (If you don't get it from the release)
### procedure
(If you want to clone the repository and get it)

First, run the following command to clone this repository.
```
git clone https://github.com/HomuraMC/Homura.git
```
Once obtained, create a Python virtual environment (recommended)
```
# Windows
python -m venv homura

# Other
python3 -m venv homura
```
If you have created a virtual environment, access Python in the virtual environment with the following command.
```
# Windows
./homura/scripts/Activate

# Other
source homura/bin/activate
```
Next, use pip to install the libraries required by Homura.
```
# Windows
pip install -r requirements.txt
# Other
python3 -m pip install -r requirements.txt
```
After installation, you can start the server by running the following command.
```
python3 main.py
```

## Trouble Shooting
### how to fix "[WinError 2] The system cannot find the file specified"
Java (JDK) is required to use the Vanilla jar for world generation.
[Install Java(JDK) from here. ( https://www.oracle.com/java/technologies/downloads/ )](https://www.oracle.com/java/technologies/downloads/)

### My friend can't connect server
Check that the IP address (leave 0.0.0.0) and port (default is 25565) in the Homura.ini file match and that the port is open. If you absolutely cannot get the port open, you can use [playit( https://playit.gg )](https://playit.gg/).

### I need help with something not mentioned here
[Issues](https://github.com/HomuraMC/Homura/issues) or [Discord](https://discord.gg/967gvTTEWc).

## Screen Shots
![Chunk send test](https://cdn.discordapp.com/attachments/1141329767858196522/1163013839932112987/image.png?ex=653e080b&is=652b930b&hm=7dcf4c7fb4ccfb8c7143032305758ab179d690f00d7ee3ac2684f9cfdefa9476&)  
![plugin test](https://cdn.discordapp.com/attachments/1141329767858196522/1162564910253879416/image.png?ex=653c65f2&is=6529f0f2&hm=d92e2095fad488ea43bb54c094ea6edfc968a84b865283ed6d1b3d85821c6ee9&)
![plugin test 2](https://cdn.discordapp.com/attachments/1141329767858196522/1162565031901282324/image.png?ex=653c660f&is=6529f10f&hm=48022d707ae097bc4c75a2df44efb9cf0be58272471aec67d92002d34cb65cf6&)

## Special Thanks
- [https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7](https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7)
- [https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509](https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509)
- [https://github.com/TMShader/QuarryMinecraftServerTests/](https://github.com/TMShader/QuarryMinecraftServerTests/)
