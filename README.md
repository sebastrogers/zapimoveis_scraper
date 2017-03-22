# Zap Imóveis - Scraper
A scraper that gathers data from [Zap Imóveis](http://zapimoveis.com.br) website.

## Install
You will need to have docker installed in your machine in order to pull and run Splash.  
Those are the major requirements:

|Requirements|
|-|
|[Python 3.5+](https://www.python.org/)|
|[Docker](https://www.docker.com/) |
|[Splash](http://splash.readthedocs.io/)|

### Pull Splash image from docker
After you have docker installed, you just need to run:

```sh
docker pull scrapinghub/splash
```

### Install python requirements
Inside the project folder, install python requirements using pip:
```sh
pip install -r requirements.txt
```


## Usage

First, start the Splash server (or just run the shell script ``$ ./run_splash.sh``)

```sh
$ docker run -p 8050:8050 scrapinghub/splash
```

Then start the crawler:
```
scrapy crawl zap [-a max_pages=n]
```
> You can pass a number through `max_pages` as an argument to limit the number of listing pages the scraper will search for.
