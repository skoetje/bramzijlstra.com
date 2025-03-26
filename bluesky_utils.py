import os
os.environ['BLUESKY_HANDLE'] = 'bramzijlstra.com'
os.environ['BLUESKY_PASSWORD'] = 'Asrg75c2!'

# !/usr/bin/env python3

import re
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from atproto import Client


def extract_post_id(url: str) -> Optional[str]:
    """Extract the post ID from a Bluesky URL."""
    pattern = r'bsky\.app/profile/([^/]+)/post/([^/]+)'
    match = re.search(pattern, url)
    if match:
        handle = match.group(1)
        post_id = match.group(2)
        return f"at://{handle}/app.bsky.feed.post/{post_id}"
    return None


def format_bluesky_date(date_str: str) -> str:
    """Format date from Bluesky timestamp format to readable format."""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return dt.strftime("%B %d, %Y at %H:%M")


def fetch_bluesky_comments(bluesky_url: str) -> Optional[Dict[str, Any]]:
    """Fetch comments from a Bluesky post URL."""
    try:
        # Initialize the client
        client = Client()

        # Try to use environment variables if available
        env_handle = os.environ.get('BLUESKY_HANDLE')
        env_password = os.environ.get('BLUESKY_PASSWORD')

        auth_success = False
        if env_handle and env_password:
            try:
                client.login(env_handle, env_password)
                auth_success = True
                print(f"Authenticated as {env_handle} using environment variables")
            except Exception as e:
                print(f"Authentication with environment variables failed: {e}")
                print("Trying to continue without authentication (may fail for private posts)...")
        else:
            print("No authentication credentials provided. Some operations may require authentication.")
            print("Set BLUESKY_HANDLE and BLUESKY_PASSWORD environment variables.")

        # Extract post ID from URL
        full_post_id = extract_post_id(bluesky_url)
        if not full_post_id:
            print(f"Error: Invalid Bluesky URL format: {bluesky_url}")
            return None

        # Get the post thread
        thread = client.get_post_thread(full_post_id)
        post = thread.thread.post
        replies = thread.thread.replies if hasattr(thread.thread, 'replies') else []

        # Format data as JSON structure
        result = {
            "post": {
                "author": {
                    "name": post.author.display_name,
                    "handle": post.author.handle,
                    "avatar": post.author.avatar if hasattr(post.author, 'avatar') else None
                },
                "content": post.record.text,
                "timestamp": post.record.created_at
            },
            "comments": []
        }

        for reply in replies:
            result["comments"].append({
                "author": {
                    "name": reply.post.author.display_name,
                    "handle": reply.post.author.handle,
                    "avatar": reply.post.author.avatar if hasattr(reply.post.author, 'avatar') else None
                },
                "content": reply.post.record.text,
                "timestamp": reply.post.record.created_at
            })

        return result

    except Exception as e:
        print(f"Error fetching comments: {str(e)}")
        return None