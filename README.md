# HomuraMC [![Discord](https://img.shields.io/discord/1141329766889300070.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/967gvTTEWc)
HomuraMC is Open Source Minecraft Server Software written in Python.  
[Join Our Discord](https://discord.gg/967gvTTEWc)
## How To (Server Admins)
##### Note: Homura is a pre-alpha version with most features not yet implemented! We recommend that you do not use it in a production environment. 
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
python -m venv homura
```
If you have created a virtual environment, access Python in the virtual environment with the following command.
```
./homura/scripts/Activate
```
Next, use pip to install the libraries required by Homura.
```
pip install -r requirements.txt
```
After installation, you can start the server by running the following command.
```
python3 main.py
```

## Special Thanks
- [https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7](https://qiita.com/YuzuRyo61/items/da7a6e55616254eb63d7)
- [https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509](https://github.com/barneygale/quarry/issues/135#issuecomment-1088143509)
