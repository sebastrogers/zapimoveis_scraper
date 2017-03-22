# Zap Imóveis - Scraper
A scraper that gathers data from [Zap Imóveis](http://zapimoveis.com.br) website.

## Installation
You will need to have docker installed in your machine in order to pull and run [Splash](http://splash.readthedocs.io/).  
|Requirements|
|-|
|[Python 3.5+](https://www.python.org/)|
|[Docker](https://www.docker.com/) |

### Pull Splash image from docker
After you have docker installed, you just need to run:

```sh
$ docker pull scrapinghub/splash
```

### Install Python requirements
Inside the project folder, install python requirements using pip:
```sh
$ pip install -r requirements.txt
```

## Usage

First, start the Splash server (or just run the shell script ``$ ./run_splash.sh``)

```sh
$ docker run -p 8050:8050 scrapinghub/splash
```

Then run the crawler:
```
$ scrapy crawl zap [-a place=<(e.g. pe+olinda)>] [-a listing_pages=n]
```
Notes:
* You can pass a number through `listing_pages` as an argument to limit the number of listing pages the scraper will search for. The default is to scrap all.
* You can also pass a place you want to search through the `place` argument, following the Zapimoveis URL format. Default: `pe+recife`.
