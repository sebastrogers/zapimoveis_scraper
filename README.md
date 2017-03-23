# Zap Imóveis - Scraper
A scraper that gathers data from [Zap Imóveis](http://zapimoveis.com.br) website.

## Installation
You will need to have docker installed in your machine in order to pull and run [Splash](http://splash.readthedocs.io/).  

|Major requirements|
|-|
|[Python 3.5+](https://www.python.org/)|
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
$ scrapy crawl zap [-a place=<(e.g. pe+olinda)>] [-a listing_pages=n]
```

Notes:

* You can pass a number through `listing_pages` as an argument to limit the number of listing pages the scraper will search for. The default is to scrap all.

* You can also pass a place you want to search through the `place` argument, following the Zapimoveis URL format. Default: `pe+recife`.

### Examples

* Default values (Recife-PE, all linsting pages):  
  ```
  $ scrapy crawl zap
  ```

* Olinda-PE, 4 linsting pages:  
  ```
  $ scrapy crawl zap -a listing_pages=4 -a place=pe+olinda
  ```

* Rio de Janeiro-RJ - south zone, all linsting pages:  
  ```
  $ scrapy crawl zap -a place=rj+rio-de-janeiro+zona-sul
  ```

* All places, 3 linsting pages:  
  ```
  $ scrapy crawl zap -a listing_pages=3 -a place=all
  ```
