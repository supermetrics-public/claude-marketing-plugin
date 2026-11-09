---
name: social-media-publishing
description: Publish and schedule social posts and moderate comments through Supermetrics on Instagram, LinkedIn company pages and Google Business Profile — images, carousels, reels, stories, text and links; reply to, hide or delete comments; answer Google reviews. Use for "schedule Instagram post", "post on LinkedIn", "reply to comments", "best time to post".
---

# Social media publishing and comments

Publish, schedule and moderate posts with the `manage_social_media` tool. Posts go out under the user's brand, so treat every write as public and permanent. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Platforms

| Platform | `ds_id` | Content types |
|---|---|---|
| Instagram (professional account) | `IGI` (default) | `IMAGE`, `VIDEO` (a reel), `CAROUSEL` (2–10), `STORY` (no caption; `frames` for a sequence) |
| LinkedIn company page | `LIP` | `TEXT`, `LINK`, `IMAGE`, `CAROUSEL` (2–20 images); no video or stories |
| Google Business Profile | `GMB` | `TEXT`, `IMAGE` (one image); caption required, up to 1,500 characters |

Pass `ds_id: GMB` for Google Business Profile even if the tool's parameter list shows only `IGI` and `LIP`. Get `account_id` from `accounts_discovery` with the same `ds_id`; for Google Business Profile pick a single location. For the exact limits and `platform_options` of each type (Instagram user tags and collaborators, Google event, offer and call-to-action posts), call `supermetrics_guide` with `mode: social_publishing` before the first publish.

## Before writing anything

1. Writes must be enabled per account at [hub.supermetrics.com/write-settings](https://hub.supermetrics.com/write-settings), where the account owner also sets the approval level. A `WRITE_ACCESS_NOT_ENABLED` error includes the link to give the user; only the person who connected the account can turn it on.
2. Check business context with `get_business_context` (with `ds_id` and `account_id`) for brand voice, hashtag and posting rules.

## Safety rules

- **Never publish or schedule without explicit approval.** Show the user the final caption, media, account and time (with time zone), and wait for a clear yes.
- **Dry-run first.** Send the same call with `validate_only: true`; it checks parameters, media, access and quota without posting. Publish only after it passes.
- **Approval links.** If the account requires approval, the write returns `approval_url`. Show it to the user and stop. After they approve, call `status` with `approval_ref` to get the result.
- **Published posts can't be edited or deleted here.** The user does that in the platform. Only posts scheduled through Supermetrics can be changed or cancelled.
- **Deleting a comment is irreversible.** Confirm before `moderate_comment` with `delete: true`; prefer `hidden: true` on Instagram when the user is unsure.
- **Don't retry blindly.** Retry only `failures` marked `retry_safe`. Repeating the same write within 15 minutes returns the first result rather than posting twice.

## Publishing

Use `action: publish` with `content_type`, `caption` and one media source:

- `media_url` (a public https URL), or `upload_ref` from `creative_picker`, which browses, uploads or AI-generates images with a preview. Use `media_prompt` (AI image without preview) only if the user says they don't need to review it.
- Carousels take several: `media_urls`, `media_prompts` or a comma-separated `upload_ref`.
- AI images, videos and story sequences run in the background: poll `status` with `job_id` and `wait_seconds`.

## Scheduling

- Add `publish_at` (5 minutes to 75 days ahead). Without a UTC offset, also send `timezone` (IANA, for example `Europe/Helsinki`); ask the user if unsure.
- `status` with no target lists scheduled posts (`state`: `scheduled`, `published`, `failed`, `cancelled`, `all`). Change caption or time with `update_post` and `scheduled_id`; to change media, `cancel_scheduled` and publish again.
- **Best time to post (Instagram).** Run `data_query` with `ds_id: IGI`, fields `hour,online_followers`, the last 30 days and `timezone` set to the user's zone, then suggest the top hours. Space one account's posts at least 5 minutes apart.

## Comments and reviews

- `list_comments` with `media_id` (find recent post IDs with `data_query`: ds_id `IGI`, or `update_id` from `LIP`). Reply with `action: comment` and `comment_id`; hide, unhide or delete with `moderate_comment`; turn comments on or off with `update_post` and `media_id`.
- LinkedIn can't hide comments, threads replies one level deep and shows commenters as LinkedIn IDs, not names.
- Google Business Profile: `list_comments` without `media_id` lists the location's reviews with their `rating`. A reply replaces the previous one; deleting removes only your reply, not the review.

## After writing

Report exactly what was published or scheduled, with the post link or `scheduled_id`. Analyse results later with `data_query` (`IGI` for Instagram posts, `LIP` for LinkedIn page posts, `GMB` for Google Business Profile, see `google-business-profile`).
