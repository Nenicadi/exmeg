import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
import os
from datetime import datetime

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("800x600")
        
        # Предопределенные цитаты
        self.default_quotes = [
            {"text": "Будьте собой, все остальные роли уже заняты.", "author": "Оскар Уайльд", "theme": "жизнь"},
            {"text": "Жизнь — это то, что происходит с вами, пока вы строите другие планы.", "author": "Джон Леннон", "theme": "жизнь"},
            {"text": "Успех — это способность переходить от одной неудачи к другой, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "успех"},
            {"text": "Единственный способ делать великие дела — это любить то, что вы делаете.", "author": "Стив Джобс", "theme": "работа"},
            {"text": "Знание — сила.", "author": "Фрэнсис Бэкон", "theme": "знания"},
            {"text": "Лучшее время посадить дерево было 20 лет назад. Второе лучшее время — сегодня.", "author": "Китайская пословица", "theme": "мотивация"},
            {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "theme": "творчество"},
            {"text": "Не важно, как медленно вы идете, до тех пор, пока вы не остановитесь.", "author": "Конфуций", "theme": "мотивация"},
            {"text": "Сложнее всего начать действовать, всё остальное зависит только от упорства.", "author": "Амелия Эрхарт", "theme": "мотивация"},
            {"text": "Вдохновение существует, но оно должно застать вас за работой.", "author": "Пабло Пикассо", "theme": "творчество"}
        ]
        
        # Загрузка истории из JSON
        self.history = self.load_history()
        if not self.history:
            self.history = self.default_quotes.copy()
            self.save_history()
        
        # Выпадающие списки для фильтрации
        self.authors = sorted(set(quote["author"] for quote in self.history))
        self.themes = sorted(set(quote["theme"] for quote in self.history))
        
        self.setup_ui()
    
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Секция генерации цитаты
        quote_frame = ttk.LabelFrame(main_frame, text="Случайная цитата", padding="10")
        quote_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.quote_text = scrolledtext.ScrolledText(quote_frame, height=4, width=70, wrap=tk.WORD)
        self.quote_text.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.author_label = ttk.Label(quote_frame, text="Автор: ")
        self.author_label.grid(row=1, column=0, sticky=tk.W)
        
        self.theme_label = ttk.Label(quote_frame, text="Тема: ")
        self.theme_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Button(quote_frame, text="🎲 Сгенерировать цитату", 
                  command=self.generate_random_quote).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Секция добавления новой цитаты
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую цитату", padding="10")
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(add_frame, text="Цитата:").grid(row=0, column=0, sticky=tk.W)
        self.new_quote_text = tk.Text(add_frame, height=3, width=50, wrap=tk.WORD)
        self.new_quote_text.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        ttk.Label(add_frame, text="Автор:").grid(row=2, column=0, sticky=tk.W)
        self.new_author_entry = ttk.Entry(add_frame, width=30)
        self.new_author_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(add_frame, text="Тема:").grid(row=3, column=0, sticky=tk.W)
        self.new_theme_entry = ttk.Entry(add_frame, width=30)
        self.new_theme_entry.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        ttk.Button(add_frame, text="➕ Добавить цитату", 
                  command=self.add_quote).grid(row=4, column=0, columnspan=2)
        
        # Секция фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="По автору:").grid(row=0, column=0, padx=(0, 10))
        self.author_filter = ttk.Combobox(filter_frame, values=["Все"] + self.authors, state="readonly")
        self.author_filter.set("Все")
        self.author_filter.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(filter_frame, text="По теме:").grid(row=0, column=2, padx=(0, 10))
        self.theme_filter = ttk.Combobox(filter_frame, values=["Все"] + self.themes, state="readonly")
        self.theme_filter.set("Все")
        self.theme_filter.grid(row=0, column=3)
        
        ttk.Button(filter_frame, text="🔍 Применить фильтр", 
                  command=self.apply_filters).grid(row=0, column=4, padx=(20, 0))
        
        # Секция истории
        history_frame = ttk.LabelFrame(main_frame, text="История цитат", padding="10")
        history_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.history_listbox = tk.Listbox(history_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления историей
        button_frame = ttk.Frame(history_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔄 Обновить список", 
                  command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Удалить выбранное", 
                  command=self.delete_selected).pack(side=tk.LEFT)
        
        # Конфигурация grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Начальное заполнение истории
        self.refresh_history()
    
    def generate_random_quote(self):
        if not self.history:
            messagebox.showwarning("Предупреждение", "Нет доступных цитат!")
            return
        
        quote = random.choice(self.history)
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(1.0, quote["text"])
        self.author_label.config(text=f"Автор: {quote['author']}")
        self.theme_label.config(text=f"Тема: {quote['theme']}")
    
    def add_quote(self):
        text = self.new_quote_text.get(1.0, tk.END).strip()
        author = self.new_author_entry.get().strip()
        theme = self.new_theme_entry.get().strip()
        
        # Проверка на пустые строки
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        if not theme:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return
        
        # Добавление цитаты
        new_quote = {
            "text": text,
            "author": author,
            "theme": theme
        }
        
        self.history.append(new_quote)
        self.save_history()
        
        # Обновление списков авторов и тем
        self.authors = sorted(set(quote["author"] for quote in self.history))
        self.themes = sorted(set(quote["theme"] for quote in self.history))
        self.author_filter["values"] = ["Все"] + self.authors
        self.theme_filter["values"] = ["Все"] + self.themes
        
        # Очистка полей ввода
        self.new_quote_text.delete(1.0, tk.END)
        self.new_author_entry.delete(0, tk.END)
        self.new_theme_entry.delete(0, tk.END)
        
        self.refresh_history()
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")
    
    def apply_filters(self):
        selected_author = self.author_filter.get()
        selected_theme = self.theme_filter.get()
        
        self.refresh_history(author_filter=selected_author, theme_filter=selected_theme)
    
    def refresh_history(self, author_filter="Все", theme_filter="Все"):
        self.history_listbox.delete(0, tk.END)
        
        filtered_quotes = self.history
        
        if author_filter != "Все":
            filtered_quotes = [q for q in filtered_quotes if q["author"] == author_filter]
        
        if theme_filter != "Все":
            filtered_quotes = [q for q in filtered_quotes if q["theme"] == theme_filter]
        
        for i, quote in enumerate(filtered_quotes, 1):
            self.history_listbox.insert(tk.END, f"{i}. \"{quote['text'][:50]}...\" - {quote['author']} [{quote['theme']}]")
    
    def delete_selected(self):
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите цитату для удаления!")
            return
        
        # Получаем текущий фильтр
        selected_author = self.author_filter.get()
        selected_theme = self.theme_filter.get()
        
        # Получаем отфильтрованный список
        filtered_quotes = self.history
        if selected_author != "Все":
            filtered_quotes = [q for q in filtered_quotes if q["author"] == selected_author]
        if selected_theme != "Все":
            filtered_quotes = [q for q in filtered_quotes if q["theme"] == selected_theme]
        
        # Находим и удаляем цитату из основного списка
        quote_to_delete = filtered_quotes[selection[0]]
        self.history.remove(quote_to_delete)
        self.save_history()
        
        # Обновление списков
        self.authors = sorted(set(quote["author"] for quote in self.history))
        self.themes = sorted(set(quote["theme"] for quote in self.history))
        self.author_filter["values"] = ["Все"] + self.authors
        self.theme_filter["values"] = ["Все"] + self.themes
        
        self.refresh_history(author_filter=selected_author, theme_filter=selected_theme)
        messagebox.showinfo("Успех", "Цитата удалена!")
    
    def save_history(self):
        try:
            with open("quotes_history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
    
    def load_history(self):
        try:
            if os.path.exists("quotes_history.json"):
                with open("quotes_history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

def main():
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()