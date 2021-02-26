import json
import os
from bs4 import BeautifulSoup, Tag
import plotly.offline as py
import plotly.graph_objs as go

payments_html    = "payment_history.html"
payments_json    = "payment_history.json"
games_input_json = "player_games.json"
out_json         = "games.json"
manual_payments_json = "manual_payments.json"

def getString(x):
	if type(x).__name__ == "NavigableString":
		return x.strip()
	else:
		return "".join(getString(t) for t in x)

def clean(text):
	text = text.replace("&amp;reg;", "")
	return text

def parse_payments():
	with open(payments_html, "r", encoding="utf-8") as f:
		text = f.read()

	soup = BeautifulSoup(text, "html.parser")

	print("patch parse starting")

	table = soup.find_all("table", { "class": "wallet_history_table" })[0]

	payment_history = {}

	for row in table.findChildren("tr"):
		# item = row.findChildren("td", { "class": "wht_items" })[0]
		if len(row.findChildren("td", { "class": "wht_items" })) == 0:
			continue
		item = row.findChildren("td", { "class": "wht_items" })[0]
		if len(item.findChildren("div", { "class": "wth_payment" })) > 0:
			continue # skip things that arent game purchases
		itemtype = row.findChildren("td", { "class": "wht_type" })[0]
		itemtype = itemtype.findChildren("div")[0]

		if getString(itemtype) != "Purchase":
			continue # only look at things that are game purchases
		if "Wallet Credit" in getString(item):
			continue # skip things that are just wallet credits

		total = row.findChildren("td", { "class": "wht_total" })[0]
		item = row.findChildren("td", { "class": "wht_items" })[0]

		gamename = clean(getString(item))
		gamecost = getString(total).replace("$", "")
		# print(gamename, gamecost)

		payment_history[gamename] = float(gamecost)

	if os.path.exists(manual_payments_json):
		with open(manual_payments_json, "r", encoding="utf-8") as f:
			manualdata = json.loads(f.read())
		for game in manualdata:
			payment_history[game] = manualdata[game]

	with open(payments_json, "w+") as f:
		f.write(json.dumps(payment_history, indent="\t"))


def generate_games_json():
	parse_payments()
	with open(games_input_json, "r", encoding="utf-8") as f:
		gamedata = json.loads(f.read())

	with open(payments_json, "r", encoding="utf-8") as f:
		paymentdata = json.loads(f.read())

	missing = []
	data = []
	for game in gamedata["response"]["games"]:
		name = game["name"]
		playtime = game["playtime_forever"]
		playtime = round(playtime / 60.0, 2) # convert to hours
		if playtime == 0:
			continue # skip games i havent played
		if name not in paymentdata:
			# if playtime > 2:
			# 	print(f"missing paymentdata {playtime} for {name}")
			continue
		price = paymentdata[name]
		if price == 0:
			continue # skip free games
		hours_per_dollar = playtime / price
		data.append({
			"label": name,
			"price": price,
			"playtime": playtime,
			"hours_per_dollar": hours_per_dollar
		})

	data = sorted(data, key=lambda game: game["hours_per_dollar"], reverse=True)

	with open(out_json, "w+") as f:
		f.write(json.dumps(data, indent="\t"))



def get_color(value, maxvalue):
	percent = min(value / maxvalue, 1)
	hexval1 = int(percent * 255)
	hexval2 = 255 - hexval1
	return f"#{hexval1:02X}{hexval2:02X}00"

def generate_chart():
	generate_games_json()
	with open(out_json, "r", encoding="utf-8") as f:
		gamedata = json.loads(f.read())

	maxprice = 40

	x = []
	y = []
	c = []

	for game in gamedata:
		x.append(game['label'] + f" ({game['playtime']:.2f} hours, ${game['price']:.2f})")
		y.append(game['hours_per_dollar'])
		c.append(get_color(game['price'], maxprice))

	data = {
		"data": [
			{
				"x": x,
				"y": y,
				"marker_color": c,
				"type": "bar"
			}
		],
		"layout": {
			"title": "Hours per Dollar for Steam Games"
		}
	}

	py.plot(data, filename=f"out.html", auto_open=False)



generate_chart()
