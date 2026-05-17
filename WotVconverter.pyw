import sys

try:
    import customtkinter as ctk
    import ctypes
    try:
        # Фикс размытия шрифтов на Windows
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except Exception:
        pass
except Exception as startup_error:
    print(f"\n[КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА]: {startup_error}")
    input("\nНажмите Enter для выхода...")
    sys.exit(1)


class WoTLiveCalculatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Калькулятор валют World of Tanks")
        self.geometry("520x820") 
        self.resizable(False, False)

        self.is_calculating = False
        self.current_lang = "RU"
        self.current_region = "LESTA" # Регион по умолчанию

        # Игровые курсы и экономика ресурсы
        self.CREDITS_PER_GOLD = 400
        self.BASE_EXP_PER_GOLD = 25
        self.PROMO_EXP_PER_GOLD = 35
        self.EUR_PER_GOLD = 0.0036  
        self.BOX_PRICE_RU = 39.0

        # Сетка цен на коробки для EU (количество: цена в EUR)
        self.BOX_PRICES_EU = [
            (230, 264.86),
            (120, 146.78),
            (80, 103.65),
            (30, 40.15),
            (5, 6.83)
        ]

        self.text_dict = {
            "RU": {
                "title": "WoT Currency Converter",
                "promo_title": "Игровые акции и скидки:",
                "switch_exp": "Акция на свободный опыт (1 к 35 вместо 1 к 25)",
                "switch_discount": "Скидка 15% во внутриигровом магазине",
                "label_gold": "Или введите количество Золота (Gold):",
                "label_exp": "Или введите количество Свободного опыта (Free XP):",
                "res_gold_fmt": "🪙 Золото: {}",
                "res_credits_fmt": "🥈 Кредиты (серебро): {}",
                "res_exp_fmt": "⭐ Свободный опыт: {}",
                "res_prem_fmt": "📅 Премиум-аккаунт: {} дней",
                "placeholder": "Например: ",
                "error": "Ошибка: вводите только числа!"
            },
            "EN": {
                "title": "WoT Currency Converter",
                "promo_title": "In-game Special Offers & Discounts:",
                "switch_exp": "Free XP Special Offer (1 to 35 instead of 1 to 25)",
                "switch_discount": "15% Discount in the Premium Shop",
                "label_gold": "Or enter Gold amount:",
                "label_exp": "Or enter Free XP amount:",
                "res_gold_fmt": "🪙 Gold: {}",
                "res_credits_fmt": "🥈 Credits (Silver): {}",
                "res_exp_fmt": "⭐ Free XP: {}",
                "res_prem_fmt": "📅 Premium Account: {} days",
                "placeholder": "e.g., ",
                "error": "Error: enter numbers only!"
            }
        }

        self.create_widgets()
        self.setup_bindings()
        self.update_ui_language()

    def get_rub_cost_by_gold(self, gold):
        """ Расчет стоимости доната в рублях с прогрессивной скидкой """
        if gold <= 0: return 0
        if gold <= 100: return gold * 0.16
        elif gold <= 500: return 16 + (gold - 100) * (62 / 400)
        else: return gold * 0.156

    def get_gold_by_rub(self, rub):
        """ Обратный расчет золота на основе внесенных рублей """
        if rub <= 0: return 0
        if rub <= 16: return rub / 0.16
        elif rub <= 78: return 100 + (rub - 16) / (62 / 400)
        else: return rub / 0.156

    def calculate_eu_boxes_cost(self, count):
        """ Жадный алгоритм подбора оптимальных пакетов коробок для EU """
        if count <= 0: return 0, "0"
        total_cost, remaining, combination = 0, count, []
        for box_pack, price in self.BOX_PRICES_EU:
            if remaining >= box_pack:
                packs_count = remaining // box_pack
                total_cost += packs_count * price
                remaining = remaining % box_pack
                combination.append(f"{packs_count}x{box_pack}")
        if remaining > 0:
            total_cost += remaining * (6.83 / 5)
            combination.append(f"{remaining}x Singles")
        return total_cost, " + ".join(combination)
    def create_widgets(self):
        # Панель переключателей (Язык + Регион) в правом верхнем углу
        self.frame_top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top_bar.pack(anchor="ne", padx=20, pady=5)
        
        # Тумблер языка
        self.switch_lang = ctk.CTkSwitch(self.frame_top_bar, text="Language: RU", font=("Arial", 11, "bold"), command=self.toggle_language)
        self.switch_lang.pack(side="right", padx=5)

        # Новый тумблер региона
        self.switch_region = ctk.CTkSwitch(self.frame_top_bar, text="Region: LESTA", font=("Arial", 11, "bold"), command=self.toggle_region)
        self.switch_region.pack(side="right", padx=5)

        # Заголовок
        self.label_title = ctk.CTkLabel(self, text="", font=("Arial", 24, "bold"), text_color="#ff7f00")
        self.label_title.pack(pady=5)

        # Переключатели акций
        self.frame_switches = ctk.CTkFrame(self)
        self.frame_switches.pack(pady=10, padx=20, fill="x")

        self.label_promo = ctk.CTkLabel(self.frame_switches, text="", font=("Arial", 14, "bold"))
        self.label_promo.pack(anchor="w", padx=10, pady=5)

        self.switch_exp = ctk.CTkSwitch(self.frame_switches, text="", font=("Arial", 12), command=self.trigger_recalc)
        self.switch_exp.pack(anchor="w", padx=20, pady=5)

        self.switch_discount = ctk.CTkSwitch(self.frame_switches, text="", font=("Arial", 12), command=self.trigger_recalc)
        self.switch_discount.pack(anchor="w", padx=20, pady=5)

        # Поля ввода ресурсов
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(pady=10, padx=20, fill="x")

        self.label_money = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_money.pack(anchor="w", padx=10, pady=2)
        self.entry_money = ctk.CTkEntry(self.frame_input)
        self.entry_money.pack(fill="x", padx=10, pady=5)

        self.label_gold = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_gold.pack(anchor="w", padx=10, pady=2)
        self.entry_gold = ctk.CTkEntry(self.frame_input)
        self.entry_gold.pack(fill="x", padx=10, pady=5)

        self.label_exp = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_exp.pack(anchor="w", padx=10, pady=2)
        self.entry_exp = ctk.CTkEntry(self.frame_input)
        self.entry_exp.pack(fill="x", padx=10, pady=5)

        # Блок коробок
        self.frame_boxes = ctk.CTkFrame(self)
        self.frame_boxes.pack(pady=10, padx=20, fill="x")
        
        self.label_boxes_title = ctk.CTkLabel(self.frame_boxes, text="", font=("Arial", 13, "bold"), text_color="#00efff")
        self.label_boxes_title.pack(anchor="w", padx=10, pady=2)
        self.entry_boxes = ctk.CTkEntry(self.frame_boxes)
        self.entry_boxes.pack(fill="x", padx=10, pady=5)

        # Блок результатов
        self.frame_results = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_results.pack(pady=10, padx=20, fill="both", expand=True)

        self.result_money_needed = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14, "bold"), text_color="#00ff00")
        self.result_money_needed.pack(anchor="w", padx=15, pady=5)

        self.result_boxes_cost = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 13, "bold"), text_color="#00efff")
        self.result_boxes_cost.pack(anchor="w", padx=15, pady=5)

        self.result_gold = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14))
        self.result_gold.pack(anchor="w", padx=15, pady=5)

        self.result_credits = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14))
        self.result_credits.pack(anchor="w", padx=15, pady=5)

        self.result_exp = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14))
        self.result_exp.pack(anchor="w", padx=15, pady=5)

        self.result_prem = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14))
        self.result_prem.pack(anchor="w", padx=15, pady=5)

    def toggle_language(self):
        self.current_lang = "EN" if self.switch_lang.get() == 1 else "RU"
        self.switch_lang.configure(text=f"Language: {self.current_lang}")
        self.update_ui_language()
        self.trigger_recalc()

    def toggle_region(self):
        self.current_region = "WG" if self.switch_region.get() == 1 else "LESTA"
        self.switch_region.configure(text=f"Region: {self.current_region}")
        
        # Очищаем все поля при смене региона для избежания путаницы с валютами
        self.entry_money.delete(0, 'end')
        self.entry_gold.delete(0, 'end')
        self.entry_exp.delete(0, 'end')
        self.entry_boxes.delete(0, 'end')
        
        self.update_ui_language()
        self.trigger_recalc()

    def update_ui_language(self):
        lang = self.current_lang
        region = self.current_region
        data = self.text_dict[lang]

        self.label_title.configure(text=data["title"])
        self.label_promo.configure(text=data["promo_title"])
        self.switch_exp.configure(text=data["switch_exp"])
        self.switch_discount.configure(text=data["switch_discount"])
        self.label_gold.configure(text=data["label_gold"])
        self.label_exp.configure(text=data["label_exp"])
        
        # Локализация полей в зависимости от региона
        if region == "LESTA":
            self.label_money.configure(text="Введите сумму в рублях (RUB):" if lang == "RU" else "Enter amount in Rubles (RUB):")
            self.label_boxes_title.configure(text="Введите количество контейнеров «Зов сокола»:" if lang == "RU" else "Enter number of Falcon Boxes:")
            self.entry_money.configure(placeholder_text=data["placeholder"] + "1000")
            self.entry_boxes.configure(placeholder_text=data["placeholder"] + "30")
        else:
            self.label_money.configure(text="Введите сумму в Евро (EUR):" if lang == "RU" else "Enter amount in Euro (EUR):")
            self.label_boxes_title.configure(text="Введите количество Коробок события:" if lang == "RU" else "Enter number of Event Boxes:")
            self.entry_money.configure(placeholder_text=data["placeholder"] + "10")
            self.entry_boxes.configure(placeholder_text=data["placeholder"] + "80")

        self.entry_gold.configure(placeholder_text=data["placeholder"] + "2500")
        self.entry_exp.configure(placeholder_text=data["placeholder"] + "100000")

        if not self.entry_money.get() and not self.entry_gold.get() and not self.entry_exp.get() and not self.entry_boxes.get():
            self.clear_results()

    def setup_bindings(self):
        self.entry_money.bind("<KeyRelease>", lambda event: self.live_calculate("money"))
        self.entry_gold.bind("<KeyRelease>", lambda event: self.live_calculate("gold"))
        self.entry_exp.bind("<KeyRelease>", lambda event: self.live_calculate("exp"))
        self.entry_boxes.bind("<KeyRelease>", lambda event: self.live_calculate("boxes"))
        
        self.bind("<Control-KeyPress>", self.global_ctrl_handler)
        self.last_edited = "money"

    def global_ctrl_handler(self, event):
        if event.keycode == 65 or event.keysym.lower() in ('a', 'ф'):
            focused_widget = self.focus_get()
            if focused_widget in (self.entry_money, self.entry_gold, self.entry_exp, self.entry_boxes):
                focused_widget.select_range(0, 'end')
                focused_widget.icursor('end')
                return "break"

    def trigger_recalc(self):
        self.live_calculate(self.last_edited, clear_others=False)

    def clear_results(self):
        lang = self.current_lang
        region = self.current_region
        
        currency = "руб." if region == "LESTA" else "EUR"
        
        if lang == "RU":
            self.result_money_needed.configure(text=f"💰 Стоимость доната: 0.00 {currency}")
            self.result_boxes_cost.configure(text=f"📦 Стоимость контейнеров: 0.00 {currency}" if region == "LESTA" else "📦 Стоимость коробок: 0.00 EUR")
        else:
            self.result_money_needed.configure(text=f"💰 Donation Cost: 0.00 {currency}")
            self.result_boxes_cost.configure(text=f"📦 Boxes Cost: 0.00 {currency}" if region == "LESTA" else "📦 Total Boxes Cost: 0.00 EUR")
            
        self.result_gold.configure(text=self.text_dict[lang]["res_gold_fmt"].format("0"))
        self.result_credits.configure(text=self.text_dict[lang]["res_credits_fmt"].format("0"))
        self.result_exp.configure(text=self.text_dict[lang]["res_exp_fmt"].format("0"))
        self.result_prem.configure(text=self.text_dict[lang]["res_prem_fmt"].format("0"))

    def live_calculate(self, source, clear_others=True):
        if self.is_calculating: return
        self.last_edited = source
        lang = self.current_lang
        region = self.current_region
        
        try:
            money_val = self.entry_money.get().strip()
            gold_val = self.entry_gold.get().strip()
            exp_val = self.entry_exp.get().strip()
            boxes_val = self.entry_boxes.get().strip()

            if (source == "money" and not money_val) or (source == "gold" and not gold_val) or \
               (source == "exp" and not exp_val) or (source == "boxes" and not boxes_val):
                self.clear_results()
                return

            self.is_calculating = True

            if clear_others:
                fields = {"money": self.entry_money, "gold": self.entry_gold, "exp": self.entry_exp, "boxes": self.entry_boxes}
                for name, entry in fields.items():
                    if name != source: entry.delete(0, 'end')

            exp_rate = self.PROMO_EXP_PER_GOLD if self.switch_exp.get() == 1 else self.BASE_EXP_PER_GOLD

            # Расчет коробок
            if source == "boxes" and boxes_val:
                box_count = int(boxes_val)
                if region == "LESTA":
                    cost_str = f"{(box_count * self.BOX_PRICE_RU):,.2f} руб.".replace(",", " ")
                    self.result_boxes_cost.configure(text=f"📦 Стоимость контейнеров: {cost_str}" if lang == "RU" else f"📦 Boxes Cost: {cost_str}")
                else:
                    box_cost, comb_str = self.calculate_eu_boxes_cost(box_count)
                    cost_str = f"{box_cost:,.2f} EUR".replace(",", " ")
                    self.result_boxes_cost.configure(text=f"📦 Стоимость коробок: {cost_str} (Комбинация: {comb_str})" if lang == "RU" else f"📦 Total Boxes Cost: {cost_str} (Combination: {comb_str})")
                
                # Обнуляем валютные строки
                self.is_calculating = False
                self.clear_results()
                # Но восстанавливаем правильную строчку коробок, чтобы она не сбросилась
                self.is_calculating = True
                return

            # Расчет валют и опыта
            if source == "money" and money_val:
                val = float(money_val)
                gold = self.get_gold_by_rub(val) if region == "LESTA" else val / self.EUR_PER_GOLD
            elif source == "gold" and gold_val:
                gold = float(gold_val)
            elif source == "exp" and exp_val:
                gold = float(exp_val) / exp_rate
            else:
                self.is_calculating = False
                return

            # Вычисляем стоимость в валюте региона
            if region == "LESTA":
                money_needed = self.get_rub_cost_by_gold(gold)
                money_str = f"{money_needed:,.2f} руб.".replace(",", " ")
            else:
                money_needed = gold * self.EUR_PER_GOLD
                money_str = f"{money_needed:,.2f} EUR".replace(",", " ")

            discount_factor = 0.85 if self.switch_discount.get() == 1 else 1.0
            credits = gold * self.CREDITS_PER_GOLD
            free_exp = gold * exp_rate
            prem_days = (gold / (2500 * discount_factor)) * 30

            # Вывод результатов
            if lang == "RU":
                self.result_money_needed.configure(text=f"💰 Стоимость доната: {money_str}")
            else:
                self.result_money_needed.configure(text=f"💰 Donation Cost: {money_str}")

            self.result_gold.configure(text=self.text_dict[lang]["res_gold_fmt"].format(f"{int(gold):,}".replace(",", " ")))
            self.result_credits.configure(text=self.text_dict[lang]["res_credits_fmt"].format(f"{int(credits):,}".replace(",", " ")))
            self.result_exp.configure(text=self.text_dict[lang]["res_exp_fmt"].format(f"{int(free_exp):,}".replace(",", " ")))
            self.result_prem.configure(text=self.text_dict[lang]["res_prem_fmt"].format(int(prem_days)))
            
            # Сбрасываем текст коробок при расчете валют
            currency_lbl = "руб." if region == "LESTA" else "EUR"
            self.result_boxes_cost.configure(text=f"📦 Стоимость контейнеров: 0.00 {currency_lbl}" if lang == "RU" else f"📦 Boxes Cost: 0.00 {currency_lbl}")

        except ValueError:
            self.clear_results()
            self.result_gold.configure(text=self.text_dict[lang]["error"])
        finally:
            self.is_calculating = False


if __name__ == "__main__":
    try:
        app = WoTLiveCalculatorGUI()
        app.mainloop()
    except Exception as run_error:
        print(f"\n[ОШИБКА]: {run_error}")
        input("\nНажмите Enter для выхода...")
