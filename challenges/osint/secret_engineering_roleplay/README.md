# [osint] secret_engineering_roleplay

<table><tbody>
<tr><th>Value</th><td>380 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
</tbody></table>

I heard there's some ERP happening in the JellyCTF discord away from prying eyes...
see if you can find any info on the places they're hanging out

note: can be completed passively, do not send messages to DMs/channels about this chal

https://discord.gg/yG37ycs8t4

10 point hint: where to start looking

50 point hint: tool to solve

---

raw notes:

  - it's going to be Discord hidden channels
    ```
    $ curl -sH 'Authorization: [REDACTED]' 'https://discord.com/api/v9/guilds/1234904889470095380/channels' | jq --raw-output '.[] | "[\(if .type == 0 then "GUILD_TEXT    " elif .type == 2 then "GUILD_VOICE   " elif .type == 4 then "GUILD_CATEGORY" else "UNKNOWN       " end)] \(.name) (\(.parent_id), \(.position), \(.id))"'
    [GUILD_CATEGORY] Text Channels (null, 0, 1234904890317213827)
    [GUILD_TEXT    ] general (1234904890317213827, 0, 1234904890317213829)
    [GUILD_CATEGORY] secret-engineering-role-play (null, 2, 1234905751932108890)
    [GUILD_TEXT    ] tickets (1234907312918102077, 5, 1234906576582606918)
    [GUILD_TEXT    ] transcripts (1234907312918102077, 6, 1234907089441128499)
    [GUILD_CATEGORY] tickets (null, 1, 1234907312918102077)
    [GUILD_TEXT    ] chal-into_the_atmosphere (1234904890317213827, 3, 1234909464902238342)
    [GUILD_TEXT    ] jellyctf (1234905751932108890, 8, 1234939918149746810)
    [GUILD_TEXT    ] open-curly-bracket (1234905751932108890, 9, 1234939933626597487)
    [GUILD_TEXT    ] that-is-what-the-e-stands-for-right (1234905751932108890, 10, 1234939980149686365)
    [GUILD_TEXT    ] close-curly-bracket (1234905751932108890, 11, 1234940000882266142)
    [GUILD_TEXT    ] notif (1234907312918102077, 7, 1234941524609994773)
    [GUILD_TEXT    ] admin (1234904890317213827, 2, 1243721705696923728)
    [GUILD_TEXT    ] log (1234904890317213827, 4, 1243722449162342491)
    [GUILD_TEXT    ] looking-for-team (1234904890317213827, 1, 1245330877660266608)
    [GUILD_VOICE   ] admin (1234904890317213827, 0, 1249622078923997284)
    ```
  - flag is `jellyCTF{that-is-what-the-e-stands-for-right}`
  - meta: this is what prompted me to join the guild
