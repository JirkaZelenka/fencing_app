TRANSLATIONS_EN = {
    "Sermirska aplikace": "Fencing App",
    "Novinky": "News",
    "Nacitani...": "Loading...",
    "Zadne novinky": "No news",
    "Info": "Info",
    "Statistiky": "Statistics",
    "Treninky": "Trainings",
    "Poznamky z treninku": "Training notes",
    "Masicko": "Circuits",
    "Fotky z akci": "Event photos",
    "Kalendar akci": "Event calendar",
    "Wiki": "Wiki",
    "Vybava": "Gear",
    "Platby": "Payments",
    "Odhlasit": "Log out",
    "Prepnout svetly/tmavy rezim": "Toggle light/dark mode",
    "Novinka": "News item",
    "Zavrit": "Close",
    "Oznacit jako prectene": "Mark as read",
    "Prihlaseni - Sermirska aplikace": "Login - Fencing App",
    "Prihlaseni": "Login",
    "Uzivatelske jmeno": "Username",
    "Heslo": "Password",
    "Prihlasit se": "Log in",
    "Zapomneli jste heslo?": "Forgot your password?",
    "Nemate ucet?": "No account yet?",
    "Zaregistrujte se": "Register",
    "Registrace - Sermirska aplikace": "Registration - Fencing App",
    "Vytvorit ucet": "Create account",
    "Email": "Email",
    "Potvrzeni hesla": "Password confirmation",
    "Jiz mate ucet?": "Already have an account?",
    "Uzivatelske jmeno nebo heslo neni spravne.": "Username or password is incorrect.",
    "Ucet byl uspesne vytvoren! Nyni se prosim priradte k jednomu z predpripravenych profilu.": "Account created successfully. Please pair yourself with one of the prepared profiles.",
}


def normalize_text(value: str) -> str:
    replacements = {
        "á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i", "ň": "n",
        "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u", "ů": "u", "ý": "y", "ž": "z",
        "Á": "A", "Č": "C", "Ď": "D", "É": "E", "Ě": "E", "Í": "I", "Ň": "N",
        "Ó": "O", "Ř": "R", "Š": "S", "Ť": "T", "Ú": "U", "Ů": "U", "Ý": "Y", "Ž": "Z",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    return value


def tr_text(text: str, lang: str) -> str:
    if lang != "en":
        return text
    normalized = normalize_text(text)
    return TRANSLATIONS_EN.get(normalized, text)


def tr(request, text: str) -> str:
    lang = getattr(request, "app_language", "cs")
    return tr_text(text, lang)
