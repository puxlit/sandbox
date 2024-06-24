# [osint] stalknights_1

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><a href="https://www.instagram.com/p/C6teE7Uv98I/">https://www.instagram.com/p/C6teE7Uv98I/</a></td></tr>
</tbody></table>

Stumbled across this Starknight while scrolling through Instagram. Can you figure out what neighbourhood and country this photo was taken in?

Flag format: `jellyCTF{neighbourhood_name,country}` (all lowercase)

---

raw notes:

  - post caption reads:
    > Jelly's coffee announcement reminded me of the ancient coffee I saw on my last holiday 😂
  - reverse image search brings up the [Albert Heijn Museum Shop](https://albertheijnerfgoed.nl/museumwinkel) on <https://www.travelwithsimina.com/one-day-in-zaanse-schans/>
  - flag is `jellyCTF{zaanse_schans,netherlands}`
  - meta: I initially tried `jellyCTF{zaandam,netherlands}`, but apparently [Zaandam](https://en.wikipedia.org/wiki/Zaandam) is a city, whereas [Zaanse Schans](https://en.wikipedia.org/wiki/Zaanse_Schans) is a "neighbourhood" of Zaandam
