# [web] aidoru

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><a href="https://aidoru.jellyc.tf/">https://aidoru.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/aidoru.zip">aidoru.zip</a></td></tr>
</tbody></table>

### Phase Connect is full of seiso idols!
Note: Volume warning

There's a hidden flag on Jelly's page, but the creator hasn't made her page public yet.
Can you find a way to access her page and capture the flag?

10 point hint: Main method \
25 point hint: Tool to use

---

raw notes:

  - using provided source code, the talent we're interested in is `jelly`, but implementation for `get_uuid` (called by `get_profile`) is not available to us
  - if we look at one of the other talents, like `rie`, the URL is `/covers/41895503f71f59ce931bd3590c577b3c`, which looks like it's probably an MD5 hash. noting that `get_uuid` takes a profile name:
    ```
    puxlit@kiara:~$ echo -n 'rie' | md5sum
    41895503f71f59ce931bd3590c577b3c  -
    puxlit@kiara:~$ echo -n 'jelly' | md5sum
    328356824c8487cf314aa350d11ae145  -
    ```
  - view source for <https://aidoru.jellyc.tf/covers/328356824c8487cf314aa350d11ae145> ([archived](./covers-328356824c8487cf314aa350d11ae145.html)), flag is embedded in malformed YT `<iframe>`'s `src`:
    ```html
        <h2>flag</h2>
        <iframe width="560" height="315" src="https://www.youtube.com/embed/jellyCTF{u_r_the_p3rfect_ultimate_IDOR}?autoplay=;start="></iframe>
    ```
