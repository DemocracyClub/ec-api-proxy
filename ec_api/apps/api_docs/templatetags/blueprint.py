from django import template
from django.template.loader import render_to_string

from apiblueprint_view import parser, dm
from apiblueprint_view.views import BASE_STYLES

register = template.Library()


def make_styles(styles=None):
    styles = BASE_STYLES
    if not isinstance(styles, dict):
        return styles
    for style in styles:
        if (
            style in styles
            and "class" in styles[style]
            and isinstance(styles[style]["class"], str)
        ):
            styles[style]["class"] += " " + styles[style]["class"]
    return styles


class InlineApibpParser(parser.ApibpParser):
    def __init__(
        self,
    ):
        super().__init__("")

    def parse_inline(self, content):
        apibp = content
        if self.process_includes:
            apibp = self._replace_includes(apibp)
        self.api = dm.parse(apibp)
        self._set_host()
        self._post_process(self.api[0])

        return self.api


def do_blueprint(parser, token):
    nodelist = parser.parse(("endblueprint",))
    parser.delete_first_token()
    return BlueprintNode(nodelist)


class BlueprintNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        parser = InlineApibpParser()
        value = self.nodelist.render(context)
        base_content = f"""FORMAT: 1A

{value}
        """

        return render_to_string(
            "api_docs/default_base.html",
            {
                "root": parser.parse_inline(base_content).content[0],
                "styles": make_styles(),
            },
        )


register.tag("blueprint", do_blueprint)
