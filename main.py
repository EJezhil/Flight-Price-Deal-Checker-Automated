# Check Sheety API and KIWI API
# Create a sheet with citi names , lowest flight ticket price you want
# Run the program to send automated email to list of emails in the sheet about the price deal


import requests
import datetime
import smtplib
import os


username = os.getenv('email')
password = os.getenv('password')
sheety_API = os.getenv('sheety_API')
kiwi_API = os.getenv('kiwi_API')


IATA = []
price_details = []
str =""

from_place = "MAA"
to_place = "PAR"

sheety_authentication = {
    "Authorization": sheety_API
}

kiwi_authentication = {
    "apikey": kiwi_API
}

KIWI_FLIGHT_IATA_ENDPOINT = "https://api.tequila.kiwi.com/locations/query"
KIWI_FLIGHT_SEARCH_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"
SHEETY_END_POINT = "https://api.sheety.co/49322ab5a397b5c8f90f780ddb34990a/flightSearch/sheet1"
# aezhiltab@gamil.com
SHEETY_SHEET2_END_POINT = "https://api.sheety.co/49322ab5a397b5c8f90f780ddb34990a/flightSearch/sheet2"


# ------------------------------------------------------------------------------------------------------------------------------------------------
# date calculation
from_date = datetime.date.today() + datetime.timedelta(days=1)
to_date = datetime.date.today() + datetime.timedelta(days=30)
# print(from_date)
# print(to_date)
from_dates = from_date.strftime("%d/%m/%Y")
to_dates = to_date.strftime("%d/%m/%Y")
print(from_dates)
print(to_dates)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# read user details from google sheet
response_sheety = requests.get(url=SHEETY_SHEET2_END_POINT, headers=sheety_authentication)
print(response_sheety.raise_for_status())
print(response_sheety.json())
data = response_sheety.json()
user_email = [i["email"] for i in data["sheet2"]]
user_firstname = [i["firstName"] for i in data["sheet2"]]
user_lastanme = [i["lastName"] for i in data["sheet2"]]
print(user_email)
print(user_firstname)
print(user_lastanme)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# find cheapest flight
    # 1) Read citynames
response_sheety = requests.get(url=SHEETY_END_POINT, headers=sheety_authentication)
print(response_sheety.raise_for_status())
print(response_sheety.json())
data = response_sheety.json()
city_names = [i["city"] for i in data["sheet1"]]
print(city_names)


# ------------------------------------------------------------------------------------------------------------------------------------------------
    # 2) find IATA code for the cities in the sheet using the citynames

for i in city_names:
    location = {
        "term": i
    }
    response_flight_iata = requests.get(url=KIWI_FLIGHT_IATA_ENDPOINT, headers=kiwi_authentication, params=location)
    IATA.append(response_flight_iata.json()["locations"][0]["code"])
print(IATA)


# ------------------------------------------------------------------------------------------------------------------------------------------------
    # 3) write IATA code to the sheet
for i in range(0, len(IATA)):
    IATA_CODE = {
        "sheet1": {
            "iataCode": IATA[i]
        }
    }
    response_sheet_write = requests.put(url=f"{SHEETY_END_POINT}/{i + 2}", headers=sheety_authentication,json=IATA_CODE)


 # ------------------------------------------------------------------------------------------------------------------------------------------------
    # 4) read price from list
response_lowest_price = requests.get(url=SHEETY_END_POINT, headers=sheety_authentication)
lowest_price = [i["lowestPrice"] for i in data["sheet1"]]
print(lowest_price)


# ------------------------------------------------------------------------------------------------------------------------------------------------
    # 5) find flight details for the IATA codes in the sheet
for i in range(0, len(IATA)):
    serach_flight = {
        "fly_from": from_place,
        "fly_to": IATA[i],
        "date_from": from_dates,
        "date_to": to_dates
    }
    try:
        response_flight_search = requests.get(url=KIWI_FLIGHT_SEARCH_ENDPOINT, headers=kiwi_authentication,
                                              params=serach_flight)
    except:
        print(f"No flight details for this IATA code {i}")
        continue
    else:
        # print(response_flight_search.raise_for_status())
        price_data = response_flight_search.json()
        # print(price_data)
        price = [i["price"] for i in price_data["data"]]
        # print(price)

# ------------------------------------------------------------------------------------------------------------------------------------------------
    # 6) compare the price with the sheet price
        lowest_flight_price = lowest_price[i]
        for j in price:
            if int(j) < lowest_flight_price:
                lowest_flight_price = j
                print(f"Low price alert!! Only {j} EURO to fly from Chennai-{from_place} to {IATA[i]}-{city_names[i]} ,from {from_dates.replace('/', '-')} to {to_dates.replace('/', '-')}")
                price_details.append(f"\nLow price alert!! Only {j} EURO to fly from Chennai-{from_place} to {IATA[i]}-{city_names[i]} ,from {from_dates.replace('/', '-')} to {to_dates.replace('/', '-')}\n")



# ------------------------------------------------------------------------------------------------------------------------------------------------
# 7) send email to the users in the sheet if we got any price lower then the sheet price

for k in range(0,len(user_email)):
    body = str.join(price_details)
    with smtplib.SMTP("smtp.gmail.com", port=587) as con:
        con.starttls()
        con.login(user=username, password=password)
        con.sendmail(from_addr=username,
                     to_addrs= user_email[k],
                     msg=f"Subject: Cheapest Flight Deals!!\n\nHi {user_firstname[k]} {user_lastanme[k]},{body}")
    print("Flight Deal mail Sent")


