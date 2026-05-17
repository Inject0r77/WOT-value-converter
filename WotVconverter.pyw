import sys

try:
    import customtkinter as ctk
    import ctypes
    try:
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
        # Увеличили базовую высоту, чтобы новые поля в RU-версии смотрелись свободно
        self.geometry("520x820") 
        self.resizable(False, False)

        self.is_calculating = False
        self.current_lang = "RU"

        # Внутриигровые курсы ресурсов
        self.CREDITS_PER_GOLD = 400
        self.BASE_EXP_PER_GOLD = 25
        self.PROMO_EXP_PER_GOLD = 35
        self.EUR_PER_GOLD = 0.0036  

        # Сетка цен на коробки для EU (количество: цена в EUR)
        self.BOX_PRICES_EU = [
            (230, 264.86),
            (120, 146.78),
            (80, 103.65),
            (30, 40.15),
            (5, 6.83)
        ]
        
        # Стоимость коробок для RU ("Зов сокола"): 39 рублей за штуку
        self.BOX_PRICE_RU = 39.0

        self.text_dict = {
            "RU": {
                "title": "WoT Currency Converter",
                "promo_title": "Игровые акции и скидки:",
                "switch_exp": "Акция на свободный опыт (1 к 35 вместо 1 к 25)",
                "switch_discount": "Скидка 15% во внутриигровом магазине",
                "label_money": "Введите сумму в рублях (RUB):",
                "label_gold": "Или введите количество Золота (Gold):",
                "label_exp": "Или введите количество Свободного опыта (Free XP):",
                "res_money": "💰 Стоимость доната: 0 руб.",
                "res_money_fmt": "💰 Стоимость доната: {} руб.",
                "res_gold": "🪙 Золото: 0",
                "res_gold_fmt": "🪙 Золото: {}",
                "res_credits": "🥈 Кредиты (серебро): 0",
                "res_credits_fmt": "🥈 Кредиты (серебро): {}",
                "res_exp": "⭐ Свободный опыт: 0",
                "res_exp_fmt": "⭐ Свободный опыт: {}",
                "res_prem": "📅 Премиум-аккаунт: 0 дней",
                "res_prem_fmt": "📅 Премиум-аккаунт: {} дней",
                "placeholder": "Например: ",
                "error": "Ошибка: вводите только числа!",
                # Текст для RU коробок
                "boxes_label": "Введите количество контейнеров «Зов сокола»:",
                "boxes_res": "📦 Стоимость контейнеров: 0 руб.",
                "boxes_res_fmt": "📦 Стоимость контейнеров: {} руб."
            },
            "EN": {
                "title": "WoT Currency Converter",
                "promo_title": "In-game Special Offers & Discounts:",
                "switch_exp": "Free XP Special Offer (1 to 35 instead of 1 to 25)",
                "switch_discount": "15% Discount in the Premium Shop",
                "label_money": "Enter amount in Euro (EUR):",
                "label_gold": "Or enter Gold amount:",
                "label_exp": "Or enter Free XP amount:",
                "res_money": "💰 Donation Cost: 0.00 EUR",
                "res_money_fmt": "💰 Donation Cost: {} EUR",
                "res_gold": "🪙 Gold: 0",
                "res_gold_fmt": "🪙 Gold: {}",
                "res_credits": "🥈 Credits (Silver): 0",
                "res_credits_fmt": "🥈 Credits (Silver): {}",
                "res_exp": "⭐ Free XP: 0",
                "res_exp_fmt": "⭐ Free XP: {}",
                "res_prem": "📅 Premium Account: 0 days",
                "res_prem_fmt": "📅 Premium Account: {} days",
                "placeholder": "e.g., ",
                "error": "Error: enter numbers only!",
                # Текст для EU коробок
                "boxes_label": "Enter number of Boxes to buy:",
                "boxes_res": "📦 Total Boxes Cost: 0.00 EUR",
                "boxes_res_fmt": "📦 Total Boxes Cost: {} EUR (Combination: {})"
            }
        }

        self.create_widgets()
        self.setup_bindings()
        self.update_ui_language()

    def get_rub_cost_by_gold(self, gold):
        if gold <= 0:
            return 0
        if gold <= 100:
            return gold * 0.16
        elif gold <= 500:
            return 16 + (gold - 100) * (62 / 400)
        else:
            return gold * 0.156

    def get_gold_by_rub(self, rub):
        if rub <= 0:
            return 0
        if rub <= 16:
            return rub / 0.16
        elif rub <= 78:
            return 100 + (rub - 16) / (62 / 400)
        else:
            return rub / 0.156

    def calculate_eu_boxes_cost(self, count):
        """ Расчет комбинации пакетов коробок для EU """
        if count <= 0:
            return 0, "0"
        total_cost = 0
        remaining = count
        combination = []
        for box_pack, price in self.BOX_PRICES_EU:
            if remaining >= box_pack:
                packs_count = remaining // box_pack
                total_cost += packs_count * price
                remaining = remaining % box_pack
                combination.append(f"{packs_count}x{box_pack}")
        if remaining > 0:
            single_box_price = 6.83 / 5
            total_cost += remaining * single_box_price
            combination.append(f"{remaining}x Singles")
        return total_cost, " + ".join(combination)

    def create_widgets(self):
        # Панель переключения языка
        self.frame_lang = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_lang.pack(anchor="ne", padx=20, pady=5)
        
        self.switch_lang = ctk.CTkSwitch(self.frame_lang, text="Language: RU", font=("Arial", 11, "bold"), command=self.toggle_language)
        self.switch_lang.pack()

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

        self.label_rub = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_rub.pack(anchor="w", padx=10, pady=2)
        self.entry_rub = ctk.CTkEntry(self.frame_input)
        self.entry_rub.pack(fill="x", padx=10, pady=5)

        self.label_gold = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_gold.pack(anchor="w", padx=10, pady=2)
        self.entry_gold = ctk.CTkEntry(self.frame_input)
        self.entry_gold.pack(fill="x", padx=10, pady=5)

        self.label_exp = ctk.CTkLabel(self.frame_input, text="", font=("Arial", 12))
        self.label_exp.pack(anchor="w", padx=10, pady=2)
        self.entry_exp = ctk.CTkEntry(self.frame_input)
        self.entry_exp.pack(fill="x", padx=10, pady=5)

        # ДИНАМИЧЕСКИЙ БЛОК КОРОБОК (Теперь всегда на экране, меняет текст и логику)
        self.frame_boxes = ctk.CTkFrame(self)
        self.frame_boxes.pack(pady=10, padx=20, fill="x")
        
        self.label_boxes_title = ctk.CTkLabel(self.frame_boxes, text="", font=("Arial", 13, "bold"), text_color="#00efff")
        self.label_boxes_title.pack(anchor="w", padx=10, pady=2)
        self.entry_boxes = ctk.CTkEntry(self.frame_boxes)
        self.entry_boxes.pack(fill="x", padx=10, pady=5)

        # Блок результатов
        self.frame_results = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_results.pack(pady=10, padx=20, fill="both", expand=True)

        self.result_rub_needed = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14, "bold"), text_color="#00ff00")
        self.result_rub_needed.pack(anchor="w", padx=15, pady=5)

        # Строка результата для коробок
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
        if self.switch_lang.get() == 1:
            self.current_lang = "EN"
            self.switch_lang.configure(text="Language: EN")
        else:
            self.current_lang = "RU"
            self.switch_lang.configure(text="Language: RU")
        
        self.entry_boxes.delete(0, 'end')
        self.update_ui_language()
        self.trigger_recalc()

    def update_ui_language(self):
        lang = self.current_lang
        data = self.text_dict[lang]

        self.label_title.configure(text=data["title"])
        self.label_promo.configure(text=data["promo_title"])
        self.switch_exp.configure(text=data["switch_exp"])
        self.switch_discount.configure(text=data["switch_discount"])
        self.label_rub.configure(text=data["label_money"])
        self.label_gold.configure(text=data["label_gold"])
        self.label_exp.configure(text=data["label_exp"])
        
        p_rub = "1000" if lang == "RU" else "10"
        self.entry_rub.configure(placeholder_text=data["placeholder"] + p_rub)
        self.entry_gold.configure(placeholder_text=data["placeholder"] + "2500")
        self.entry_exp.configure(placeholder_text=data["placeholder"] + "100000")

        # Настройка текстовок блока коробок
        self.label_boxes_title.configure(text=data["boxes_label"])
        p_box = "30" if lang == "RU" else "80"
        self.entry_boxes.configure(placeholder_text=data["placeholder"] + p_box)
        self.result_boxes_cost.configure(text=data["boxes_res"])

        if not self.entry_rub.get() and not self.entry_gold.get() and not self.entry_exp.get() and not self.entry_boxes.get():
            self.clear_results()

    def setup_bindings(self):
        self.entry_rub.bind("<KeyRelease>", lambda event: self.live_calculate("rub"))
        self.entry_gold.bind("<KeyRelease>", lambda event: self.live_calculate("gold"))
        self.entry_exp.bind("<KeyRelease>", lambda event: self.live_calculate("exp"))
        self.entry_boxes.bind("<KeyRelease>", lambda event: self.live_calculate("boxes"))
        
        self.bind("<Control-KeyPress>", self.global_ctrl_handler)
        self.last_edited = "rub"

    def global_ctrl_handler(self, event):
        if event.keycode == 65 or event.keysym.lower() in ('a', 'ф'):
            focused_widget = self.focus_get()
            if focused_widget in (self.entry_rub, self.entry_gold, self.entry_exp, self.entry_boxes):
                focused_widget.select_range(0, 'end')
                focused_widget.icursor('end')
                return "break"

    def trigger_recalc(self):
        self.live_calculate(self.last_edited, clear_others=False)

    def clear_results(self):
        lang = self.current_lang
        self.result_rub_needed.configure(text=self.text_dict[lang]["res_money"])
        self.result_gold.configure(text=self.text_dict[lang]["res_gold"])
        self.result_credits.configure(text=self.text_dict[lang]["res_credits"])
        self.result_exp.configure(text=self.text_dict[lang]["res_exp"])
        self.result_prem.configure(text=self.text_dict[lang]["res_prem"])
        self.result_boxes_cost.configure(text=self.text_dict[lang]["boxes_res"])

    def live_calculate(self, source, clear_others=True):
        if self.is_calculating:
            return
        
        self.last_edited = source
        lang = self.current_lang
        
        try:
            rub_val = self.entry_rub.get().strip()
            gold_val = self.entry_gold.get().strip()
            exp_val = self.entry_exp.get().strip()
            boxes_val = self.entry_boxes.get().strip()

            if (source == "rub" and not rub_val) or (source == "gold" and not gold_val) or \
               (source == "exp" and not exp_val) or (source == "boxes" and not boxes_val):
                self.clear_results()
                return

            self.is_calculating = True

            if clear_others:
                fields = {"rub": self.entry_rub, "gold": self.entry_gold, "exp": self.entry_exp, "boxes": self.entry_boxes}
                for name, entry in fields.items():
                    if name != source:
                        entry.delete(0, 'end')

            exp_rate = self.PROMO_EXP_PER_GOLD if self.switch_exp.get() == 1 else self.BASE_EXP_PER_GOLD

            # Расчет коробок
            if source == "boxes" and boxes_val:
                box_count = int(boxes_val)
                if lang == "RU":
                    # Прямой расчет стоимости контейнеров «Зов сокола» по 39 руб/шт
                    total_box_cost = box_count * self.BOX_PRICE_RU
                    cost_str = f"{total_box_cost:,.2f}".replace(",", " ")
                    self.result_boxes_cost.configure(text=self.text_dict["RU"]["boxes_res_fmt"].format(cost_str))
                else:
                    # Алгоритм подбора бандлов для EU
                    box_cost, comb_str = self.calculate_eu_boxes_cost(box_count)
                    cost_str = f"{box_cost:,.2f}".replace(",", " ")
                    self.result_boxes_cost.configure(text=self.text_dict["EN"]["boxes_res_fmt"].format(cost_str, comb_str))
                
                # Обнуление остальных полей вывода при расчете коробок
                self.result_rub_needed.configure(text=self.text_dict[lang]["res_money"])
                self.result_gold.configure(text=self.text_dict[lang]["res_gold"])
                self.result_credits.configure(text=self.text_dict[lang]["res_credits"])
                self.result_exp.configure(text=self.text_dict[lang]["res_exp"])
                self.result_prem.configure(text=self.text_dict[lang]["res_prem"])
                self.is_calculating = False
                return

            # Стандартный расчет валют и опыта
            if source == "rub" and rub_val:
                money_needed = float(rub_val)
                if lang == "RU":
                    gold = self.get_gold_by_rub(money_needed)
                else:
                    gold = money_needed / self.EUR_PER_GOLD
            elif source == "gold" and gold_val:
                gold = float(gold_val)
                if lang == "RU":
                    money_needed = self.get_rub_cost_by_gold(gold)
                else:
                    money_needed = gold * self.EUR_PER_GOLD
            elif source == "exp" and exp_val:
                target_exp = float(exp_val)
                gold = target_exp / exp_rate
                if lang == "RU":
                    money_needed = self.get_rub_cost_by_gold(gold)
                else:
                    money_needed = gold * self.EUR_PER_GOLD
            else:
                self.is_calculating = False
                return

            discount_factor = 0.85 if self.switch_discount.get() == 1 else 1.0

            credits = gold * self.CREDITS_PER_GOLD
            free_exp = gold * exp_rate
            prem_cost_30_days = 2500 * discount_factor
            prem_days = (gold / prem_cost_30_days) * 30

            money_str = f"{money_needed:,.2f}".replace(",", " ")
            gold_str = f"{int(gold):,}".replace(",", " ")
            credits_str = f"{int(credits):,}".replace(",", " ")
            exp_str = f"{int(free_exp):,}".replace(",", " ")
            prem_str = f"{int(prem_days)}"

            self.result_rub_needed.configure(text=self.text_dict[lang]["res_money_fmt"].format(money_str))
            self.result_gold.configure(text=self.text_dict[lang]["res_gold_fmt"].format(gold_str))
            self.result_credits.configure(text=self.text_dict[lang]["res_credits_fmt"].format(credits_str))
            self.result_exp.configure(text=self.text_dict[lang]["res_exp_fmt"].format(exp_str))
            self.result_prem.configure(text=self.text_dict[lang]["res_prem_fmt"].format(prem_str))
            
            self.result_boxes_cost.configure(text=self.text_dict[lang]["boxes_res"])

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
