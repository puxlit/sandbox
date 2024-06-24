# [osint] stalknights_2

<table><tbody>
<tr><th>Value</th><td>802 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
</tbody></table>

**starknight1337** shared another photo on their Instagram. What is the name of the park where the photo was taken?

Flag format: `jellyCTF{name_of_park}` (all lowercase)

Note: If a link/image asks for login, try opening it in a new tab to bypass login.

---

raw notes:

  - other post is <https://www.instagram.com/p/C7wZW4JPrOz/>, caption reads:
    > Waffle throwback! 😍
      - to get the highest resolution, we can grab the image URL with the `1080w` width descriptor on the `<img>`'s `srcset`
  - key landmarks:
      - a stall with a sign that reads "BRIGHT FESTIVAL" in white on a purple/orange circle, which upon searching turns up <https://www.visit.brussels/en/visitors/agenda/bright-festival>
      - a building with a neon sign of "28" in a circle, which upon searching turns up Brasserie 28
  - looking up "Brasserie 28, Brussels" in maps, it looks like [Square de la Putterie](https://gardens.brussels/fr/espaces-verts/square-de-la-putterie) has the same style of fencing atop brick wall on the side closest to Brasserie 28
  - flag is `jellyCTF{square_de_la_putterie}`
  - meta: initially, I wasn't sure, because the road looked much wider in Street View than it did in the photo
