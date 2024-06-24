# [osint] super_fan

<table><tbody>
<tr><th>Value</th><td>955 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
</tbody></table>

this guy is like some kind of jelly superfan or something... what a weirdo. he deleted all his old tweets and changed his username, can you find his new handle?

@j3llyfan7

note: unrelated to the stalknights challenges

10 point hint: pointer on where to start looking

20 point hint: info on how to use a piece of information further

30 point hint: specific location of the information required to complete

---

raw notes:

  - DDG(/Bing) search for `j3llyfan7 twitter` turns up <https://twitter.com/j3llyfan7/status/1772305492322189324>
      - Bing also turns up <https://megalodon.jp/pc/history/20240604/22>, leading to <https://megalodon.jp/2024-0604-0904-16/https://twitter.com:443/j3llyfan7>, but what was saved was a login interstitial, so… not useful
  - Wayback Machine _does_ have a working copy of the tweet, but successfully _loading_ the snapshotted page is flakey and requires patience. <https://web.archive.org/web/20240329093042/https://twitter.com/j3llyfan7/status/1772305492322189324> worked for me after a few retries
      - tweet reads:
        > feelin a lil freaky might post a flag later
  - what we really care about is one of the snapshotted API calls that fetches tweet info (<https://web.archive.org/web/20240329093043id_/https://api.twitter.com/graphql/d8VeZsachn33iPtrefQGHQ/TweetResultByRestId?variables=%7B%22tweetId%22%3A%221772305492322189324%22%2C%22withCommunity%22%3Afalse%2C%22includePromotedContent%22%3Afalse%2C%22withVoice%22%3Afalse%7D&features=%7B%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Atrue%2C%22withArticlePlainText%22%3Afalse%7D>), as it'll include info about the tweeting user, including their _stable_ REST ID: `1772301250572263429`
    ```
    $ jq --raw-output '.data.tweetResult.result.core.user_results.result.rest_id' <./twitter-api-graphql-TweetResultByRestId-1772305492322189324.json
    1772301250572263429
    ```
      - (it doesn't matter too much here, but we can use the `id_` flag to get the resource as archived, without rewrites)
        ```diff
        --- without any flags (pretty-printed via `jq`)
        +++ with `id_` flag (pretty-printed via `jq`)
        @@ -36,8 +36,8 @@
                         "normal_followers_count": 0,
                         "pinned_tweet_ids_str": [],
                         "possibly_sensitive": false,
        -                "profile_banner_url": "https://web.archive.org/web/20240329093047/https://pbs.twimg.com/profile_banners/1772301250572263429/1711456007",
        -                "profile_image_url_https": "https://web.archive.org/web/20240329093047/https://pbs.twimg.com/profile_images/1772305047726034945/-cwL0Yka_normal.jpg",
        +                "profile_banner_url": "https://pbs.twimg.com/profile_banners/1772301250572263429/1711456007",
        +                "profile_image_url_https": "https://pbs.twimg.com/profile_images/1772305047726034945/-cwL0Yka_normal.jpg",
                         "profile_interstitial_type": "",
                         "screen_name": "j3llyfan7",
                         "statuses_count": 1,
        ```
  - with this ID, we can construct a URL that'll redirect us to the user's current profile: <https://x.com/i/user/1772301250572263429>
  - their new handle is `@bmFmeWxsM2p3ZW4`, they have three tweets
      - tweet <https://x.com/bmFmeWxsM2p3ZW4/status/1774200080725131543> reads:
        > amVsbA==

        … which decodes to `jell`
      - tweet <https://x.com/bmFmeWxsM2p3ZW4/status/1794061497104056612> reads:
        > eUNURns=

        … which decodes to `yCTF{`
      - tweet <https://x.com/bmFmeWxsM2p3ZW4/status/1794061516347482225> reads:
        > dGhpc193YXNfbm90X215X2ludGVudGlvbn0=

        … which decodes to `this_was_not_my_intention}`
