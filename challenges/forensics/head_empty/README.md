# [forensics] head_empty

<table><tbody>
<tr><th>Value</th><td>842 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Files</th><td><a href="./files/memory.dmp.gz">memory.dmp.gz</a></td></tr>
</tbody></table>

what's jelly's password?

if you're having problems with the tool, try using a version prior to commit e5a5b895771b655d21c36689c33a534034c31e36 (or manually patch the contents of that commit out)

10 point hint: tool to use

20 point hint: how to use it

---

raw notes:

  - pick your poison to grab NTLM hashes; I went with [`mimikatz`](https://github.com/gentilkiwi/mimikatz)
  - load dump into windbg, follow the documented process. NTLM hash for user `jelly` is `aa05ab5319d59779b937bdbf9797d895`
  - throw into <https://crackstation.net/>, password is `jellynerd2`
