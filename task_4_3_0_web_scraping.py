# -*- coding: utf-8 -*-
#                       Веб-скрапинг.
#       Задача. Получить вакансии с сайта "HeadHunter".

from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
import json
from task_4_3_0_modules import *


def get_page(url: str, headers: Dict[str, str]) -> Any:
    """Получает разметку интернет-страницы."""
    page_html: Any = requests.get(url=url, headers=headers)
    return page_html


def produce_file_name(base_name: str) -> str:
    """Создаёт имя для файла."""
    today: datetime = datetime.today()
    year: str = today.strftime('%Y')
    month: str = today.strftime('%m')
    day: str = today.strftime('%d')

    #                                 Пожалуйста подскажите, какой вариант предпочтительнее (1/2) ?
    # res_name = year + month + day + '_' + base_name      # 1)
    res_name: str = f'{year}{month}{day}_{base_name}'      # 2)
    return res_name


def print_len_satisfy(satisfy: List[Dict[str, str]]) -> None:
    """Подставляет нужное окончание в зависимости от последней цифры числа."""
    ending: str = 'й'
    len_satisfy: int = len(satisfy)
    if len_satisfy % 10 in [2, 3, 4]:
        ending = 'и'
    elif len_satisfy % 10 == 1:
        ending = 'я'
    print(f'\nНайдено {len_satisfy} ваканси{ending}.')


def view_vacancies() -> List[Dict[str, str]]:
    """Получает вакансии с сайта HeadHunter."""
    n: int    # Счётчик просмотренных вакансий на одной странице.
    satisfy: List[Dict[str, str]] = []
    base_url: str = 'https://spb.hh.ru'
    extra_url: str = '/search/vacancy?text=python&area=1&area=2'
    CUR_NUM: int = 0
    headers: Dict[str, str]
    while True:
        CUR_NUM, headers = get_headers(CUR_NUM)
        page_html: Any = get_page(base_url + extra_url, headers)
        if not (200 <= page_html.status_code < 400):
            print(" Что-то пошло не так...(страница не зарузилась)")
            return satisfy
        page_soup: Any = BeautifulSoup(markup=page_html.text, features="html.parser")
        vacancy_serpent: Any = page_soup.find('div', class_='vacancy-serp-content')
        vacancies_list: List[Any] = vacancy_serpent.find_all('div', class_='serp-item')
        n, satisfy = parse_vacancy(vacancies_list, base_url, satisfy)
        #
        print(f'{here_and_now()}   CUR_NUM ={CUR_NUM:>3}    Обработано вакансий:{n:>3}')
        #
        next_page: Any = vacancy_serpent.select_one('div.pager > a')
        if next_page is None:
            return satisfy
        extra_url = next_page['href']


def main():
    """
    Осуществляет подготовку исходных данных, выполнение основной задачи и вывод результата.
    """
    base_name: str = 'scraping_res.json'
    # print('\n Исходные данные:')

    satisfy = view_vacancies()

    print_len_satisfy(satisfy)
    res_name = produce_file_name(base_name)
    with open(res_name, 'wt', encoding='utf-8') as json_file:
        json.dump(satisfy, json_file, ensure_ascii=False, indent=2)
    # print('\n    Результаты выполнения:')
    print(f"Результаты сохранены в файле: '{res_name}'")
    
    return


if __name__ == '__main__':
    main()

    print('\n  -- Конец --  ')  # - Для блокнота
    # input('\n  -- Конец --  ')	#	Типа  "Пауза" - Для среды
