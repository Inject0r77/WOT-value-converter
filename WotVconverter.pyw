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
        self.geometry("500x710")
        self.resizable(False, False)

        self.is_calculating = False
        self.current_lang = "RU"

        # Внутриигровые курсы ресурсов
        self.CREDITS_PER_GOLD = 400
        self.BASE_EXP_PER_GOLD = 25
        self.PROMO_EXP_PER_GOLD = 35
        
        # ТОЧНЫЙ ЕВРОПЕЙСКИЙ КУРС ИЗ СКРИНШОТА (~0.0036 EUR за 1 единицу золота)
        self.EUR_PER_GOLD = 0.0036  

        self.text_dict = {
            "RU": {
                "title": "Конвертер валют Lesta",
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
                "error": "Ошибка: вводите только числа!"
            },
            "EN": {
                "title": "Currency Converter Wargaming(eu)",
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
                "error": "Error: enter numbers only!"
            }
        }

        self.create_widgets()
        self.setup_bindings()
        self.update_ui_language()

    def get_rub_cost_by_gold(self, gold):
        """ Динамический расчет стоимости доната в рублях на основе сетки цен """
        if gold <= 0:
            return 0
        if gold <= 100:
            return gold * 0.16
        elif gold <= 500:
            return 16 + (gold - 100) * (62 / 400)
        else:
            return gold * 0.156

    def get_gold_by_rub(self, rub):
        """ Обратный расчет золота на основе внесенных рублей """
        if rub <= 0:
            return 0
        if rub <= 16:
            return rub / 0.16
        elif rub <= 78:
            return 100 + (rub - 16) / (62 / 400)
        else:
            return rub / 0.156

    def create_widgets(self):
        self.frame_lang = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_lang.pack(anchor="ne", padx=20, pady=5)
        
        self.switch_lang = ctk.CTkSwitch(self.frame_lang, text="Language: RU", font=("Arial", 11, "bold"), command=self.toggle_language)
        self.switch_lang.pack()

        self.label_title = ctk.CTkLabel(self, text="", font=("Arial", 24, "bold"), text_color="#ff7f00")
        self.label_title.pack(pady=10)

        self.frame_switches = ctk.CTkFrame(self)
        self.frame_switches.pack(pady=10, padx=20, fill="x")

        self.label_promo = ctk.CTkLabel(self.frame_switches, text="", font=("Arial", 14, "bold"))
        self.label_promo.pack(anchor="w", padx=10, pady=5)

        self.switch_exp = ctk.CTkSwitch(self.frame_switches, text="", font=("Arial", 12), command=self.trigger_recalc)
        self.switch_exp.pack(anchor="w", padx=20, pady=5)

        self.switch_discount = ctk.CTkSwitch(self.frame_switches, text="", font=("Arial", 12), command=self.trigger_recalc)
        self.switch_discount.pack(anchor="w", padx=20, pady=5)

        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(pady=15, padx=20, fill="x")

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

        self.frame_results = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_results.pack(pady=15, padx=20, fill="both", expand=True)

        self.result_rub_needed = ctk.CTkLabel(self.frame_results, text="", font=("Arial", 14, "bold"), text_color="#00ff00")
        self.result_rub_needed.pack(anchor="w", padx=15, pady=7)

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

        if not self.entry_rub.get() and not self.entry_gold.get() and not self.entry_exp.get():
            self.clear_results()

    def setup_bindings(self):
        self.entry_rub.bind("<KeyRelease>", lambda event: self.live_calculate("rub"))
        self.entry_gold.bind("<KeyRelease>", lambda event: self.live_calculate("gold"))
        self.entry_exp.bind("<KeyRelease>", lambda event: self.live_calculate("exp"))
        self.bind("<Control-KeyPress>", self.global_ctrl_handler)
        self.last_edited = "rub"

    def global_ctrl_handler(self, event):
        if event.keycode == 65 or event.keysym.lower() in ('a', 'ф'):
            focused_widget = self.focus_get()
            if focused_widget in (self.entry_rub, self.entry_gold, self.entry_exp):
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

    def live_calculate(self, source, clear_others=True):
        if self.is_calculating:
            return
        
        self.last_edited = source
        lang = self.current_lang
        
        try:
            rub_val = self.entry_rub.get().strip()
            gold_val = self.entry_gold.get().strip()
            exp_val = self.entry_exp.get().strip()

            if (source == "rub" and not rub_val) or (source == "gold" and not gold_val) or (source == "exp" and not exp_val):
                self.clear_results()
                return

            self.is_calculating = True

            if clear_others:
                if source == "rub":
                    self.entry_gold.delete(0, 'end')
                    self.entry_exp.delete(0, 'end')
                elif source == "gold":
                    self.entry_rub.delete(0, 'end')
                    self.entry_exp.delete(0, 'end')
                elif source == "exp":
                    self.entry_rub.delete(0, 'end')
                    self.entry_gold.delete(0, 'end')

            exp_rate = self.PROMO_EXP_PER_GOLD if self.switch_exp.get() == 1 else self.BASE_EXP_PER_GOLD

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
