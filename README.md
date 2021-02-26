# steam-hours-per-dollar

I had an idea to make this, figured it'd be nice. Shows the steam games youve purchased, and graphs them by the hours youve played per dollar spent. The color is price. Note that because this is drawn from my payment history, this is the actual price i payed (including discounts) instead of the current steam price of the game.

<img alt="Example graph" src="/example_output.png">

# Usage

This is really shit if you want to use it. First make sure to install yer python libraries with `python -m pip install -r requirements.txt`. Then gotta get 2 basic input files. "player_games.json", which has your stats for games you've played, and "payment_history.html", which has your payment history as downloaded from a web browser, because you can't get it from an api i think.

- **player_games.json** You'll need a [steam api key](https://steamcommunity.com/dev/apikey), and then just plug that and your steamid64 into this url: http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=API_KEY_HERE&steamid=STEAM_ID_HERE&include_appinfo=true&include_played_free_games=true&format=json
- **payment_history.html** Log into this url for steam and download the html for it: https://store.steampowered.com/account/history/

Then put those files in the same directory as everything else, run the script `python calculate.py`, and open up out.html, which will have the graph.