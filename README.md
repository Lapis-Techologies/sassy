<h1 align="center">
    <br>
    <a href="https://www.youtube.com/watch?v=9OmR0ypCyOU"><img src="https://i.ytimg.com/vi/QvIgmc2G6lk/maxresdefault.jpg" alt="Sassy the Sasquatch"></a>
    <br>
    Sassy the Sasquatch Bot
    <br>
</h1>

<h4 align="center">wadiyatalkinabeet.</h4>

<p align="center">
    <img alt="Python Versions" src="https://img.shields.io/badge/Python-3.9 | 3.10 | 3.11 | 3.12-yellow">
    <img alt="Python Library" src="https://img.shields.io/badge/Library-discord.py-blue">
    <img alt="Platforms" src="https://img.shields.io/badge/Platforms-Windows 10 | Linux (Debian)-green">
    <img alt="PRs" src="https://img.shields.io/badge/PRs-welcome-green">
    <img alt="Version" src="https://img.shields.io/badge/Version-1.6.3-green">
</p>


[//]: # (Quick Menu)

<p align="center">
    <a href="#overview">Overview</a>
    •
    <a href="#setup">Setup</a>
    •
    <a href="#join-us">Join Us!</a>
    •
    <a href="#license">License</a>
</p>

# Overview

Sassy the Discord bot is a general purpose bot themed around for the server [Sassy's Hang Out](https://discord.gg/HxFxPF3n25). It has just about everything you need to run a server and then some! The batteries are *not* included, you'll need to host the bot yourself. Sassy is designed to be robust, built to withstand errors, and elegantly handle user interactions.

[Setup](#setup) is fairly easy, you do not need to do much to get it started. 99% of all config will be done in `config.json`.



# Setup

### Config Setup
> [!WARNING]
> **Do not** touch values within "database" yet, we will fill that out in a moment.

1. Rename `config.json.example` -> `config.json`
2. Fill in each key with the proper IDs

> [!IMPORTANT]
> Rewards is special. Follow the format `"level": id`. For example: `"5": 123321,`.

### Database setup

> [!IMPORTANT]
> Sassy uses [Mongodb](https://www.mongodb.com/) for it's database. Insure you have Mongodb installed correctly before proceeding.

1. Open `config.json`
2. Set `dev` to true if you plan on developing for the bot, else set it to false
3. `url` is the url to the database, for example `mongodb://localhost:27017/`
4. `name` is the name of the database, for example `sassy`

5. Create a database named `NAME-prod`, if you plan on developing on this bot, make a `NAME-dev` database too. For example, if your database was named `sassy` then you'd make `sassy-prod` database.
6. Create 3 collections, the names are important, and need to be the same for both `prod` and `dev`
    * `economy`
    * `starboard`
    * `user`


### Example
```json
{
    "database": {
        "dev": false,
        "url": "mongodb://localhost:27017/",
        "name": "coolname" 
    },
    "bot": {
        "token": "wowie.this.isaconfig",
        "prefix": "?",
        "starboard": 5
    },
    "guild": {
      "id": 90237802347890234,
      "roles": {
        "admin": 942340784235234
      },
      "channels": {
        "welcome": 243978789423423,
        "logs": 43978423978234897,
        "drops": 2347634727946833,
        "starboard": 2347897894632378493
      }
    },
    "xp": {
      "rewards": {
        "5": 2344232342347803443,
        "10": 4308942378023482348,
        "15": 2348742387234780234,
        "20": 8974378943624234589
      }
    }
}
```


# Join us!
We would love to see you in the community, your contributions to community help fuel the development of Sassy the Discord Bot. New features are added constantly, so if you see an issue with the bot, or love The Big Lez show, consider joining our [little server](https://discord.gg/HxFxPF3n25).


# License
Released under the [Apache V 2.0 License](LICENSE) license.

Sassy the Sasquatch is a side character in "[The Big Lez Show](https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL)". Please go support them!!