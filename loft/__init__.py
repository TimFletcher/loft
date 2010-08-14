# To get a CSS dump of your custom style, run this
# from pygments.formatters import HtmlFormatter
# from pygments.styles.twilight import TwilightStyle (or wherever your style is)
# print HtmlFormatter(style=TwilightStyle).get_style_defs('.twilight')


# class RSVPForm(forms.ModelForm):
# 
#     class Meta:
#         model = Guest
# 
#     def __init__(self, *args, **kwargs):
#         super(RSVPForm, self).__init__(*args, **kwargs)
#         self.fields['attending_ceremony'] = forms.TypedChoiceField(
#             choices=Guest.CHOICES,
#             required=True,
#             widget=forms.RadioSelect)
# 
# # -*- coding: utf-8 -*-
# """
#     pygments.styles.twilight
#     ~~~~~~~~~~~~~~~~~~~~~~~~
# 
#     A clone of the Twilight style from TextMate.
# """
# 
# from pygments.style import Style
# from pygments.token import Keyword, Name, Comment, String, Error, \
#      Number, Operator, Generic, Whitespace
# 
# 
# class TwilightStyle(Style):
# 
#     background_color = "#141414"
#     default_style = "#F8F8F8"
# 
#     styles = {
#         Whitespace:                "#141414",
#         Comment:                   "italic #5F5A60",
# 
#         Keyword:                   "bold #CDA869",
#         Keyword.Pseudo:            "nobold #9B703F",
#         Keyword.Type:              "nobold",
# 
#         Operator:                  "#F8F8F8",
#         Operator.Word:             "bold #AA22FF",
# 
#         Name:                      "#7587A6",
#         Name.Builtin:              "#CDA869",
#         Name.Function:             "bold #9B703F",
#         Name.Class:                "bold #9B859D",
#         Name.Namespace:            "bold #9B859D",
#         Name.Variable:             "#7587A6",
#         Name.Constant:             "#9B859D",
#         Name.Entity:               "bold #CF6A4C",
#         Name.Attribute:            "#F9EE98",
#         Name.Tag:                  "bold #CDA869",
#         Name.Decorator:            "#7587A6",
# 
#         String:                    "#8F9D6A",
#         String.Doc:                "italic",
#         String.Interpol:           "bold #DAEFA3",
#         String.Escape:             "bold #F9EE98",
#         String.Regex:              "#E9C062",
#         String.Symbol:             "#CF6A4C",
#         Number:                    "#CF6A4C",
# 
#         Generic.Heading:           "bold #000080",
#         Generic.Subheading:        "bold #800080",
#         Generic.Deleted:           "bg:#420E09 #F8F8F8",
#         Generic.Inserted:          "bg:#253B22 #F8F8F8",
#         Generic.Error:             "bg:#B22518 #F8F8F8",
#         Generic.Emph:              "italic",
#         Generic.Strong:            "bold",
#         Generic.Prompt:            "bold #F8F8F8",
#         Generic.Output:            "#F8F8F8",
#         Generic.Traceback:         "#F8F8F8",
# 
#         Error:                     "border:#B22518"
#     }