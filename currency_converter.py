import tkinter as tk
import tkinter.ttk as ttk
from bs4 import BeautifulSoup
import urllib.request
import pickle
import re

def get_data():
    '''
    function pulling currency rates from website
    or from backup file

    returns
    -------
    dictionary with names of currency and it's worth
    and date from which they are

    '''
    nbp_page = "https://www.nbp.pl/home.aspx?f=%2Fkursy%2Fkursya.html&fbclid=IwAR2fYe5V6HgOutrgzUV1eWW_3x-pMigh9yMIZlHmDlXTMAjhUZmr8nTIeGI"
    currency_rate = {}

    try:
        text = urllib.request.urlopen(nbp_page).read()
        soup = BeautifulSoup(text, "html.parser")

        link = soup.find("a", string="Powyższa tabela w formacie .xml")
        url = "https://www.nbp.pl" + str(link.get("href"))

        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content, "html.parser")

        date = soup.find("data_publikacji")
        publication_date = str("Valid exchange rate from: " + date.get_text())

        code = soup.find_all("kod_waluty")
        currency = soup.find_all("nazwa_waluty")
        names_list = []
        for c,u in zip(code,currency):
            name = str(c.get_text() + " (" + u.get_text() + ")")
            names_list.append(name)

        rate = soup.find_all("kurs_sredni")
        scaler = soup.find_all("przelicznik")
        rate_list = []
        for r,s in zip(rate,scaler):
            name = r.get_text().replace(",", ".")
            num = float(name) / float(s.get_text())       # multiplying by rate
            rate_list.append(num)

        for i in range(0, len(rate_list)):
            currency_rate[names_list[i]] = rate_list[i]
        currency_rate["PLN (złoty)"] = float(1.0)         # added PLN
  
        outfile = open("backup_data", "wb")               # new backup file
        pickle.dump(currency_rate, outfile)
        outfile.close()

    except urllib.error.URLError:                         # using backup file if there's no internet connection 
        infile = open("backup_data", "rb")
        currency_rate = pickle.load(infile)
        infile.close()

        publication_date = "No internet connection!"

    return currency_rate, publication_date

def convert():
    '''
    function converting currencies after pressing 
    convert button

    '''
    first_currency = currency_list1.get()
    second_currency = currency_list2.get()
    rate1 = float(currency_rate.get(first_currency))
    rate2 = float(currency_rate.get(second_currency))
    try :
        amount = float(entry.get())
        final = ((rate1/rate2) * amount)
        output["text"] = f"{final}" 
    except ValueError:                               # accepting only numbers 
        output["text"] = "enter a number"
    
def end():
    '''
    function closing aplication
    '''
    window.destroy()

window = tk.Tk()
window.title("Currency converter")
window.configure(bg = "#7AA9BF")
window.resizable(False,False)

myfont = ("Balker", 15)

currency_rate, publication_date = get_data()
currency_names = list(currency_rate.keys())

tk.Label(window, text="From", fg="black", bg="#7AA9BF", font=myfont).grid(row=0, column=0, padx=5, pady=5, sticky="W")
currency_list1 = ttk.Combobox(window, values=currency_names, state="readonly", font=myfont)
currency_list1.grid(row=1, column=0, padx=5, pady=5)

tk.Label(window, text="Amount", fg="black", bg="#7AA9BF", font=myfont).grid(row=3, column=0, padx=5, pady=5, sticky="W")
entry = tk.Entry(window, font=myfont, bg="#eae6e3", width=21)
entry.grid(row=4, column=0, padx=5, pady=5)

tk.Label(window, text="To", fg="black", bg="#7AA9BF", font=myfont).grid(row=0, column=1, padx=5, pady=5, sticky="W")
currency_list2 = ttk.Combobox(window, values=currency_names, state="readonly", font=myfont)
currency_list2.grid(row=1, column=1, padx=5, pady=5)

tk.Label(window, text="Worth", fg="black", bg="#7AA9BF", font=myfont).grid(row=3, column=1, padx=5, pady=5, sticky="W")
output = tk.Label(window, text=" ", relief="sunken", bg="#eae6e3", font=myfont, width=21)
output.grid(row=4, column=1, padx=5, pady=5) 

button_convert = tk.Button(window, text="Convert", font=myfont, fg="#14406c", bg="#eae6e3", command=convert)
button_convert.grid(row=5, column=0, padx=5, pady=5)

button_end = tk.Button(window, text="End", font=myfont, fg="#14406c", bg="#eae6e3", command=end)
button_end.grid(row=5, column=1, padx=5, pady=5)

last_date = tk.Label(window, text=publication_date, font=("Balker", 8), bg="#7AA9BF")
last_date.grid(row=6, column=1, sticky="E")

window.mainloop()
