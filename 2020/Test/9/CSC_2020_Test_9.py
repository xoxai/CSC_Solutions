import re

# используемые имена числительных и их составляющих
data = ["100 сто",
        "200 двести",
        "300 триста",
        "400 четыреста",
        "500 пятьсот",
        "600 шестьсот",
        "700 семьсот",
        "800 восемьсот",
        "900 девятьсот",
        "10 десять",
        "11 одиннадцать",
        "12 двенадцать",
        "13 тринадцать",
        "14 четырнадцать",
        "15 пятнадцать",
        "16 шестнадцать",
        "17 семнадцать",
        "18 восемнадцать",
        "19 девятнадцать",
        "20 двадцать",
        "30 тридцать",
        "40 сорок",
        "50 пятьдесят",
        "60 шестьдесят",
        "70 семьдесят",
        "80 восемьдесят",
        "90 девяносто",
        "1 одна",
        "2 две",
        "3 три",
        "4 четыре",
        "5 пять",
        "6 шесть",
        "7 семь",
        "8 восемь",
        "9 девять"]

### генерация вспомогательных элементов ###

# создадим словарь для входных и выходных числительных
# они будут отличаться только родом, поскольку миля -- ж.р., а километр - м.р.
nd_input, nd_output = {}, {}

for s in data:
    element = s.split(' ')
    nd_input[element[1]] = int(element[0])

# входной и выходной словари будут очень похожи
nd_output = nd_input

# числительные, на которые влияет род слова -- это только 1 и 2
# поэтому заменим их в выходном словаре
# предварительно поменяв при этом местами ключи и значения словаря
nd_output = {key: value for value, key in nd_output.items()}
# обратный словарь для миль
nd_input_inverted = {key: value for value, key in nd_input.items()}
nd_output[1] = 'один'
nd_output[2] = 'два'


def get_miles(s, context_width=3):
    """
    parameters:
        s -- input sentence

    returns:
        number of miles contains in sentence
    """

    # формы слова "миля" для поиска
    mileword = ["миля", "мили", "миль"]

    # регулярным выражением избавляемся от знаков препинания
    # ищем только по строчным буквам, потому что гарантируется, что предложение
    # не начинается с числительного
    splitted = re.findall("[а-я]+", s)
    number_of_miles = 0
    # пробегаемся по каждому слову в предложении
    for index, word in enumerate(splitted):
        # среди всех формослов слова "миля"
        for mile in mileword:
            # если формослова найдена, смотрим контекст вокруг него
            # мы используем функцию find, поэтому ищутся и
            if (word.find(mile) != -1):
                miles_wordform = mile
                """
                Предположим, что числительное может быть как справа от словоформы, так и слева от неё
                поскольку максимальная длина числительного здесь -- 3 слова, то шагаем влево-вправо
                на 3 слова и смотрим их на вхождение в словарь наших числительных как ключей
                
                P.S. Вообще, этот подход не универсальный, потому что не учитывает случаи, 
                когда числительное отстоит от единицы измерения на более, чем три слова, например:
                мы прошли миль этак двести тридцать семь -- на таком примере алгоритм вернёт 230 вместо 237,
                но это легко решается увеличением ширины учитываемых слева-справа слов (параметр context_width)
                """
                # для просмотра контекста раскомментируй следующую строку
                # print("context", splitted[index-context_width:index+context_width+1])
                for numword in splitted[index-context_width:index+context_width+1]:
                    if numword in nd_input.keys():
                        # splitted.remove(numword)
                        number_of_miles += nd_input[numword]
                # прерываем цикл как только найдена одна словоформа "мили",
                # поскольку в условии гарантировано одно её вхождение
                break
    return number_of_miles, miles_wordform


def word_form(number, word="километр"):
    """
    parameters:
        word   -- normal form of the word
        number -- numeral to satisfy

    returns:
        word form satisfying input number

    principle:
        if last_two_digits in interval [10, 19], returns "ов"
        else look for last_digit and returns:
            "ов" if last_digit in [5, 9]
            "а"  if last_digit in [2, 4]
            ""   if last_digit in {1}

    limitations:
        works only for words in masculin gender ended by consonants
    """

    last_two_digits = number % 100

    if last_two_digits in range(11, 20):
        word_end = "ов"
    else:
        last_digit = last_two_digits % 10
        if last_digit in [0] + list(range(5, 10)):
            word_end = "ов"
        elif last_digit in range(2, 5):
            word_end = "а"
        else:
            word_end = ""

    return word + word_end


def get_digits(number):
    """
    parameters:
        number -- input number

    returns:
        list of digits of a given number
    """

    digits = []

    for i in range(len(str(number))):
        digit = number % 10
        digits.append(digit)
        number //= 10

    digits.reverse()

    return digits


def num2word(number, dictionary=nd_output):
    """
    parameters:
        number     -- number to decode
        dictionary -- dictionary contains needed word forms

    returns:
        sentence contains word form of input numeral

    principle:


    limitations:
        works only for numbers smaller than 1k
    """

    num_len = len(str(number))
    output = []

    digits = get_digits(number)
    last_two = int(''.join(str(x) for x in digits[num_len-2:]))

    # проверим, образуют ли последние две цифры числа самостоятельное числительное
    if last_two in list(range(10, 100, 10)) + list(range(11, 20)):
        output.append(dictionary[last_two])
    # в противном случае соберём его из составляющих
    else:
        for i, d in enumerate(digits[num_len-2:]):
            if d != 0:
                output.append(dictionary[d * 10 ** (1-i)])

    # обработаем оставшиеся цифры числа
    for i, d in enumerate(digits[:num_len-2]):
        output = [dictionary[d * 10 ** (num_len-(i+1))]] + output

    return ' '.join(output)


def miles2km(miles):
    """
    parameters:
        miles -- distance in miles

    returns:
        kilometers (int) -- distance in kilometers

    principle:
        multiplying by constant
    """

    c = 1.60934

    return round(miles * c)


def make_replace(s):
    s_info = get_miles(s)

    miles_num, miles_wordform = s_info[0], s_info[1]
    # для миль преобразование делаем с использованием своего словаря
    # поскольку "километр" и "миля" разных родов
    # и прошлый вариант кода не работал бы для примеров,
    # содержащих склоняемые числительные типа один/одна и два/две
    miles_words = num2word(miles_num, dictionary=nd_input_inverted)
    miles = miles_words + " " + miles_wordform

    km_num = miles2km(miles_num)
    km_wordform = word_form(km_num)
    km_words = num2word(km_num)
    km = km_words + " " + km_wordform

    return s.replace(miles, km)


print(make_replace(input()))
