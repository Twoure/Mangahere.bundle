Mangahere
===========

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c94a56ddb7a24cfc97e4763d3972103b)](https://www.codacy.com/app/twoure/Mangahere-bundle?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Twoure/Mangahere.bundle&amp;utm_campaign=Badge_Grade) [![GitHub issues](https://img.shields.io/github/issues/Twoure/Mangahere.bundle.svg?style=flat)](https://github.com/Twoure/Mangahere.bundle/issues) [![](https://img.shields.io/github/release/Twoure/Mangahere.bundle.svg?style=flat)](https://github.com/Twoure/Mangahere.bundle/releases)

This plugin creates a new Photo Channel within [Plex Media Server](https://plex.tv/) (PMS) to view [Manga](https://en.wikipedia.org/wiki/Manga) from [Mangahere.co](http://www.mangahere.co/).  It is currently under development and as such, should be considered alpha software and potentially unstable.

## Features

- Read Manga
- Search Manga
- Update from within the Channel

## [Changelog](Changelog.md#changelog)

## Channel Support

##### Plex Media Server:
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 1.1.4

##### Plex Clients:
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, v1.4.1)
  - OpenPHT (Ubuntu 14.04 LTS, v1.6.1)
  - Android (4.4.2) (Plex Client App, v4.32.2.597)
  - Plex Media Player (1.1.4)
  - Plex Web (2.8.6)
  - Chromecast

## Install

- This channel can be installed via [WebTools.bundle](https://github.com/dagalufh/WebTools.bundle) or manually follow the directions below.
- Download the latest [![](https://img.shields.io/github/release/Twoure/Mangahere.bundle.svg?style=flat)](https://github.com/Twoure/Mangahere.bundle/releases) and install **Mangahere** by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to **Mangahere.bundle**
  - Copy **Mangahere.bundle** into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - Unix based platforms need to `chown plex:plex -R Mangahere.bundle` after moving it into the [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory _(`user:group` may differ by platform)_
  - **Restart PMS**

## Support

- ~~Plex Forums Thread~~
- [GitHub Issues](https://github.com/Twoure/Mangahere.bundle/issues)
