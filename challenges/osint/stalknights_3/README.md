# [osint] stalknights_3

<table><tbody>
<tr><th>Value</th><td>626 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
</tbody></table>

> Hmm, I wonder where this starknight is from...

Find the city and country where this starknight lives.

Flag format: `jellyCTF{name_of_city,name_of_country}`

Note: This challenge **does not** required paid services and can be done only using free tools 

---

raw notes:

  - Instagram bio includes a link to their Twitter account: <https://twitter.com/starknight1337>
  - tweet <https://x.com/starknight1337/status/1788571641439752370> reads:
    > Good morning starknights! Can't wait for Jelly collab!
      - snowflake to timestamp: 2024-05-09T14:08:04Z
      - if it's morning, then they're probably in North America? it'd be around 7 am PDT and 10 am EDT
  - tweet <https://x.com/starknight1337/status/1788584687532970045> reads:
    > Picked my friend up from the airport last Friday and she tells me this was what she flew on?! It's so cute 😭
      - to get the highest resolution, we can <https://pbs.twimg.com/media/GNJUBb_aQAAOLzu?format=jpg&name=small> → <https://pbs.twimg.com/media/GNJUBb_aQAAOLzu?format=jpg&name=orig> (or <https://pbs.twimg.com/media/GNJUBb_aQAAOLzu.jpg:orig>)
      - tail number is JA784A
      - snowflake to timestamp: 2024-05-09T14:59:54Z
      - "last Friday" would be May 3
  - looking up [flight history](https://www.flightaware.com/live/flight/JA784A/history), we can see that plane landed at KJFK, so NYC
    <table><thead>
    <tr><th>Date</th><th>Aircraft</th><th>Origin</th><th>Destination</th><th>Departure</th><th>Arrival</th><th>Duration</th></tr>
    </thead><tbody>
    <tr><td><a href="https://www.flightaware.com/live/flight/JA784A/history/20240503/1355Z/RJTT/KJFK">03-May-2024</a></td><td>B77W</td><td>Tokyo Int'l (Haneda) (<a href="https://www.flightaware.com/live/airport/RJTT">HND / RJTT</a>)</td><td>John F Kennedy Intl (<a href="https://www.flightaware.com/live/airport/KJFK">KJFK</a>)</td><td>23:27 JST</td><td>22:41 EDT</td><td>12:13</td></tr>
    </tbody></table>
  - flag is `jellyCTF{new_york,america}`
  - meta: initially, I tried `jellyCTF{new_york_city,usa}`, `jellyCTF{new_york_city,united_states}`, and `jellyCTF{new_york_city,america}`. some more lenience for matching the city name would be nice
  - meta: not sure how I feel about having to create a FlightAware account for this. I suppose I could've guessed, since the plane only bounces between a handful of cities
