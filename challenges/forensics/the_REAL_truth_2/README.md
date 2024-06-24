# [forensics] the_REAL_truth_2

<table><tbody>
<tr><th>Value</th><td>890 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://therealtruthaboutjellyhoshiumi.carrd.co/">https://therealtruthaboutjellyhoshiumi.carrd.co/</a></td></tr>
</tbody></table>

this chal is web/forensics

looks like jelly still has some more secrets on her site

note: this is the only subdomain in scope. do not bruteforce/dirbust.

10 point hint: where to look for the web part of the chal

20 point hint: what to pay attention to for the forensics part of the chal

---

raw notes:

  - sitemap (<https://therealtruthaboutjellyhoshiumi.carrd.co/sitemap.xml> ([archived](./sitemap.xml))) indicates that, in addition to `image01.png`, there's an `image02.png`
  - most apparent difference is the lack of cyan at the top of `image02.png`
  - try diffing the two images: `magick composite image02.png image01.png -compose difference imagediff.png`
  - flag is `jellyCTF{tw0_h41v3s_m4k3_a_wh0L3}`
  - meta: I got this before [[forensics] the_REAL_truth](../the_REAL_truth/README.md) and thought this was the flag to the first part. ideally, the challenge descriptions should be clearer about which flag goes where
