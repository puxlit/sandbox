# [forensics] head_empty_2

<table><tbody>
<tr><th>Value</th><td>871 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
</tbody></table>

I was editing [this image](https://twitter.com/jellyhoshiumi/status/1785919609872474201) - can you see the changes I made?

20 point hint: what data to carve out

40 point hint: how to search it

---

raw notes:

  - if we do some exploratorily `strings`ing, we can see that `GMjcaebbcAAoc7D.png` was opened in Paint. maybe it was running when the memory dump was created. pick your poison to extract that process' memory. (I used Volatility; PID was 4700.)
  - looking through strings some more, we can speculate that the image was saved in non-resized dimensions (300×251)
    ```
    puxlit@kiara:~/Sandbox$ strings ./memory.dmp | grep twimg
    ReferrerUrl=https://pbs.twimg.com/media/GMjcaebbcAAoc7D?format=png&name=orig
    HostUrl=https://pbs.twimg.com/media/GMjcaebbcAAoc7D?format=png&name=orig
    s://pbs.twimg.com/me
    _keyhttps://abs.twimg.com/responsive-web/client-web-legacy/shared~bundle.UserLists~loader.ListHandler~ondemand.HoverCard.1fd8459a.js
    ```
  - throw the memory dump in GIMP, start with the speculative width/height, assume buffer is RGBA, scrub through offsets, adjust dimensions as needed
    ![](./dumpy.png)
  - flag is `jellyCTF{pa1nt_pr1nc355}`
  - meta: so I did notice Twitter image-like filenames when exploratorily `strings`ing in [[forensics] head_empty](../head_empty/README.md), and thought that <https://pbs.twimg.com/media/GMjcaebbcAAoc7D.png:orig> was an Easter egg
