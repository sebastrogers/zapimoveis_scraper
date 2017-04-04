# Zap Imóveis - Scraper
A scraper that gathers data from [Zap Imóveis](http://zapimoveis.com.br) website.

## Installation
You need docker installed in your machine in order to pull and run [Splash](http://splash.readthedocs.io/).  

|Major requirements|
|-|
|[Python 3.6](https://www.python.org/)|
|[Docker](https://www.docker.com/) |
|[PostgreSQL](https://www.postgresql.org/) |

### 1. Pull Splash image from docker
After you have docker installed, you just need to run:

```sh
$ docker pull scrapinghub/splash
```

### 2. Install Python requirements
Inside the project folder, install python requirements using pip:
```sh
$ pip install -r requirements.txt
```

### 3. Create the database
After installing PostgreSQL, create the database:
```sh
$ createdb zapimoveis
```

## Usage

First, start the Splash server (or just run the shell script ``$ ./run_splash.sh``)

```sh
$ docker run -p 8050:8050 scrapinghub/splash
```

Then run the crawler:
```
$ scrapy crawl zap [-a place=<(e.g. pe+olinda)>] \
                   [-a start=n] [-a count=n] [-a expiry=[nw][nd][nh][nm]]
```

**Arguments**:

* **count**: limits the number of listing pages the crawler will search for. The default is to crawl till the end.

* **start**: start crawling from a given page. The default is `1`.

* **expiry**: every time an item is inserted or updated, it's given an `updated_time` attribute. You can determine for how long the items remains valid by passing a timespan (e.g. `1h`). By default all items in the database are considered valid.

* **place**: a place you want to search, following the Zapimoveis URL format. Default: `pe+recife`.

### Examples

* Default values - Recife-PE, crawl all pages, don't scrape items already in the database:  
  ```
  $ scrapy crawl zap
  ```

* Olinda-PE, crawl 4 pages, scrape again items older than 1 day and 12 hours:  
  ```
  $ scrapy crawl zap -a count=4 -a place=pe+olinda -a expiry=1d12h
  ```

* Rio de Janeiro-RJ - south zone, crawl to the end, starting at page 100:
  ```
  $ scrapy crawl zap -a start=100 -a place=rj+rio-de-janeiro+zona-sul
  ```

* All places, starting from page 4, crawl 3 pages:
  ```
  $ scrapy crawl zap -a start=4 -a count=3 -a place=all
  ```
