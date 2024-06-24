# [osint] into_the_atmosphere

<table><tbody>
<tr><th>Value</th><td>453 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
</tbody></table>

my friend sent me an epic video in discord - I pasted the link into the #chal-into_the_atmosphere channel in the [jellyCTF Discord](https://discord.gg/yG37ycs8t4).

**what time was the channel the video was originally uploaded to created? (NOT when it was posted in the jellyCTF discord).**

be accurate to the nearest millisecond, use UTC, and answer in ISO8601 or unix epoch format, e.g. one of:

* 2024-04-30T17:59:00.995000+00:00
* 2024-04-30T17:59:00.995+00:00
* 2024-04-30T17:59:00.995000Z
* 2024-04-30T17:59:00.995Z
* 1714499940.995
* 1714499940.995000

free hint: it's not in 2024

25 point hint: where to look and how to use

---

raw notes:

  - message: <https://discord.com/channels/1234904889470095380/1234909464902238342/1249437826190413885>
  - linked attachment (excluding auth/expiration crap): <https://cdn.discordapp.com/attachments/225994578258427904/1249437169056088176/Punting_Jelly.mov>
  - first snowflake (225994578258427904) is the channel ID to which the attachment was uploaded; timestamp is 2016-09-15T15:01:46.233Z
  - flag is `2016-09-15T15:01:46.233Z`
  - meta: this challenge eschews any form of `jellyCTF{}` flag wrapper
