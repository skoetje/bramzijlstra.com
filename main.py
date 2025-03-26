from fasthtml.common import *
from lucide_fasthtml import Lucide
import yaml
from datetime import datetime
import os
from bluesky_utils import fetch_bluesky_comments, format_bluesky_date

# Create cache directory if it doesn't exist
if not os.path.exists("cache"):
    os.makedirs("cache")


frankenui = (
    Link(
        rel="stylesheet",
        href="https://unpkg.com/franken-wc@0.1.0/dist/css/zinc.min.css",
    ),
    Script(src="https://cdn.jsdelivr.net/npm/uikit@3.21.6/dist/js/uikit.min.js"),
    Script(src="https://cdn.jsdelivr.net/npm/uikit@3.21.6/dist/js/uikit-icons.min.js"),
)
tailwind = Link(rel="stylesheet", href="/app.css", type="text/css")
bluesky_css = Link(rel="stylesheet", href="/custom-bluesky.css", type="text/css")

og_headers = (
    Meta(property="og:image", content="https://blog.mariusvach.com/images/og.png"),
)

app, rt = fast_app(
    pico=False,
    static_path="public",
    hdrs=(
        frankenui,
        tailwind,
        bluesky_css,
        Meta(name='google-site-verification', content='itQt7wzA-lxt_NZlV4e5GOMtF3TLj_DGdTXnwCP5aN4'),
        *og_headers,
        MarkdownJS(),
        HighlightJS(langs=["python", "bash", "yaml", "json"], light="atom-one-dark"),
    ),
)


def BlueskyComments(comments_data, bluesky_url):
    """Render Bluesky comments section."""
    if not comments_data:
        return Div(
            Div(
                "Failed to load Bluesky comments. Please try again later.",
                cls="uk-alert uk-alert-warning"
            ),
            A(
                Lucide("message-circle", cls="w-4 h-4 mr-2"),
                "View on Bluesky",
                href=bluesky_url,
                cls="bluesky-cta",
                target="_blank"
            ),
            cls="bluesky-comment-section"
        )

    post = comments_data.get("post", {})
    comments = comments_data.get("comments", [])

    if not comments:
        return Div(
            H3("Bluesky Comments", cls="text-xl font-bold"),
            Div(
                P(
                    "No comments yet. Be the first to join the conversation!",
                    cls="uk-text-muted"
                ),
                cls="bluesky-empty"
            ),
            A(
                Lucide("message-circle", cls="w-4 h-4 mr-2"),
                "Comment on Bluesky",
                href=bluesky_url,
                cls="bluesky-cta",
                target="_blank"
            ),
            cls="bluesky-comment-section"
        )

    def default_avatar(handle):
        """Generate a default avatar with initials if no avatar is available"""
        # Use the first character of the handle for default avatar
        initial = handle[0].upper() if handle else "?"
        return Div(
            initial,
            cls="bluesky-avatar-default"
        )

    return Div(
        H3("Bluesky Comments", cls="text-xl font-bold"),
        P(
            f"{len(comments)} comment{'s' if len(comments) != 1 else ''} from Bluesky",
            cls="uk-text-muted uk-text-small uk-margin-small-bottom"
        ),
        Div(
            *[Div(
                Div(
                    cls="bluesky-comment-container"
                )(
                    Div(
                        cls="bluesky-avatar"
                    )(
                        Img(
                            src=comment.get("author", {}).get("avatar"),
                            alt=f"Avatar of @{comment.get('author', {}).get('handle')}",
                            cls="uk-border-circle",
                        ) if comment.get("author", {}).get("avatar") else default_avatar(
                            comment.get("author", {}).get("handle", ""))
                    ),
                    Div(
                        cls="bluesky-comment-header"
                    )(
                        Div(
                            cls="bluesky-author-name"
                        )(comment.get("author", {}).get("name", "Anonymous")),
                        Div(
                            cls="bluesky-author-handle"
                        )(f"@{comment.get('author', {}).get('handle', '')}"),
                        Div(
                            cls="bluesky-content"
                        )(comment.get("content", "")),
                        Div(
                            cls="bluesky-timestamp"
                        )(format_bluesky_date(comment.get("timestamp", ""))),
                    )
                ),
                cls="bluesky-comment-card bluesky-comment"
            ) for comment in comments],
            cls="uk-margin-medium-bottom"
        ),
        A(
            Lucide("message-circle", cls="w-4 h-4 mr-2"),
            "Join the conversation on Bluesky",
            href=bluesky_url,
            cls="bluesky-cta",
            target="_blank"
        ),
        cls="bluesky-comment-section"
    )


@rt("/")
def get():
    posts = []
    posts_dir = "posts"

    for filename in os.listdir(posts_dir):
        if filename.endswith(".md"):
            with open(os.path.join(posts_dir, filename), "r") as file:
                content = file.read()
                parts = content.split("---")
                if len(parts) > 2:
                    post = yaml.safe_load(parts[1])
                    post["slug"] = os.path.splitext(filename)[0]
                    post["content"] = parts[2].strip()
                    lines = post["content"].split("\n")
                    if "excerpt" not in post:
                        for line in lines:
                            if line.strip() and not line.strip().startswith("!["):
                                post["excerpt"] = line.strip()
                                break

                    # Convert date string to datetime object if it exists
                    if "date" in post and isinstance(post["date"], str):
                        post["date"] = datetime.strptime(post["date"], "%Y-%m-%d")

                    if not post["draft"]:
                        posts.append(post)

    # Sort posts by date, most recent first
    posts.sort(key=lambda x: x.get("date", datetime.min), reverse=True)

    def BlogCard(post, *args, **kwargs):
        # Add bluesky comment count badge if URL exists
        bluesky_badge = None
        if "blueskyUrl" in post and post["blueskyUrl"]:
            bluesky_badge = Span(
                Lucide("message-circle", cls="w-3 h-3 inline-block mr-1"),
                "Bluesky Comments",
                cls="uk-badge uk-margin-small-right"
            )

        return Div(
            Div(
                *args,
                A(
                    H2(
                        post["title"],
                        cls="text-2xl font-bold font-heading tracking-tight",
                    ),
                    P(
                        post["date"].strftime("%B %d, %Y"),
                        cls="uk-text-muted uk-text-small uk-text-italic",
                    ),
                    P(
                        post["excerpt"] if "excerpt" in post else "",
                        cls="uk-text-muted uk-margin-small-top marked",
                    ),
                    href=f"/posts/{post['slug']}",
                ),
                cls="uk-card-body",
            ),
            cls=f"uk-card uk-card-default uk-border-rounded uk-box-shadow-small {kwargs.pop('cls', '')}",
            **kwargs,
        )

    return Title("Bram Zijlstra"), Div(
        H1(
            "My name is Bram.",
            cls="text-4xl font-bold font-heading tracking-tight uk-margin-small-bottom",
        ),
        P(
            "I'm a machine learning engineer and co-founder of ",
            A("BQ Insights", href="https://bqinsights.nl", style="color: #9ca3af; text-decoration: underline;"),
            ", an AI and data consulting firm focused on building pragmatic, high-impact solutions. My experience ranges from being a Tech Lead at ",
            A("Media Distillery", href="https://mediadistillery.com",
              style="color: #9ca3af; text-decoration: underline;"),
            " to working as a freelance data scientist for ",
            #A("Eindsprint", href="https://eindsprint.nl", style="color: #9ca3af; text-decoration: underline;"),
            #" and",
            " the ",
            A("Dutch Chamber of Commerce", href="https://www.kvk.nl",
              style="color: #9ca3af; text-decoration: underline;"),
            ". I hold a degree in Artificial Intelligence and Philosophy.",
            cls="text-lg uk-text-muted",
        ),
        Div(
            A(
                Lucide("mail", cls="w-4 h-4 mr-2"),
                "Email me",
                href="mailto:bram.zijlstra@gmail.com",
                cls="uk-button uk-button-primary uk-margin-small-top uk-margin-small-right",
            ),
            A(
                Lucide("github", cls="w-4 h-4 mr-2 text-white"),
                "GitHub",
                href="https://github.com/skoetje",
                cls="uk-button uk-button-primary  uk-margin-small-right uk-margin-small-top",
            ),
            A(
                Lucide("twitter", cls="w-4 h-4 mr-2 text-white"),
                "Twitter",
                href="https://x.com/bramzijlstra",
                cls="uk-button uk-button-primary uk-margin-small-top uk-margin-small-right",
            ),
            A(
                Lucide("smile", cls="w-4 h-4 mr-2 text-white"),
                "Bluesky",
                href="https://bsky.app/profile/bramzijlstra.com",
                cls="uk-button uk-button-primary uk-margin-small-top",
            ),
        ),
        H2(
            "Some stuff I've written:",
            cls="text-3xl font-bold font-heading tracking-tight uk-margin-large-top",
        ),
        Div(
            *[BlogCard(post) for post in posts],
            cls="md:grid md:grid-cols-3 md:gap-4 uk-margin-top space-y-4 md:space-y-0",
        ),
        cls="uk-container uk-container-xl py-16",
    )


@rt("/posts/{slug}")
def get(slug: str):
    with open(f"posts/{slug}.md", "r") as file:
        content = file.read()

    post_content = content.split("---")[2]

    frontmatter = yaml.safe_load(content.split("---")[1])

    # Fetch Bluesky comments if URL is provided
    bluesky_comments_data = None
    bluesky_url = frontmatter.get("blueskyUrl")
    if bluesky_url:
        bluesky_comments_data = fetch_bluesky_comments(bluesky_url)

    twitter_headers = (
        Meta(name="twitter:card", content="summary"),
        Meta(name="twitter:title", content=frontmatter["title"]),
        Meta(
            name="twitter:description",
            content=frontmatter["excerpt"]
            if "excerpt" in frontmatter
            else "Blog by Bram Zijlstra",
        ),
        Meta(
            name="twitter:image",
            content=f"https://blog.bramzijlstra.com/images/{frontmatter['image']}"
            if "image" in frontmatter
            else "https://blog.bramzijlstra.com/images/og.png",
        ),
    )

    return (
        *twitter_headers,
        Title(f"{frontmatter['title']} - Bram Zijlstra Blog"),
        Div(
            A(
                Lucide("arrow-left", cls="w-4 h-4 text-black mr-2"),
                "Go Back",
                href="/",
                cls="absolute md:top-0 left-0 top-2 md:-ml-48 md:mt-16 uk-button uk-button-ghost",
            ),
            H1(
                frontmatter["title"],
                cls="text-4xl font-bold font-heading tracking-tight uk-margin-small-bottom",
            ),
            P(
                frontmatter["date"].strftime("%B %d, %Y"),
                " by Bram Zijlstra",
                cls="uk-text-muted uk-text-small uk-text-italic",
            ),
            Div(post_content, cls="marked prose mx-auto uk-margin-top"),
            # Add Bluesky comments section if URL provided
            BlueskyComments(bluesky_comments_data, bluesky_url) if bluesky_url else None,
            cls="uk-container max-w-[65ch] mx-auto relative py-16",
        ),
    )


serve()
