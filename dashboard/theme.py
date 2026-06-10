import plotly.io as pio

F1_COLORS = {
    "background": "#0d0d0d",
    "text": "#e6e6e6",
    "accent": "#ff1e00",
    "secondary": "#1f77b4",
    "grid": "#333333"
}

def apply_f1_theme():
    pio.templates["f1"] = pio.templates["plotly_dark"]

    pio.templates["f1"].layout.update(
        {
            "paper_bgcolor": F1_COLORS["background"],
            "plot_bgcolor": F1_COLORS["background"],
            "font": {"color": F1_COLORS["text"], "family": "Helvetica"},
            "title": {"font": {"size": 22, "color": F1_COLORS["accent"]}},
            "xaxis": {
                "gridcolor": F1_COLORS["grid"],
                "zerolinecolor": F1_COLORS["grid"],
            },
            "yaxis": {
                "gridcolor": F1_COLORS["grid"],
                "zerolinecolor": F1_COLORS["grid"],
            },
            "colorway": [
                "#ff1e00", "#1f77b4", "#2ca02c", "#d62728",
                "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
            ],
            "legend": {
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": F1_COLORS["grid"],
                "borderwidth": 0
            }
        }
    )

    pio.templates.default = "f1"
