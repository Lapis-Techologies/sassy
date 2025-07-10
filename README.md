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
    <img alt="Version" src="https://img.shields.io/badge/Version-2.3.9-green">
    <img alt="Stable" src="https://img.shields.io/badge/Status-Unstable-red">
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
    "url": "mongodb://localhost:27017/",
    "name": "coolname"
  },
  "bot": {
    "token": "wowie.this.isaconfig",
    "prefix": ".",
    "starboard": 5
  },
  "guild": {
    "id": 1234567890,
    "roles": {
      "admin": 1234567890,
      "dev": 1234567890,
      "reactions": {
        "message": 1234567890,
        "rofl": 1234567890,  # REMOVE ME! FORMAT: EMOJI: ROLE
        "1234567890": 1234567890
      }
    },
    "channels": {
      "welcome": 1234567890,
      "logs": 1234567890,
      "drops": 1234567890,
      "starboard": 1234567890,
      "bump": {
        "id": 1234567890,
        "bot": 1234567890
      }
    }
  },
  "xp": {
    "rewards": {
      "5": 1234567890,
      "10": 1234567890,
      "15": 1234567890,
      "20": 1234567890
    }
  },
  "commands": {
    "poll": {
      "1": 1234567890,
      "2": 1234567890,
      "3": 1234567890,
      "4": 1234567890,
      "5": 1234567890,
      "6": 1234567890,
      "7": 1234567890,
      "8": 1234567890,
      "9": 1234567890,
      "10": 1234567890
    }
}

```

# Join us!
We would love to see you in the community, your contributions to community help fuel the development of Sassy the Discord Bot. New features are added constantly, so if you see an issue with the bot, or love The Big Lez show, consider joining our [little server](https://discord.gg/HxFxPF3n25).


# License
Released under the [Apache V 2.0 License](LICENSE) license.

Sassy the Sasquatch is a side character in "[The Big Lez Show](https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL)". Please go support them!!
