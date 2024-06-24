# [web] do_not_trust

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
</tbody></table>

there's a flag hidden somewhere on this site (jellyc.tf) in a common location for websites, see if you can find it

---

raw notes:

  - "a common location for websites" -> `robots.txt`
  - <https://jellyc.tf/robots.txt> ([archived](./robots.txt)):
    ```
    User-agent: *
    Disallow: /
    # jellyCTF{g0d_d4mn_cL4nk3r5}
    ```
