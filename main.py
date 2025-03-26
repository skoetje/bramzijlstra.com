from fasthtml.common import *

from lucide_fasthtml import Lucide

import yaml

from datetime import datetime

import os

from blog.embed_bluesky_comments import fetch_comments_html

plausible = Script(
    defer=True,
    data_domain="blog.mariusvach.com",
    src="https://plausible.io/js/script.js",
)
frankenui = (
    Link(
        rel="stylesheet",
        href="https://unpkg.com/franken-wc@0.1.0/dist/css/zinc.min.css",
    ),
    Script(src="https://cdn.jsdelivr.net/npm/uikit@3.21.6/dist/js/uikit.min.js"),
    Script(src="https://cdn.jsdelivr.net/npm/uikit@3.21.6/dist/js/uikit-icons.min.js"),
)
tailwind = (
    Link(rel="stylesheet", href="/app.css", type="text/css"),
    Link(rel="stylesheet", href="/tailwind.css", type="text/css"),
)
og_headers = (
    Meta(property="og:image", content="https://blog.mariusvach.com/images/og.png"),
)

app, rt = fast_app(
    pico=False,
    static_path="public",
    hdrs=(
        frankenui,
        *tailwind,
        plausible,
        Meta(name='google-site-verification', content='AHzT8BdRGuJ20gfBTqIHtWBGoleIfJ0e9gfjWwA_7HA'),
        *og_headers,
        MarkdownJS(),
        HighlightJS(langs=["python", "bash", "yaml", "json"], light="atom-one-dark"),
    ),
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
                    post["blueskyUrl"] = post.get("blueskyUrl")
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
            cls=f"uk-card {kwargs.pop('cls', '')}",
            **kwargs,
        )

    return Title("Bram Zijlstra"), Div(
        H1(
                "My name is Bram.",
            cls="text-4xl font-bold font-heading tracking-tight uk-margin-small-bottom",
        ),
        P(
            "I’m a machine learning engineer and co-founder of ",
            A("BQ Insights", href="https://bqinsights.nl", style="color: #9ca3af; text-decoration: underline;"),
            ", an AI and data consulting firm focused on building pragmatic, high-impact solutions. My experience ranges from leading teams as a Tech Lead at ",
            A("Media Distillery", href="https://mediadistillery.com",
              style="color: #9ca3af; text-decoration: underline;"),
            " to working as a freelancer for ",
            A("Eindsprint", href="https://eindsprint.nl", style="color: #9ca3af; text-decoration: underline;"),
            " and the ",
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
            "Some stuff I’ve written:",
            cls="text-3xl font-bold font-heading tracking-tight uk-margin-large-top",
        ),
        Div(
            *[BlogCard(post) for post in posts],
            cls="md:grid md:grid-cols-3 md:gap-4 uk-margin-top space-y-4 md:space-y-0",
        ),
        cls="uk-container uk-container-xl py-16",
    )

@rt("/comments/{slug}")
def bluesky_comments(slug: str):
    from fasthtml.common import Html

    with open(f"posts/{slug}.md", "r") as file:
        content = file.read()

    frontmatter = yaml.safe_load(content.split("---")[1])
    bluesky_url = frontmatter.get("blueskyUrl")

    if not bluesky_url:
        return Html("<div>No comments available.</div>", unsafe=True)

    html_output = fetch_comments_html(bluesky_url)
    return Html(html_output, unsafe=True)

@rt("/test-html")
def test_html():
    html_string = """
    <div class="bg-blue-100 text-blue-800 p-4 rounded">
        <strong>Note:</strong> This is a test of raw HTML rendering.
    </div>
    """
    from fasthtml.common import Html
    return Html(html_string, unsafe=True)


@rt("/posts/{slug}")
def get(slug: str):
    from fastapi.responses import HTMLResponse

    with open(f"posts/{slug}.md", "r") as file:
        content = file.read()

    post_content = content.split("---")[2]
    frontmatter = yaml.safe_load(content.split("---")[1])
    bluesky_comments_html = fetch_comments_html(frontmatter.get("blueskyUrl", ""))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{frontmatter['title']} - Bram Zijlstra Blog</title>
        <link rel="stylesheet" href="/app.css" />
        <link rel="stylesheet" href="/tailwind.css" />
    </head>
    <body class="bg-white text-black">
        <div class="uk-container max-w-[65ch] mx-auto py-16">
            <a href="/" class="text-blue-500 underline block mb-6">← Go back</a>
            <h1 class="text-4xl font-bold mb-2">{frontmatter['title']}</h1>
            <p class="text-sm text-gray-500 mb-8">{frontmatter['date'].strftime('%B %d, %Y')} by Bram Zijlstra</p>
            <div class="marked prose mb-12">{post_content}</div>
            <h2 class="text-2xl font-bold mb-4">Discussion</h2>
            {bluesky_comments_html}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

serve()
