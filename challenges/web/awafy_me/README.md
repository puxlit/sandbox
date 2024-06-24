# [web] awafy_me

<table><tbody>
<tr><th>Value</th><td>553 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><a href="https://awafy-me.jellyc.tf/">https://awafy-me.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/awafy_me.zip">awafy_me.zip</a></td></tr>
</tbody></table>

Hacked this together for Jelly's mutually beneficial partnership application

---

raw notes:

  - reading the provided source code, the `user_input` query parameter is passed to a system shell with improper escaping. (they're using Flask's `escape` meant for escaping HTML special characters)
    ```py
    @app.route("/")
    def index():
        user_input = escape(request.args.get("user_input", ""))
    
        if user_input:
            try:
                result = subprocess.check_output("python3 ./awafier.py " + user_input, shell=True)
                result = result.decode()
    ```
  - we can supply a `user_input` of `; cat /app/flag.txt` to get the flag `jellyCTF{c3rt1fied_aw4t15tic}`
