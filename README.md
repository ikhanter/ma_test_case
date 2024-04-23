### Task

Make a parser of Metro C&C: https://online.metro-cc.ru/

Choose a category of the goods and make 2 CSV-files with parsed data.
Need to get data of all goods with chosen category in Moscow and Saint-Petersburg.

Mandatory data: 
- id of the good, 
- name, 
- url, 
- regular price, 
- promo price, 
- brand.

### Requirements (pyproject.toml)
- python = "^3.10"
- requests = "^2.31.0"
- pandas = "^2.2.2"
- aiohttp = "^3.9.5"
- asyncio = "^3.4.3"

### Solution
Парсер сам выбирает случайную категорию, извлекает субкатегории товаров и отправляет асинхронные запросы к API с целью получения списка товаров заданных субкатегорий из магазинов конкретного города. Затем полученный данные формируют Dataframe и экспортируются в CSV.
В рамках задания были выбраны магазины Москвы и Санкт-Петербурга (они определены из общего списка магазинов по графе города, но можно автоматизировать и рандомизировать (либо сделать полный парсинг по всем городам) и этот процесс).

The parser itself selects a random category, extracts subcategories of goods and sends asynchronous requests to the API in order to obtain a list of goods of specified subcategories from stores in a specific city. Then the resulting data is formed into a Dataframe and exported to CSV.
As part of the task, stores in Moscow and St. Petersburg were selected (they were determined from the general list of stores by city column, but this process can be automated and randomized (or do a full parsing for all cities)).

### Path
```ma_test_case/parser.py```

### Start
```make start```

### Examples
```Сладости_ чипсы_ снеки_Moscow.csv```
```Сладости_ чипсы_ снеки_SPb.csv```