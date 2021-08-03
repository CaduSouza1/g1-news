import pathlib
import scrap
import json

parser = scrap.G1Parser()
nc = scrap.NewsCollection()

with (
    open("example_data.json") as example_data,
):
    rawData = json.loads(example_data.read())
    for parsedData in parser.ParseNews("education", rawData):
        nc.AddNew(parsedData)

    