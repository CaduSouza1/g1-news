# g1-news
A simple script that gets, parses, and sends news information from g1.com to the user's gmail address

## Installation
```
$ git clone https://github.com/CaduSouza1/g1-news.git
$ cd g1-news
$ pip install -r requirements.txt 
```

## Usage
```
$ python src/main.py <email> <password>
```

After a while, all the news that are not older that 1 day old will be delivered to the user's gmail address

Make sure that you can receive HTML emails. For now, this script can only send HTML emails
