from atproto import Client
from datetime import datetime
import html
import os
import re


def extract_post_id(url: str):
    match = re.search(r'bsky\.app/profile/([^/]+)/post/([^/]+)', url)
    if match:
        handle, post_id = match.groups()
        return f"at://{handle}/app.bsky.feed.post/{post_id}"
    return None


def format_timestamp(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def generate_html(post, replies):
    html_parts = []

    # Main post with UIkit classes
    html_parts.append(f"""
    <div class="tw-text-base tw-space-y-6">
        <div class="tw-text-xl tw-font-bold tw-mb-4 tw-text-gray-800">
            {html.escape(post.author.display_name)} 
            <span class="uk-text-meta">@{html.escape(post.author.handle)}</span>
        </div>
        <p class="uk-margin-remove">
            {html.escape(post.record.text)}
        </p>
        <div class="uk-text-meta uk-margin-small-top">{format_timestamp(post.record.created_at)}</div>
    </div>
    """)

    # Tailwind-styled comment section (prefixed with tw-)
    html_parts.append("""
    <div class="tw-text-base tw-space-y-6">
        <h3 class="tw-text-xl tw-font-bold tw-mb-4 tw-text-gray-800">Comments</h3>
    """)

    if not replies:
        html_parts.append('<div class="tw-text-gray-400 tw-italic">No comments yet.</div>')
    else:
        for reply in replies:
            html_parts.append(f"""
            <div class="tw-border tw-border-gray-200 tw-bg-gray-50 tw-p-4 tw-rounded-xl tw-shadow-sm">
                <div class="tw-text-gray-800 tw-font-semibold tw-mb-1">
                    {html.escape(reply.post.author.display_name) or ""}
                    <span class="tw-text-gray-500 tw-text-sm tw-ml-1">@{html.escape(reply.post.author.handle)}</span>
                </div>
                <p class="tw-text-gray-700 tw-leading-relaxed tw-mb-2">
                    {html.escape(reply.post.record.text)}
                </p>
                <p class="tw-text-xs tw-text-gray-400">{format_timestamp(reply.post.record.created_at)}</p>
            </div>
            """)

    html_parts.append("</div>")  # close Tailwind wrapper

    return "\n".join(html_parts)
def fetch_comments_html(url: str) -> str:
    post_id = extract_post_id(url)
    if not post_id:
        return "<div class='error'>Invalid Bluesky URL</div>"

    client = Client()
    try:
        #client.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
        client.login('bramzijlstra.com', "Asrg75c2!")

    except Exception as e:
        # Fallback: anonymous (public posts only)
        print(e)
        pass

    try:
        thread = client.get_post_thread(post_id)
        post = thread.thread.post
        replies = thread.thread.replies if hasattr(thread.thread, 'replies') else []

        return generate_html(post, replies)
    except Exception as e:
        return f"<div class='error'>Error fetching comments: {html.escape(str(e))}</div>"