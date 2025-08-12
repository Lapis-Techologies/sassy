<h1 align="center">
    <br>
    <a href="https://www.youtube.com/watch?v=9OmR0ypCyOU"><img src="https://i.ytimg.com/vi/QvIgmc2G6lk/maxresdefault.jpg" alt="Sassy the Sasquatch"></a>
    <br>
    Sassy the Sasquatch Bot
    <br>
</h1>

<h4 align="center">wadiyatalkinabeet.</h4>

<p align="center">
    <img alt="Python Versions" src="https://img.shields.io/badge/Python-3.12+-yellow">
    <img alt="Python Library" src="https://img.shields.io/badge/Library-discord.py-blue">
    <img alt="Platforms" src="https://img.shields.io/badge/Platforms-Windows 10 | Windows 11 | Linux (Debian)-green">
    <img alt="PRs" src="https://img.shields.io/badge/PRs-welcome-green">
    <img alt="Version" src="https://img.shields.io/badge/Version-2.4.0-green">
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

Sassy is a general-purpose Discord bot designed for the [Sassy's Hang Out](https://discord.gg/HxFxPF3n25) server. It offers nearly every feature you need to manage a server—and more! Note that you'll need to host the bot yourself. Sassy is built to handle errors gracefully and interact with users elegantly.

Setup is simple, with almost all configuration done in `config.json`.

# Setup

### Config Setup
> [!WARNING]
> **Do not** modify values within "database" until instructed.

1. Rename `config.json.example` to `config.json`.
2. Fill in each key with the correct IDs.

> [!IMPORTANT]
> For Rewards, use the format `"level": id` (e.g., `"5": 123321,`).

### Database Setup

> [!IMPORTANT]
> Sassy uses [MongoDB](https://www.mongodb.com/) as its database. Ensure MongoDB is properly installed before proceeding.

> [!IMPORTANT]
> Steps 5 & 6 are optional but may be necessary depending on your setup.

1. Open `config.json`.
2. Set `dev` to `true` if developing the bot; otherwise, set it to `false`.
3. Set `url` to your database URL (e.g., `mongodb://localhost:27017/`).
4. Set `name` to your database name (e.g., `sassy`).

### Example
```json
{
  "database": {
    "dev": false,
    "url": "mongodb+srv://username:password@name.node.mongodb.net/?retryWrites=true&w=majority&appName=ClusterName",
    "name": "sassy"
  },
  "bot": {
    "token": "very.secret.token",
    "prefix": ".",
    "starboard": 5
  },
  "guild": {
    "id": 1234,
    "roles": {
      "admin": 1234,
      "dev": 1234,
      "reactions": {
        "message": 1234,
        "1234": 1234,
        "🤣": 1234
      }
    },
    "channels": {
      "welcome": 1234,
      "logs": 1234,
      "drops": 1234,
      "starboard": 1234,
      "reaction_role": 1234,
      "rules": 1234,
      "bump": {
        "id": 1234,
        "bot": 1234
      }
    }
  },
  "xp": {
    "rewards": {
      "5": 1234,
      "10": 1234,
      "15": 1234,
      "20": 1234
    },
    "multipliers": {
      "level": 1,
      "choomah_coins": 0.5,
      "bumps": 1.1
    }
  },
  "commands": {
    "poll": {
      "1": 1234,
      "2": 1234,
      "3": 1234,
      "4": 1234,
      "5": 1234,
      "6": 1234,
      "7": 1234,
      "8": 1234,
      "9": 1234,
      "10": 1234
    }
  }
}
```

# Join us!
We would love to see you in the community, your contributions to community help fuel the development of Sassy the Discord Bot. New features are added constantly, so if you see an issue with the bot, or love The Big Lez show, consider joining our [little server](https://discord.gg/HxFxPF3n25).


# License
Released under the [Apache V 2.0 License](LICENSE) license.

Sassy the Sasquatch is a side character in "[The Big Lez Show](https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL)". Please go support them!!
