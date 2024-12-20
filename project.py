import csv
import os
import json


class PriceMachine:

    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 25  # Устанавливаем максимальную длину названия товара для выравнивания в таблице

    def load_prices(self, file_path='dir_price'):
        """
        Сканирует указанный каталог. Ищет файлы со словом 'price' в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        Допустимые названия для столбца с товаром:
            товар
            название
            наименование
            продукт
        Допустимые названия для столбца с ценой:
            розница
            цена
        Допустимые названия для столбца с весом (в кг.):
            вес
            масса
            фасовка
        """

        # Сканируем каталог и находим файлы с нужным именем
        files = [os.path.join(file_path, f) for f in os.listdir(file_path) if 'price' in f and f.endswith('.csv')]

        for file in files:
            with open(file, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                headers = next(reader)
                product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)

                for row in reader:
                    if row[product_idx] and row[price_idx] and row[weight_idx]:
                        product_name = row[product_idx].strip()
                        try:
                            price = float(row[price_idx].strip())
                            weight = float(row[weight_idx].strip())
                            price_per_kg = price / weight

                            # Обновляем максимальную длину названия товара
                            self.name_length = max(len(product_name), self.name_length)

                            self.data.append({
                                'product_name': product_name,
                                'price': price,
                                'weight': weight,
                                'file': file,
                                'price_per_kg': price_per_kg
                            })
                        except ValueError:
                            print(f"Ошибка преобразования значения в строке файла {file}: {row}")

    def _search_product_price_weight(self, headers):
        """
        Возвращает индексы столбцов с названием товара, ценой и весом.
        """
        product_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']

        product_idx = next(i for i, h in enumerate(headers) if h.lower() in product_columns)
        price_idx = next(i for i, h in enumerate(headers) if h.lower() in price_columns)
        weight_idx = next(i for i, h in enumerate(headers) if h.lower() in weight_columns)

        return product_idx, price_idx, weight_idx

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML-файл.
        """
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for idx, item in enumerate(sorted(self.data, key=lambda x: x['price_per_kg'])):
            result += f'''
                        <tr>
                            <td>{idx + 1}</td>
                            <td>{item['product_name'][:self.name_length]:<{self.name_length}}</td>
                            <td>{item['price']:.2f}</td>
                            <td>{item['weight']:.2f}</td>
                            <td>{os.path.basename(item['file'])}</td>
                            <td>{item['price_per_kg']:.2f}</td>
                        </tr>
                    '''
        result += '''
                    </table>
                </body>
                </html>
                '''
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)

    def find_text(self, search_text: str):
        """
        Поиск товаров по частичному совпадению названия.
        """
        results = [
            item for item in self.data
            if search_text.lower() in item['product_name'].lower()
        ]

        return sorted(results, key=lambda x: x['price_per_kg'])


# Основной блок программы
if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices('dir_price')

    while True:
        user_input = input("Введите текст для поиска или 'exit' для завершения: ").strip().lower()

        if user_input == 'exit':
            print("Работа завершена.")
            pm.export_to_html()
            break

        results = pm.find_text(user_input)

        if results:
            for i, result in enumerate(results, start=1):
                print(
                    f"{i:>3}. {result['product_name'][:pm.name_length]:<{pm.name_length}} {result['price']:>10.2f} {result['weight']:>5.2f} {os.path.basename(result['file']):<20} {result['price_per_kg']:>10.2f}")
        else:
            print("Товары не найдены.")