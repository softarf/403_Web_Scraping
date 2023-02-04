# -*- coding: utf-8 -*-
#                       Веб-скрапинг.
#       Задача. Получить вакансии с сайта "HeadHunter".

from typing import Any, Dict, List, Tuple
from datetime import datetime
import re

from fake_headers import Headers


def get_headers(cur_num: int) -> Tuple[int, Dict[str, str]]:
    """Генерирует заголовки для requests-запроса."""
    browsers: List[str] = ['chrome', 'firefox', 'opera']
    oss: List[str] = ['win', 'mac', 'lin']
    n: int = cur_num % 9
    i: int = n // 3
    j: int = n - i * 3
    cur_browser: str = browsers[i]
    cur_os: str = oss[j]
    cur_num += 1
    return cur_num, Headers(browser=cur_browser, os=cur_os).generate()


def here_and_now() -> str:
    """Печатает текущее время и дату."""
    today: datetime = datetime.today()
    wday: str = today.strftime('%a')
    day: str = today.strftime('%d')
    month: str = today.strftime('%b')
    year: str = today.strftime('%Y')
    hour: str = today.strftime('%H')
    minute: str = today.strftime('%M')
    second: str = today.strftime('%S')
    return f'Now: {wday}, {day} {month} {year} {hour}:{minute}:{second}'


def get_preferences(vacancy: Any) -> List[str]:
    """Получает описание должности и необходимых знаний."""
    # Предпочтения: (Должностные обязанности, Требования к кондидатам).
    duty_require: List[str] = ['Не указано', 'Не указано']
    vacancy_content: Any = vacancy.find('div', class_='g-user-content')
    if vacancy_content is not None:
        preferences: Any = vacancy_content.find_all('div', class_='bloko-text')
        item: Any
        for item in preferences:
            if item['data-qa'] == 'vacancy-serp__vacancy_snippet_responsibility':
                duty_require[0] = item.text
            elif item['data-qa'] == 'vacancy-serp__vacancy_snippet_requirement':
                duty_require[1] = item.text
    return duty_require


def is_include(element: str, *args: Any) -> bool:
    """Проверяет, что 'element' встречается хотя бы один раз."""
    flag: bool = False
    arg: Any
    for arg in args:
        if re.search(element, arg, flags=re.I) is not None:
            flag = True
            break
    return flag


def get_wage(vacancy: Any) -> Tuple[str, str, str]:
    """Разбирает тег зарплаты."""
    min_wage: str = 'Не указано'
    max_wage: str = 'Не указано'
    currency: str = 'Не указано'
    salary: str
    wage_span: Any = vacancy.find('span', class_='bloko-header-section-3')
    if wage_span is not None:
        wage: str = wage_span.text
        salary, currency = wage.rsplit(maxsplit=1)
        if re.search(r'\d+\s\W\s\d+', salary, flags=re.I) is not None:
            min_wage = ''.join(salary.split()[:2])
            max_wage = ''.join(salary.split()[-2:])
        else:
            if 'от' in salary:
                min_wage = ''.join(salary.split()[1:3])
            if 'до' in salary:
                max_wage = ''.join(salary.split()[-2:])
    return min_wage, max_wage, currency


def parse_vacancy(vacancies_list: List[Any], base_url: str,
                  satisfy_list: List[Dict[str, str]]) -> Tuple[int, List[Dict[str, str]]]:
    """Просматривает вакансии."""
    n: int = 0
    min_wage: str
    max_wage: str
    currency: str
    satisfied_vacancy: Dict[str, str] = {}
    vacancy: Any
    for vacancy in vacancies_list:
        n += 1
        town_text: str = vacancy.find('div', attrs={'class': 'bloko-text',
                                               'data-qa': "vacancy-serp__vacancy-address"}).text
        duty_require: List[str] = get_preferences(vacancy)
        find_towns: List[str] = ['Москва', 'Санкт-Петербург']
        find_skills: List[str] = ['Django', 'Flask']
        # find_skills: List[str] = ['Pandas', 'Numpy']      # Вариант для тестирования.
        town: str = 'Не указано'
        if is_include(find_towns[0], town_text):
            town = find_towns[0]
        elif is_include(find_towns[1], town_text):
            town = find_towns[1]

        #   Проверяет, что выбрался один из указанных городов. И в то же время, что оба навыка,
        #   и "Django" и "Flask", одновременно, встречаются в описаниях либо должностных
        #   обязанностей, либо требований к кондидатам. Если город не подошёл, или одно из
        #   навыков ("Django" или "Flask") не востребовано, то вакансия игнорируется.
        if (town != 'Не указано' and is_include(find_skills[0], *duty_require)
                and is_include(find_skills[1], *duty_require)):
            #       Сохраняет информацию о текущей вакансии.
            vacancy_href: str = 'Не указано'
            # vacancy_name: str = 'Не указано'  # Можно добавить.
            vacancy_a: Any = vacancy.find('a', class_='serp-item__title')
            if vacancy_a is not None:
                vacancy_href = base_url + vacancy_a['href']
                # vacancy_name = vacancy_a.text  # Можно добавить.
            company_name: str = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text
            min_wage, max_wage, currency = get_wage(vacancy)
            satisfied_vacancy.clear()
            satisfied_vacancy = {
                'vacancy_href': vacancy_href,          # Ссылка на вакансию.
                'min_wage': min_wage,                  # Нижняя граница зарплаты.
                'max_wage': max_wage,                  # Верхняя граница зарплаты.
                'company_name': company_name,          # Название компании.
                'town': town                           # Город.
            }                        # Можно добавить:
            #     'vacancy_name': vacancy_name,        # Название вакансии.
            #     'currency': currency,                # Денежная валюта.
            #     'job_duties': duty_require[0],       # Должностные обязанности.
            #     'requirements': duty_require[1]      # Требования к кондидату.

            satisfy_list.append(satisfied_vacancy)
    return n, satisfy_list
