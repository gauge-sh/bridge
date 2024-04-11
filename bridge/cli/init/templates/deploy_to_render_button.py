RENDER_BUTTON_TAG = "DEPLOY_TO_RENDER_BUTTON"


def as_html_comment(tag: str) -> str:
    return f"<!-- {tag} -->"


template = f"""# Bridge Deployment

{as_html_comment(RENDER_BUTTON_TAG)}
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
"""


def deploy_to_render_button_template():
    # No args for now, but we can templatize the github repo URL in the future
    return template


def button_exists_in_content(content: str) -> bool:
    return as_html_comment(RENDER_BUTTON_TAG) in content
