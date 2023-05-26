import tkinter as tk
from tkinter import filedialog
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import io


class HypothesisTester:
    def __init__(self):
        self.data = None
        self.mean = None
        self.std_dev = None
        self.median = None
        self.alpha = None  # Переменная alpha для уровня значимости
        self.figure = None
        self.canvas = None

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.calculate_statistics()
                self.display_statistics()
            except pd.errors.EmptyDataError:
                self.show_message("Error", "Выбранный файл пуст.")
            except pd.errors.ParserError:
                self.show_message("Error", "Не удалось проанализировать выбранный файл.")
        else:
            self.show_message("Error", "Файл не выбран.")

    def calculate_statistics(self):
        self.mean = self.data.mean()
        self.std_dev = self.data.std()
        self.median = self.data.median()

    def display_statistics(self):
        name1 = "1 группа"
        mean_str = "Среднее значение: {:.2f}".format(self.mean.iloc[0])
        std_dev_str = "Стандартное отклонение: {:.2f}".format(self.std_dev.iloc[0])
        median_str = "Медиана: {:.2f}".format(self.median.iloc[0])

        name2 = "2 группа"
        mean_str2 = "Среднее значение: {:.2f}".format(self.mean.iloc[1])
        std_dev_str2 = "Стандартное отклонение: {:.2f}".format(self.std_dev.iloc[1])
        median_str2 = "Медиана: {:.2f}".format(self.median.iloc[1])

        message = f"{name1}\n{mean_str}\n{std_dev_str}\n{median_str}\n\n" \
                  f"{name2}\n{mean_str2}\n{std_dev_str2}\n{median_str2}"
        self.show_message("Статистика", message)

    def ansari_bradley_test(self):
        if self.data is None:
            self.show_message("Error", "Данные недоступны.")
            return

        data_group1 = self.data.iloc[:, 0]
        data_group2 = self.data.iloc[:, 1]

        try:
            stat, p_value = stats.ansari(data_group1, data_group2)
            self.alpha = float(self.alpha_entry.get())  # Set the value of alpha

            result = self.get_hypothesis_result(p_value)
            message = f"Статистика Ансари-Бредли: {stat}\nP-значение: {p_value}\nРезультат: {result}"
            self.show_message("Проверка гипотезы", message)

            # Вывод графика распределения данных
            plt.figure(figsize=(8, 6))
            plt.hist(data_group1, bins=20, color='lightblue', alpha=0.5, label='Группа 1', edgecolor='black')
            plt.hist(data_group2, bins=20, color='lightgreen', alpha=0.5, label='Группа 2', edgecolor='black')
            plt.xlabel('Значение')
            plt.ylabel('Частота')
            plt.title('Распределение данных')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)

            plt.show()

        except Exception as e:
            self.show_message("Error", str(e))

    def get_hypothesis_result(self, p_value):
        alpha = self.alpha_entry.get()
        if not alpha:
            return "Не задан уровень значимости"
        try:
            alpha = float(alpha)
            if alpha <= 0 or alpha >= 1:  # Добавлено условие для проверки корректности значения alpha
                return "Некорректное значение альфа"
            else:
                return "Гипотеза принята"
        except ValueError:
            return "Некорректное значение альфа"

    def save_results(self):
        if self.data is None:
            self.show_message("Error", "Данные недоступны.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                result_df = pd.DataFrame({
                    "Статистические данные": ["Среднее значение", "Стандартное отклонение", "Медиана"],
                    "Группа 1": [self.mean.iloc[0], self.std_dev.iloc[0], self.median.iloc[0]],
                    "Группа 2": [self.mean.iloc[1], self.std_dev.iloc[1], self.median.iloc[1]]
                })
                result_df.to_csv(file_path, index=False)
                self.show_message("Success", "Результаты успешно сохранены в табличном формате.")
            except Exception as e:
                self.show_message("Error", str(e))

    def show_message(self, title, message):
        window = tk.Toplevel()
        window.title(title)
        label = tk.Label(window, text=message, padx=20, pady=20)
        label.pack()

    def open_file_dialog(self):
        self.import_data()

    def create_gui(self):
        root = tk.Tk()
        root.title("Тест Ансари-Брэдли")
        root.geometry("300x300")

        root.configure(bg="lightgray")
        button_font = ("Arial", 10)

        import_button = tk.Button(root, text="Импорт данных", font=button_font, command=self.open_file_dialog, bg="LightBlue")
        import_button.pack(pady=10)

        self.alpha_label = tk.Label(root, text="Уровень значимости (альфа):", font=button_font, bg="LightGray")
        self.alpha_label.pack(pady=5, padx=10)

        self.alpha_entry = tk.Entry(root, font=button_font)
        self.alpha_entry.pack(pady=5, padx=10)
        self.alpha_entry.insert(0, "0.05")

        run_test_button = tk.Button(root, text="Выполнить тест гипотезы", font=button_font, command=self.ansari_bradley_test, bg="Beige")
        run_test_button.pack(pady=10)

        save_results_button = tk.Button(root, text="Сохранить результаты .csv", font=button_font, command=self.save_results, bg="LightGreen")
        save_results_button.pack(pady=10)

        save_text_button = tk.Button(root, text="Сохранить результаты .txt", command=self.save_results_as_text,
                                     bg="LightGreen", fg="black", font=("Arial", 10))
        save_text_button.pack(pady=10, padx=10)

        root.mainloop()

    def save_results_as_text(self):
        if self.data is None:
            self.show_message("Error", "Данные недоступны.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                result_text = f"1 группа:\nСреднее значение: {self.mean.iloc[0]}\nСтандартное отклонение: " \
                              f"{self.std_dev.iloc[0]}\nМедиана: {self.median.iloc[0]}\n\n"
                result_text += f"2 группа:\nСреднее значение: {self.mean.iloc[1]}\nСтандартное отклонение: " \
                               f"{self.std_dev.iloc[1]}\nМедиана: {self.median.iloc[1]}\n"

                with io.open(file_path, 'w', encoding='utf-8') as file:
                    file.write(result_text)

                self.show_message("Success", "Результаты успешно сохранены в текстовом формате.")
            except Exception as e:
                self.show_message("Error", str(e))


if __name__ == "__main__":
    tester = HypothesisTester()
    tester.create_gui()
