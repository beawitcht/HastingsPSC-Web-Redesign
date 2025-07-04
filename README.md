# HastingsPSC-Web-Redesign

[![CodeQL](https://github.com/beawitcht/HastingsPSC-Web-Redesign/actions/workflows/codeql.yml/badge.svg)](https://github.com/beawitcht/HastingsPSC-Web-Redesign/actions/workflows/codeql.yml) ![GitHub](https://img.shields.io/github/license/beawitcht/HastingsPSC-Web-Redesign) [![Twitter Follow](https://img.shields.io/twitter/follow/beawitcht?style=social)](https://www.twitter.com/beawitcht)
***

<p align="center">
    <img src="https://www.hastingspalestinecampaign.org/images/hdpsc-logo.jpg" width="200" alt="Hastings & District PSC">
</p>

## About
Redesign of The HastingsPSC website and building of custom CMS


## Setup guide

### Installation

#### Install with pip:

```bash
pip install -r requirements.txt
```
### Configure .env
#### The following environment variables are required:
```
IS_DEV = 1 # set to 1 to disable caching
SECRET_KEY= # key for admin
SECURITY_PASSWORD_SALT= # salt for admin

### Run with gunicorn
```bash
gunicorn -w 1 -b 127.0.0.1:8010 app.main:app
```
