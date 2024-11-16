[![CHANNEL](https://img.shields.io/badge/-CHANNEL-black?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/hidden_coding)
[![CHAT](https://img.shields.io/badge/-CHAT-black?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/hidden_codding_chat)
[![BOT LINK](https://img.shields.io/badge/-BOT%20LINK-black?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/wheelofwhalesbot?start=CGYJGk91pub)
[![BOT MARKET](https://img.shields.io/badge/-BOT%20MARKET-black?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/hcmarket_bot?start=referral_5143703753)

## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
|                         Feature                          | Supported |
|:--------------------------------------------------------:|:---------:|
|                      Multithreading                      |     ✅     |
|                 Proxy binding to session                 |     ✅     |
|                      Auto Referral                       |     ✅     |
|                Automatic joining to squad                |     ✅     |
|                       AutoTapper                         |     ✅     |
|                       AutoSpins                          |     ✅     |
|              AutoPlay games (Flappy and Dino)            |     ✅     |
|                       AutoTasks                          |     ✅     |
|                       WebSockets                         |     ✅     |
|              Support for pyrogram .session               |     ✅     |

## [Settings](https://github.com/yummy1gay/WheelOfWhales/blob/main/.env-example/)
|         Settings            |                                     Description                                     |
|:---------------------------:|:-----------------------------------------------------------------------------------:|
|        **API_ID**           |           Platform data from which to run the Telegram session (default - android)  |
|       **API_HASH**          |           Platform data from which to run the Telegram session (default - android)  |
|       **AUTO_TAP**          |                      Automatic clicking (default - True)                            |
|        **SCORE**            |                 Score per game (default is [5, 30] (That is, 5 to 30))              |
|      **SQUAD_NAME**         |               @username of the squad channel/chat without the '@' symbol            |
|        **REF_ID**           |                         Text after 'start=' in your referral link                   |
|       **AUTO_TASKS**        |                        Automatically performs tasks (default - False)               |
|  **AUTO_CLAIM_REF_REWARD**  |                             Name saying itself (default - True)                     |
| **USE_RANDOM_DELAY_IN_RUN** |                             Name saying itself (default - True)                     |
|   **RANDOM_DELAY_IN_RUN**   |                     Random seconds delay for ^^^ (default is [5, 30])               |
|       **NIGHT_MODE**        |               Pauses operations from 22:00 to 06:00 UTC (default - False)           |
| **USE_PROXY_FROM_FILE**     |      Whether to use a proxy from the `bot/config/proxies.txt` file (True / False)   |

## Quick Start 📚

To quickly install the required libraries and run the bot:

1. Open `run.bat` on Windows or `run.sh` on Linux.

---

## Prerequisites

Make sure you have Python **3.10** installed.  
Download Python [here](https://www.python.org/downloads/).

### Obtaining API Keys

1. Visit [my.telegram.org](https://my.telegram.org) and log in with your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Note down your **API_ID** and **API_HASH** from the site and add them to the `.env` file.

---

## Installation
You can download the [**repository**](https://github.com/yummy1gay/WheelOfWhales) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/yummy1gay/WheelOfWhales.git
cd WheelOfWhales
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/WheelOfWhales >>> python3 main.py --action (1/2)
# Or
~/WheelOfWhales >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/WheelOfWhales >>> python main.py --action (1/2)
# Or
~/WheelOfWhales >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```




### Contacts

[![Support](https://img.shields.io/badge/For%20support%20or%20questions-BOT%20AUTHOR-blue?style=for-the-badge&logo=telegram&logoColor=white&labelColor=black)](https://t.me/yummy1gay)