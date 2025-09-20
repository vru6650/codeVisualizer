from typing import Callable, Dict, Union  # @UnusedImport

from thonny import get_workbench
from thonny.misc_utils import running_on_linux, running_on_mac_os, running_on_windows
from thonny.ui_utils import ems_to_pixels
from thonny.workbench import BasicUiThemeSettings, CompoundUiThemeSettings


def scale(value) -> float:
    # dimensions in this module were designed with a 1.67 scale
    return get_workbench().scale(value / 1.67)


def _treeview_settings() -> BasicUiThemeSettings:
    light_blue = "#ADD8E6"
    light_grey = "#D3D3D3"

    if running_on_linux() or running_on_mac_os():
        bg_sel_focus = light_blue
        fg_sel_focus = "black"
        fg_sel_notfocus = "black"
    else:
        bg_sel_focus = "SystemHighlight"
        fg_sel_focus = "SystemHighlightText"
        fg_sel_notfocus = "SystemWindowText"

    return {
        "Treeview": {
            "map": {
                "background": [
                    ("selected", "focus", bg_sel_focus),
                    ("selected", "!focus", light_grey),
                ],
                "foreground": [
                    ("selected", "focus", fg_sel_focus),
                    ("selected", "!focus", fg_sel_notfocus),
                ],
            },
            "layout": [
                # get rid of borders
                ("Treeview.treearea", {"sticky": "nswe"})
            ],
        },
        "treearea": {"configure": {"borderwidth": 0}},
    }


def _menubutton_settings() -> BasicUiThemeSettings:
    return {
        "TMenubutton": {
            "configure": {"padding": scale(14)},
            "layout": [
                ("Menubutton.dropdown", {"side": "right", "sticky": "ns"}),
                (
                    "Menubutton.button",
                    {
                        "children": [
                            # ('Menubutton.padding', {'children': [
                            ("Menubutton.label", {"sticky": ""})
                            # ], 'expand': '1', 'sticky': 'we'})
                        ],
                        "expand": "1",
                        "sticky": "nswe",
                    },
                ),
            ],
        }
    }


def _paned_window_settings() -> BasicUiThemeSettings:
    return {"Sash": {"configure": {"sashthickness": ems_to_pixels(0.6)}}}


def _menu_settings() -> BasicUiThemeSettings:
    return {"Menubar": {"configure": {"activeborderwidth": 0, "relief": "flat"}}}


def _text_settings() -> BasicUiThemeSettings:
    return {
        "Text": {
            "configure": {
                "background": "SystemWindow" if running_on_windows() else "white",
                "foreground": "SystemWindowText" if running_on_windows() else "black",
            }
        },
        "Syntax.Text": {"map": {"background": [("readonly", "Yellow")]}},
        "Gutter": {"configure": {"background": "#e0e0e0", "foreground": "#999999"}},
    }


def _link_settings() -> BasicUiThemeSettings:
    tip_background = "#b8c28d"
    tip_background = "systemInfoBackground"
    return {
        "Url.TLabel": {"configure": {"foreground": "DarkBlue"}},
        "Tip.TLabel": {"configure": {"background": tip_background, "foreground": "black"}},
        "Tip.TFrame": {"configure": {"background": tip_background}},
    }


def _button_notebook_settings() -> BasicUiThemeSettings:
    # Adapted from https://github.com/python/cpython/blob/2.7/Demo/tkinter/ttk/notebook_closebtn.py
    return {
        "closebutton": {
            "element create": (
                "image",
                "img_close",
                ("active", "pressed", "!disabled", "img_close_active"),
                ("active", "!disabled", "img_close_active"),
                {"padding": scale(2), "sticky": ""},
            )
        },
        "ButtonNotebook.TNotebook.Tab": {
            "layout": [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.focus",
                                            {
                                                "side": "left",
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        "Notebook.label",
                                                        {"side": "left", "sticky": ""},
                                                    )
                                                ],
                                            },
                                        ),
                                        ("Notebook.closebutton", {"side": "right", "sticky": ""}),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ]
        },
    }


def clam() -> BasicUiThemeSettings:
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    defaultfg = "#000000"
    disabledfg = "#999999"
    frame = "#dcdad5"
    window = "#ffffff"
    dark = "#cfcdc8"
    darker = "#bab5ab"
    darkest = "#9e9a91"
    lighter = "#eeebe7"
    selectbg = "#4a6984"
    selectfg = "#ffffff"
    altindicator = "#5895bc"
    disabledaltindicator = "#a0a0a0"

    return {
        ".": {
            "configure": {
                "background": frame,
                "foreground": defaultfg,
                "bordercolor": darkest,
                "darkcolor": dark,
                "lightcolor": lighter,
                "troughcolor": darker,
                "selectbackground": selectbg,
                "selectforeground": selectfg,
                "selectborderwidth": 0,
                "font": "TkDefaultFont",
            },
            "map": {
                "background": [("disabled", frame), ("active", lighter)],
                "foreground": [("disabled", disabledfg)],
                "selectbackground": [("!focus", darkest)],
                "selectforeground": [("!focus", "white")],
            },
        },
        "TButton": {
            "configure": {
                "anchor": "center",
                "width": scale(11),
                "padding": scale(5),
                "relief": "raised",
            },
            "map": {
                "background": [("disabled", frame), ("pressed", darker), ("active", lighter)],
                "lightcolor": [("pressed", darker)],
                "darkcolor": [("pressed", darker)],
                "bordercolor": [("alternate", "#000000")],
            },
        },
        "Toolbutton": {
            "configure": {"anchor": "center", "padding": scale(2), "relief": "flat"},
            "map": {
                "relief": [
                    ("disabled", "flat"),
                    ("selected", "sunken"),
                    ("pressed", "sunken"),
                    ("active", "raised"),
                ],
                "background": [("disabled", frame), ("pressed", darker), ("active", lighter)],
                "lightcolor": [("pressed", darker)],
                "darkcolor": [("pressed", darker)],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorbackground": "#ffffff",
                "indicatormargin": [scale(1), scale(1), scale(6), scale(1)],
                "padding": scale(2),
            },
            "map": {
                "indicatorbackground": [
                    ("pressed", frame),
                    ("!disabled", "alternate", altindicator),
                    ("disabled", "alternate", disabledaltindicator),
                    ("disabled", frame),
                ]
            },
        },
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton": {
            "configure": {
                "indicatorbackground": "#ffffff",
                "indicatormargin": [scale(1), scale(1), scale(6), scale(1)],
                "padding": scale(2),
            },
            "map": {
                "indicatorbackground": [
                    ("pressed", frame),
                    ("!disabled", "alternate", altindicator),
                    ("disabled", "alternate", disabledaltindicator),
                    ("disabled", frame),
                ]
            },
        },
        "TMenubutton": {"configure": {"width": scale(11), "padding": scale(5), "relief": "raised"}},
        "TEntry": {
            "configure": {"padding": scale(1), "insertwidth": scale(1)},
            "map": {
                "background": [("readonly", frame)],
                "bordercolor": [("focus", selectbg)],
                "lightcolor": [("focus", "#6f9dc6")],
                "darkcolor": [("focus", "#6f9dc6")],
            },
        },
        "TCombobox": {
            "configure": {
                "padding": [scale(4), scale(2), scale(2), scale(2)],
                "insertwidth": scale(1),
            },
            "map": {
                "background": [("active", lighter), ("pressed", lighter)],
                "fieldbackground": [("readonly", "focus", selectbg), ("readonly", frame)],
                "foreground": [("readonly", "focus", selectfg)],
                "arrowcolor": [("disabled", disabledfg)],
            },
        },
        "ComboboxPopdownFrame": {"configure": {"relief": "solid", "borderwidth": scale(1)}},
        "TSpinbox": {
            "configure": {"arrowsize": scale(10), "padding": [scale(2), 0, scale(10), 0]},
            "map": {"background": [("readonly", frame)], "arrowcolor": [("disabled", disabledfg)]},
        },
        "TNotebook.Tab": {
            "configure": {"padding": [scale(6), scale(2), scale(6), scale(2)]},
            "map": {
                "padding": [("selected", [scale(6), scale(4), scale(6), scale(4)])],
                "background": [("selected", frame), ("", darker)],
                "lightcolor": [("selected", lighter), ("", dark)],
            },
        },
        "Treeview": {
            "configure": {"background": window},
            "map": {
                "background": [
                    ("disabled", frame),
                    ("!disabled", "!selected", window),
                    ("selected", selectbg),
                ],
                "foreground": [
                    ("disabled", disabledfg),
                    ("!disabled", "!selected", defaultfg),
                    ("selected", selectfg),
                ],
            },
        },
        # Treeview heading
        "Heading": {
            "configure": {
                "font": "TkHeadingFont",
                "relief": "raised",
                "padding": [scale(3), scale(3), scale(3), scale(3)],
            }
        },
        "TLabelframe": {"configure": {"labeloutside": True, "labelmargins": [0, 0, 0, scale(4)]}},
        "TProgressbar": {"configure": {"background": frame}},
        "Sash": {"configure": {"sashthickness": ems_to_pixels(0.6), "gripcount": 10}},
    }


def vista() -> BasicUiThemeSettings:
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/xpTheme.tcl
    return {
        ".": {
            "configure": {
                "background": "SystemButtonFace",
                "foreground": "SystemWindowText",
                "selectbackground": "SystemHighlight",
                "selectforeground": "SystemHighlightText",
                "font": "TkDefaultFont",
            },
            "map": {"foreground": [("disabled", "SystemGrayText")]},
        },
        "TButton": {
            "configure": {"anchor": "center", "width": scale(11), "padding": [scale(1), scale(1)]}
        },
        "Toolbutton": {"configure": {"padding": [scale(4), scale(4)]}},
        "TCheckbutton": {"configure": {"padding": scale(2)}},
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton": {"configure": {"padding": scale(2)}},
        "TMenubutton": {"configure": {"padding": [scale(8), scale(4)]}},
        "TEntry": {
            "configure": {"padding": [scale(2), scale(2), scale(2), scale(4)]},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
            },
        },
        "TCombobox": {
            "configure": {"padding": scale(2)},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
                "foreground": [
                    ("disabled", "SystemGrayText"),
                    ("readonly", "focus", "SystemHighlightText"),
                ],
                "focusfill": [("readonly", "focus", "SystemHighlight")],
            },
        },
        "ComboboxPopdownFrame": {"configure": {"relief": "solid", "borderwidth": scale(1)}},
        "TSpinbox": {
            "configure": {"padding": [scale(2), 0, scale(14), 0]},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
            },
        },
        "TNotebook": {"configure": {"tabmargins": [scale(2), scale(2), scale(2), 0]}},
        "TNotebook.Tab": {
            "map": {"expand": [("selected", [scale(2), scale(2), scale(2), scale(2)])]}
        },
        "Treeview": {
            "configure": {"background": "SystemWindow"},
            "map": {
                "background": [
                    ("disabled", "SystemButtonFace"),
                    ("!disabled", "!selected", "SystemWindow"),
                    ("selected", "SystemHighlight"),
                ],
                "foreground": [
                    ("disabled", "SystemGrayText"),
                    ("!disabled", "!selected", "SystemWindowText"),
                    ("selected", "SystemHighlightText"),
                ],
            },
        },
        "Heading": {"configure": {"font": "TkHeadingFont", "relief": "raised"}},  # Treeview heading
        "TLabelframe.Label": {"configure": {"foreground": "#0046d5"}},
    }


def aqua() -> BasicUiThemeSettings:
    # https://github.com/tcltk/tk/blob/main/library/ttk/aquaTheme.tcl
    return {
        ".": {
            "configure": {
                "font": "TkDefaultFont",
                "background": "systemWindowBody",
                "foreground": "systemModelessDialogActiveText",
                "selectbackground": "systemHighlight",
                "selectforeground": "systemModelessDialogActiveText",
                "selectborderwidth": 0,
                "insertwidth": 1,
                "stipple": "",
            },
            "map": {
                "foreground": [
                    ("disabled", "systemModelessDialogInactiveText"),
                    ("background", "systemModelessDialogInactiveText"),
                ],
                "selectbackground": [
                    ("background", "systemHighlightSecondary"),
                    ("!focus", "systemHighlightSecondary"),
                ],
                "selectforeground": [
                    ("background", "systemModelessDialogInactiveText"),
                    ("!focus", "systemDialogActiveText"),
                ],
            },
        },
        "TButton": {"configure": {"anchor": "center", "width": "6"}},
        # "Toolbutton": {"configure": {"padding": 0}},
        "Toolbutton": {
            "configure": {"anchor": "center", "padding": scale(2), "relief": "flat"},
            "map": {
                "relief": [
                    ("disabled", "flat"),
                    ("selected", "sunken"),
                    ("pressed", "sunken"),
                    ("active", "raised"),
                ],
                "background": [("disabled", "gray"), ("pressed", "gray"), ("active", "gray")],
                "lightcolor": [("pressed", "red")],
                "darkcolor": [("pressed", "red")],
            },
            "layout": [
                (
                    "Toolbutton.padding",
                    {"sticky": "nswe", "children": [("Toolbutton.label", {"sticky": "nswe"})]},
                )
            ],
        },
        "TNotebook": {
            "configure": {"tabmargins": [10, 0], "tabposition": "n", "padding": [18, 8, 18, 17]}
        },
        "TNotebook.Tab": {"configure": {"padding": [12, 3, 12, 2]}},
        "TCombobox": {"configure": {"postoffset": [5, -2, -10, 0]}},
        "Heading": {"configure": {"font": "TkHeadingFont"}},
        "Treeview": {
            "map": {
                "background": [
                    ("disabled", "systemDialogBackgroundInactive"),
                    ("!disabled", "!selected", "systemWindowBody"),
                    ("selected", "background", "systemHighlightSecondary"),
                    ("selected", "systemHighlight"),
                ],
                "foreground": [
                    ("disabled", "systemModelessDialogInactiveText"),
                    ("!disabled", "!selected", "black"),
                    ("selected", "systemModelessDialogActiveText"),
                ],
            },
        },
        "TProgressbar": {"configure": {"period": 100, "maxphase": 255}},
        "Labelframe": {"configure": {"labeloutside": True, "labelmargins": [14, 0, 14, 4]}},
    }


def windows() -> CompoundUiThemeSettings:
    tip_background = "#bbbbbb"
    return [
        vista(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        _link_settings(),
        _button_notebook_settings(),
        {
            "Tip.TLabel": {"configure": {"background": tip_background, "foreground": "black"}},
            "Tip.TFrame": {"configure": {"background": tip_background}},
        },
        {
            "TNotebook": {
                "configure": {
                    # With tabmargins I can get a gray line below tab, which separates
                    # tab content from label
                    "tabmargins": [scale(2), scale(2), scale(2), scale(2)]
                }
            },
            "Tab": {"configure": {"padding": [scale(3), scale(1), scale(3), 0]}},
            "ButtonNotebook.TNotebook.Tab": {
                "configure": {"padding": (scale(4), scale(1), scale(1), 0)}
            },
            "TCombobox": {
                "map": {
                    "selectbackground": [
                        ("readonly", "!focus", "SystemWindow"),
                        ("readonly", "focus", "SystemHighlight"),
                    ],
                    "selectforeground": [
                        ("readonly", "!focus", "SystemWindowText"),
                        ("readonly", "focus", "SystemHighlightText"),
                    ],
                }
            },
            "Listbox": {
                "configure": {
                    "background": "SystemWindow",
                    "foreground": "SystemWindowText",
                    "disabledforeground": "SystemGrayText",
                    "highlightbackground": "SystemActiveBorder",
                    "highlightcolor": "SystemActiveBorder",
                    "highlightthickness": scale(1),
                }
            },
            "ViewBody.TFrame": {
                "configure": {
                    "background": "SystemButtonFace"  # to create the fine line below toolbar
                }
            },
            "ViewToolbar.TFrame": {"configure": {"background": "SystemWindow"}},
            "ViewToolbar.Toolbutton": {"configure": {"background": "SystemWindow"}},
            "ViewTab.TLabel": {
                "configure": {"background": "SystemWindow", "padding": [scale(5), 0]}
            },
            "ViewToolbar.TLabel": {
                "configure": {"background": "SystemWindow", "padding": [scale(5), 0]}
            },
            "ViewToolbar.Link.TLabel": {
                "configure": {"background": "SystemWindow", "padding": [scale(5), 0]}
            },
            "Active.ViewTab.TLabel": {
                "configure": {
                    # "font" : "BoldTkDefaultFont",
                    "relief": "sunken",
                    "borderwidth": scale(1),
                }
            },
            "Inactive.ViewTab.TLabel": {"map": {"relief": [("hover", "raised")]}},
        },
    ]


def enhanced_clam() -> CompoundUiThemeSettings:
    tip_background = "#bab5ab"
    return [
        clam(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        _link_settings(),
        {
            "Tip.TLabel": {"configure": {"background": tip_background, "foreground": "black"}},
            "Tip.TFrame": {"configure": {"background": tip_background}},
        },
        _button_notebook_settings(),
        {
            "ButtonNotebook.Tab": {
                "configure": {"padding": (scale(6), scale(4), scale(2), scale(3))}
            },
            "TScrollbar": {
                "configure": {
                    "gripcount": 0,
                    "arrowsize": scale(14),
                    # "arrowcolor" : "DarkGray"
                    # "width" : 99 # no effect
                }
            },
            "TCombobox": {
                "configure": {"arrowsize": scale(14)},
                "map": {
                    "selectbackground": [("readonly", "!focus", "#dcdad5")],
                    "selectforeground": [("readonly", "!focus", "#000000")],
                },
            },
            "TCheckbutton": {"configure": {"indicatorsize": scale(12)}},
            "TRadiobutton": {"configure": {"indicatorsize": scale(12)}},
            "Listbox": {
                "configure": {
                    "background": "white",
                    "foreground": "black",
                    "disabledforeground": "#999999",
                    "highlightbackground": "#4a6984",
                    "highlightcolor": "#4a6984",
                    "highlightthickness": scale(1),
                }
            },
            "ViewTab.TLabel": {"configure": {"padding": [scale(5), 0]}},
            "Active.ViewTab.TLabel": {
                "configure": {
                    # "font" : "BoldTkDefaultFont",
                    "relief": "sunken",
                    "borderwidth": scale(1),
                }
            },
            "Inactive.ViewTab.TLabel": {"map": {"relief": [("hover", "raised")]}},
        },
    ]


def enhanced_aqua() -> CompoundUiThemeSettings:
    return [
        _treeview_settings(),
        _menubutton_settings(),
        # _paned_window_settings(),
        _menu_settings(),
        {
            "TPanedWindow": {"configure": {"background": "systemDialogBackgroundActive"}},
            "TFrame": {"configure": {"background": "systemDialogBackgroundActive"}},
            "ViewTab.TLabel": {"configure": {"padding": [scale(5), 0]}},
            "Tab": {"map": {"foreground": [("selected", "systemSelectedTabTextColor")]}},
            "Active.ViewTab.TLabel": {
                "configure": {
                    # "font" : "BoldTkDefaultFont",
                    "relief": "sunken",
                    "borderwidth": scale(1),
                }
            },
            "Inactive.ViewTab.TLabel": {"map": {"relief": [("hover", "raised")]}},
        },
    ]


def modern_light() -> CompoundUiThemeSettings:
    accent = "#2563EB"
    accent_hover = "#1D4ED8"
    accent_pressed = "#1E40AF"
    surface = "#F5F6FA"
    surface_alt = "#E5E7EB"
    canvas = "#FFFFFF"
    border = "#D0D5DD"
    focus_border = "#A4C0F5"
    text_primary = "#111827"
    text_secondary = "#475467"
    muted = "#9AA4B2"
    tooltip_background = "#1F2937"
    tooltip_foreground = "#F8FAFC"

    return [
        {
            ".": {
                "configure": {
                    "background": surface,
                    "foreground": text_primary,
                    "bordercolor": border,
                    "darkcolor": surface,
                    "lightcolor": surface,
                    "troughcolor": surface_alt,
                    "selectbackground": accent,
                    "selectforeground": "#FFFFFF",
                    "font": "TkDefaultFont",
                },
                "map": {
                    "background": [("disabled", surface), ("active", surface_alt)],
                    "foreground": [("disabled", muted)],
                    "selectbackground": [("!focus", accent_hover)],
                    "selectforeground": [("!focus", "#FFFFFF")],
                },
            },
            "TFrame": {"configure": {"background": surface}},
            "TLabel": {"configure": {"background": surface, "foreground": text_primary}},
            "Secondary.TLabel": {"configure": {"foreground": text_secondary}},
            "Url.TLabel": {"configure": {"foreground": accent}},
            "Tip.TLabel": {
                "configure": {"foreground": tooltip_foreground, "background": tooltip_background}
            },
            "Tip.TFrame": {"configure": {"background": tooltip_background}},
            "TSeparator": {
                "configure": {"background": border, "borderwidth": 0, "relief": "flat"}
            },
            "TButton": {
                "configure": {
                    "background": accent,
                    "foreground": "#FFFFFF",
                    "bordercolor": accent,
                    "lightcolor": accent,
                    "darkcolor": accent,
                    "padding": [scale(8), scale(4)],
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("disabled", surface_alt),
                        ("pressed", accent_pressed),
                        ("active", accent_hover),
                    ],
                    "bordercolor": [("focus", focus_border)],
                    "foreground": [("disabled", "#FFFFFF")],
                },
            },
            "Toolbutton": {
                "configure": {
                    "background": surface,
                    "foreground": text_secondary,
                    "padding": [scale(6), scale(4)],
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("disabled", surface),
                        ("pressed", accent_pressed),
                        ("active", surface_alt),
                        ("selected", accent),
                    ],
                    "foreground": [
                        ("disabled", muted),
                        ("pressed", "#FFFFFF"),
                        ("selected", "#FFFFFF"),
                    ],
                },
            },
            "TMenubutton": {
                "configure": {
                    "background": canvas,
                    "foreground": text_secondary,
                    "bordercolor": border,
                    "lightcolor": border,
                    "darkcolor": border,
                    "padding": [scale(8), scale(4)],
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("disabled", canvas),
                        ("pressed", accent_pressed),
                        ("active", surface_alt),
                    ],
                    "foreground": [
                        ("disabled", muted),
                        ("pressed", "#FFFFFF"),
                        ("active", text_primary),
                    ],
                    "bordercolor": [("focus", accent)],
                },
            },
            "TCheckbutton": {
                "configure": {
                    "foreground": text_secondary,
                    "indicatorbackground": canvas,
                    "indicatorforeground": accent,
                    "padding": [scale(4), scale(2)],
                },
                "map": {
                    "foreground": [("disabled", muted), ("selected", text_primary)],
                    "indicatorbackground": [
                        ("disabled", surface_alt),
                        ("selected", accent),
                    ],
                    "indicatorforeground": [
                        ("disabled", muted),
                        ("selected", "#FFFFFF"),
                    ],
                },
            },
            "TRadiobutton": {
                "configure": {
                    "foreground": text_secondary,
                    "indicatorbackground": canvas,
                    "indicatorforeground": accent,
                    "padding": [scale(4), scale(2)],
                },
                "map": {
                    "foreground": [("disabled", muted), ("selected", text_primary)],
                    "indicatorbackground": [
                        ("disabled", surface_alt),
                        ("selected", accent),
                    ],
                    "indicatorforeground": [
                        ("disabled", muted),
                        ("selected", "#FFFFFF"),
                    ],
                },
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": canvas,
                    "foreground": text_primary,
                    "insertcolor": accent,
                    "lightcolor": border,
                    "darkcolor": border,
                    "bordercolor": border,
                    "padding": [scale(4), scale(4)],
                },
                "map": {
                    "fieldbackground": [("readonly", canvas)],
                    "bordercolor": [("focus", accent)],
                    "lightcolor": [("focus", accent)],
                    "darkcolor": [("focus", accent)],
                    "foreground": [("disabled", muted)],
                },
            },
            "TCombobox": {
                "configure": {
                    "background": canvas,
                    "fieldbackground": canvas,
                    "foreground": text_primary,
                    "selectbackground": canvas,
                    "selectforeground": text_primary,
                    "bordercolor": border,
                    "lightcolor": border,
                    "darkcolor": border,
                    "arrowcolor": text_secondary,
                    "padding": [scale(4), scale(2), scale(4), scale(2)],
                },
                "map": {
                    "background": [("active", canvas)],
                    "fieldbackground": [("readonly", canvas)],
                    "selectbackground": [("readonly", canvas)],
                    "selectforeground": [("readonly", text_primary)],
                    "foreground": [("disabled", muted)],
                    "arrowcolor": [("disabled", muted)],
                    "bordercolor": [("focus", accent)],
                },
            },
            "ComboboxPopdownFrame": {
                "configure": {
                    "borderwidth": scale(1),
                    "relief": "solid",
                    "background": canvas,
                    "bordercolor": border,
                }
            },
            "TSpinbox": {
                "configure": {
                    "background": canvas,
                    "fieldbackground": canvas,
                    "foreground": text_primary,
                    "arrowsize": scale(12),
                    "bordercolor": border,
                },
                "map": {
                    "fieldbackground": [("readonly", canvas)],
                    "foreground": [("disabled", muted)],
                    "arrowcolor": [("disabled", muted)],
                    "bordercolor": [("focus", accent)],
                },
            },
            "TNotebook": {
                "configure": {
                    "background": surface,
                    "bordercolor": border,
                    "tabmargins": [scale(4), scale(2), scale(4), 0],
                }
            },
            "AutomaticNotebook.TNotebook": {
                "configure": {"background": surface, "bordercolor": border}
            },
            "ButtonNotebook.TNotebook": {
                "configure": {"background": surface, "bordercolor": border}
            },
            "TNotebook.Tab": {
                "configure": {
                    "padding": [scale(10), scale(6)],
                    "background": surface,
                    "foreground": text_secondary,
                    "borderwidth": scale(1),
                    "bordercolor": surface,
                    "lightcolor": surface,
                    "darkcolor": surface,
                },
                "map": {
                    "background": [
                        ("selected", canvas),
                        ("!selected", surface),
                        ("disabled", surface),
                    ],
                    "foreground": [
                        ("selected", text_primary),
                        ("disabled", muted),
                    ],
                    "bordercolor": [
                        ("selected", accent),
                        ("focus", accent),
                        ("!selected", surface),
                    ],
                    "lightcolor": [
                        ("selected", accent),
                        ("!selected", surface),
                    ],
                    "darkcolor": [
                        ("selected", accent),
                        ("!selected", surface),
                    ],
                },
            },
            "ButtonNotebook.TNotebook.Tab": {
                "configure": {"padding": [scale(10), scale(4)]}
            },
            "Treeview": {
                "configure": {
                    "background": canvas,
                    "foreground": text_primary,
                    "fieldbackground": canvas,
                    "borderwidth": 0,
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("selected", "focus", accent),
                        ("selected", "!focus", accent_hover),
                    ],
                    "foreground": [
                        ("selected", "#FFFFFF"),
                        ("disabled", muted),
                    ],
                },
            },
            "Treeview.Heading": {
                "configure": {
                    "background": surface,
                    "foreground": text_secondary,
                    "borderwidth": scale(1),
                    "bordercolor": border,
                    "lightcolor": surface,
                    "darkcolor": surface,
                    "padding": [scale(6), scale(3)],
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("active", surface_alt),
                        ("pressed", accent_pressed),
                    ],
                    "foreground": [
                        ("active", text_primary),
                        ("pressed", "#FFFFFF"),
                    ],
                },
            },
            "TScrollbar": {
                "configure": {
                    "gripcount": 0,
                    "borderwidth": 0,
                    "relief": "flat",
                    "background": border,
                    "darkcolor": border,
                    "lightcolor": border,
                    "troughcolor": surface_alt,
                },
                "map": {
                    "background": [
                        ("disabled", border),
                        ("active", accent),
                        ("pressed", accent_pressed),
                    ],
                    "troughcolor": [("disabled", surface)],
                },
            },
            "Vertical.TScrollbar": {
                "layout": [
                    (
                        "Vertical.Scrollbar.trough",
                        {
                            "sticky": "ns",
                            "children": [
                                ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                            ],
                        },
                    )
                ]
            },
            "Horizontal.TScrollbar": {
                "layout": [
                    (
                        "Horizontal.Scrollbar.trough",
                        {
                            "sticky": "we",
                            "children": [
                                ("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                            ],
                        },
                    )
                ],
                "map": {
                    "background": [
                        ("disabled", border),
                        ("active", accent),
                        ("pressed", accent_pressed),
                    ],
                    "troughcolor": [("disabled", surface)],
                },
            },
            "Menubar": {
                "configure": {
                    "custom": 1 if running_on_windows() else 0,
                    "background": surface,
                    "foreground": text_secondary,
                    "activebackground": accent,
                    "activeforeground": "#FFFFFF",
                    "relief": "flat",
                }
            },
            "Menu": {
                "configure": {
                    "background": canvas,
                    "foreground": text_primary,
                    "selectcolor": accent,
                    "activebackground": accent,
                    "activeforeground": "#FFFFFF",
                    "borderwidth": 0,
                    "relief": "flat",
                }
            },
            "CustomMenubarLabel.TLabel": {
                "configure": {
                    "background": surface,
                    "foreground": text_secondary,
                    "padding": [scale(10), scale(4), 0, scale(10)],
                }
            },
            "Text": {
                "configure": {
                    "background": canvas,
                    "foreground": text_primary,
                    "insertbackground": accent,
                }
            },
            "Gutter": {
                "configure": {"background": surface_alt, "foreground": muted}
            },
            "Listbox": {
                "configure": {
                    "background": canvas,
                    "foreground": text_primary,
                    "selectbackground": accent,
                    "selectforeground": "#FFFFFF",
                    "disabledforeground": muted,
                    "highlightbackground": border,
                    "highlightcolor": accent,
                    "highlightthickness": scale(1),
                }
            },
            "ViewBody.TFrame": {"configure": {"background": canvas}},
            "ViewToolbar.TFrame": {"configure": {"background": surface}},
            "ViewToolbar.Toolbutton": {
                "configure": {
                    "background": surface,
                    "foreground": text_secondary,
                    "padding": [scale(6), scale(4)],
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("disabled", surface),
                        ("active", surface_alt),
                        ("pressed", accent_pressed),
                        ("selected", accent),
                    ],
                    "foreground": [
                        ("disabled", muted),
                        ("pressed", "#FFFFFF"),
                        ("selected", "#FFFFFF"),
                    ],
                },
            },
            "ViewToolbar.TLabel": {
                "configure": {"background": surface, "foreground": text_secondary}
            },
            "ViewTab.TLabel": {
                "configure": {
                    "background": surface,
                    "foreground": text_secondary,
                    "padding": [scale(8), scale(2)],
                },
                "map": {"background": [("hover", surface_alt)]},
            },
            "Active.ViewTab.TLabel": {
                "configure": {"background": canvas, "foreground": text_primary}
            },
            "Inactive.ViewTab.TLabel": {
                "configure": {"foreground": text_secondary}
            },
            "TProgressbar": {
                "configure": {
                    "background": accent,
                    "troughcolor": surface_alt,
                    "bordercolor": surface,
                }
            },
            "TScale": {
                "configure": {
                    "background": accent,
                    "troughcolor": surface_alt,
                    "borderwidth": 0,
                    "lightcolor": accent,
                    "darkcolor": accent,
                    "gripcount": 0,
                }
            },
            "Sash": {
                "configure": {
                    "background": border,
                    "borderwidth": 0,
                    "sashthickness": ems_to_pixels(0.5),
                    "gripcount": 0,
                }
            },
        },
        _paned_window_settings(),
        _menu_settings(),
        _link_settings(),
        _button_notebook_settings(),
    ]


def load_plugin() -> None:
    from tkinter import ttk

    original_themes = ttk.Style().theme_names()

    # load all base themes
    for name in original_themes:
        settings = {}  # type: Union[Dict, Callable[[], Dict]]
        if name == "clam":
            settings = clam
        elif name == "vista":
            settings = vista
        elif name == "aqua":
            settings = aqua

        get_workbench().add_ui_theme(name, None, settings)

    get_workbench().add_ui_theme(
        "Enhanced Clam",
        "clam",
        enhanced_clam,
        {"tab-close": "tab-close-clam", "tab-close-active": "tab-close-active-clam"},
    )

    if "vista" in original_themes:
        get_workbench().add_ui_theme("Windows", "vista", windows)

    if "aqua" in original_themes:
        get_workbench().add_ui_theme("Kind of Aqua", "aqua", enhanced_aqua)
