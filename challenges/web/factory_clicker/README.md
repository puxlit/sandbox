# [web] factory_clicker

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>LISP BEAMER</td></tr>
<tr><th>Connection info</th><td><a href="https://factory-clicker.jellyc.tf/">https://factory-clicker.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/factory_clicker.zip">factory_clicker.zip</a></td></tr>
</tbody></table>

---

raw notes:

  - reading the provided source code, naively we have one minute to increment our way to over 500,000,000,000
  - however, we can dictate the increment amount. we don't even need to increment from an existing session; score will default to zero
    ```
    $ curl -sX POST 'https://factory-clicker.jellyc.tf/increment?increment_amount=500000000001' | jq
    {
      "flag": "jellyCTF{keep_on_piping_jelly}",
      "score": 500000000001
    }
    ```
