
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------------
# UC ADMISSIONS | FALL 2025
# Interactive data challenge
# ------------------------------------------------------------

st.set_page_config(
    page_title="UC Admissions | Fall 2025",
    page_icon="UC",
    layout="wide"
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data(1).csv")

    data = df[
        (df["fall_term"] == 2025) &
        (df["school_type"] == "High Schools (Public)") &
        (df["campus"] != "Universitywide")
    ].copy()

    data = data.dropna(
        subset=["county", "campus", "applicants", "admits"]
    )

    # Aggregate first, then calculate the rate.
    # This gives each applicant equal weight rather than
    # giving every school equal weight.
    summary = (
        data.groupby(["county", "campus"], as_index=False)
        .agg(
            applicants=("applicants", "sum"),
            admits=("admits", "sum"),
            schools=("high_school", "nunique")
        )
    )

    summary["admission_rate"] = (
        summary["admits"] / summary["applicants"]
    )

    return summary


summary = load_data()

counties = sorted(summary["county"].unique())
campuses = sorted(summary["campus"].unique())

overall_applicants = summary["applicants"].sum()
overall_admits = summary["admits"].sum()
overall_rate = overall_admits / overall_applicants


# ---------- Styling ----------
st.markdown("""
<style>
    .main-title {
        font-family: Georgia, serif;
        font-size: 3.0rem;
        font-weight: 400;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .subtitle {
        color: #666;
        font-size: 1rem;
        margin-top: 4px;
        margin-bottom: 22px;
    }

    .section-title {
        font-family: Georgia, serif;
        font-size: 1.7rem;
        margin-top: 10px;
    }

    .rate {
        font-family: Georgia, serif;
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
    }

    .label {
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: .75rem;
    }

    .answer-box {
        border-left: 4px solid #222;
        padding: 12px 18px;
        margin: 12px 0 18px 0;
        background: #f7f7f7;
    }

    .small-note {
        color: #666;
        font-size: .86rem;
    }

    div[data-testid="stMetric"] {
        border-top: 1px solid #ddd;
        padding-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------
st.markdown('<div class="main-title">UC Admissions</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Fall 2025 | California public high schools</div>',
    unsafe_allow_html=True
)
st.divider()

st.markdown(
    '<div class="section-title">How did admission rates vary across counties and UC campuses?</div>',
    unsafe_allow_html=True
)

st.write(
    "Choose a county and campus to investigate the historical freshman "
    "admission rate in the provided Fall 2025 data."
)


# ---------- Selection ----------
left, right = st.columns(2)

with left:
    selected_county = st.selectbox("County", counties)

with right:
    selected_campus = st.selectbox("UC campus", campuses)


selected = summary[
    (summary["county"] == selected_county) &
    (summary["campus"] == selected_campus)
]

if selected.empty:
    st.warning("There is not enough data for this county-campus combination.")
    st.stop()

row = selected.iloc[0]

rate = row["admission_rate"]
rate_pct = rate * 100
difference = (rate - overall_rate) * 100


# ---------- Result ----------
st.divider()
st.markdown(
    f'<div class="label">{selected_county} County → UC {selected_campus}</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f'<div class="rate">{rate_pct:.1f}%</div>'
        '<div class="small-note">historical admission rate</div>',
        unsafe_allow_html=True
    )

with c2:
    st.metric("Applicants", f'{int(row["applicants"]):,}')

with c3:
    st.metric("Admitted", f'{int(row["admits"]):,}')

with c4:
    if difference >= 0:
        st.metric(
            "Vs. overall rate",
            f"+{difference:.1f} pts"
        )
    else:
        st.metric(
            "Vs. overall rate",
            f"{difference:.1f} pts"
        )

st.markdown(
    f"""
    <div class="answer-box">
    The historical admission rate for applicants from
    <b>{selected_county} County</b> applying to
    <b>UC {selected_campus}</b> was <b>{rate_pct:.1f}%</b>.
    The overall rate across the analyzed Fall 2025 population was
    <b>{overall_rate * 100:.1f}%</b>.
    </div>
    """,
    unsafe_allow_html=True
)


# ---------- Guessing game ----------
st.divider()
st.markdown('<div class="section-title">Make an estimate</div>', unsafe_allow_html=True)

st.write(
    "Before looking at the visualization, choose the range you think "
    "the admission rate falls into."
)

ranges = ["Under 20%", "20–40%", "40–60%", "60–80%", "Over 80%"]

def rate_range(value):
    pct = value * 100
    if pct < 20:
        return "Under 20%"
    if pct < 40:
        return "20–40%"
    if pct < 60:
        return "40–60%"
    if pct < 80:
        return "60–80%"
    return "Over 80%"

guess = st.radio(
    "Your estimate",
    ranges,
    horizontal=True,
    label_visibility="collapsed"
)

if st.button("Reveal rate", type="primary"):
    correct = rate_range(rate)

    if guess == correct:
        st.success(f"Correct range. The actual rate was {rate_pct:.1f}%.")
    else:
        st.info(
            f"The actual rate was {rate_pct:.1f}%, which falls in "
            f"the **{correct}** range."
        )

    st.caption(
        f"{int(row['admits']):,} admitted out of "
        f"{int(row['applicants']):,} applicants."
    )


# ---------- 3D overview ----------
st.divider()
st.markdown('<div class="section-title">The admissions landscape</div>', unsafe_allow_html=True)

st.write(
    "Each vertical bar represents a county-campus combination. "
    "Higher bars indicate higher historical admission rates. "
    "Hover over a bar to see applicants, admits, and the rate."
)

# Create a consistent 3D grid
plot_data = summary.copy()
county_order = counties
campus_order = campuses

county_index = {c: i for i, c in enumerate(county_order)}
campus_index = {c: i for i, c in enumerate(campus_order)}

fig = go.Figure()

for _, r in plot_data.iterrows():
    x = campus_index[r["campus"]]
    y = county_index[r["county"]]
    z = r["admission_rate"] * 100

    # Use a thin vertical line as a 3D "bar".
    # A marker at the top makes the value easier to see.
    fig.add_trace(
        go.Scatter3d(
            x=[x, x],
            y=[y, y],
            z=[0, z],
            mode="lines+markers",
            line=dict(width=12),
            marker=dict(size=[2, 7]),
            text=[
                f"<b>{r['county']} County</b><br>"
                f"UC {r['campus']}<br>"
                f"Admission rate: {z:.1f}%<br>"
                f"Applicants: {int(r['applicants']):,}<br>"
                f"Admitted: {int(r['admits']):,}<br>"
                f"Schools: {int(r['schools']):,}"
            ] * 2,
            hovertemplate="%{text}<extra></extra>",
            showlegend=False
        )
    )

# Highlight the selected combination with a larger point.
sx = campus_index[selected_campus]
sy = county_index[selected_county]
sz = rate_pct

fig.add_trace(
    go.Scatter3d(
        x=[sx],
        y=[sy],
        z=[sz],
        mode="markers",
        marker=dict(size=11, symbol="diamond"),
        text=[
            f"<b>SELECTED</b><br>"
            f"{selected_county} County → UC {selected_campus}<br>"
            f"Admission rate: {sz:.1f}%"
        ],
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    )
)

fig.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=10, b=0),
    scene=dict(
        xaxis=dict(
            title="UC campus",
            tickmode="array",
            tickvals=list(range(len(campus_order))),
            ticktext=campus_order,
            backgroundcolor="white",
            gridcolor="#dddddd"
        ),
        yaxis=dict(
            title="County",
            tickmode="array",
            tickvals=list(range(len(county_order))),
            ticktext=county_order,
            backgroundcolor="white",
            gridcolor="#dddddd"
        ),
        zaxis=dict(
            title="Admission rate (%)",
            range=[0, max(100, plot_data["admission_rate"].max() * 100 * 1.08)],
            backgroundcolor="white",
            gridcolor="#dddddd"
        ),
        bgcolor="white"
    ),
    paper_bgcolor="white",
    font=dict(family="Arial", size=12)
)

st.plotly_chart(fig, use_container_width=True)


# ---------- Comparison chart ----------
st.divider()
st.markdown('<div class="section-title">Compare campuses within this county</div>', unsafe_allow_html=True)

county_view = summary[
    summary["county"] == selected_county
].sort_values("admission_rate")

bar = go.Figure(
    go.Bar(
        x=county_view["admission_rate"] * 100,
        y=county_view["campus"],
        orientation="h",
        customdata=county_view[["applicants", "admits", "schools"]],
        hovertemplate=(
            "<b>UC %{y}</b><br>"
            "Admission rate: %{x:.1f}%<br>"
            "Applicants: %{customdata[0]:,}<br>"
            "Admitted: %{customdata[1]:,}<br>"
            "Schools: %{customdata[2]:,}"
            "<extra></extra>"
        )
    )
)

bar.update_layout(
    height=470,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Admission rate (%)",
    yaxis_title="",
    paper_bgcolor="white",
    plot_bgcolor="white"
)

st.plotly_chart(bar, use_container_width=True)


# ---------- Methodology ----------
st.divider()
st.markdown('<div class="section-title">Methodology</div>', unsafe_allow_html=True)

st.write(
    "The analysis uses Fall 2025 freshman admissions records for "
    "California public high schools. Records were grouped by county "
    "and UC campus. For each combination, total admits were divided "
    "by total applicants to calculate the admission rate. "
    "The interactive visualization lets users explore these "
    "historical rates rather than treating them as a prediction "
    "of an individual student's chance of admission."
)

st.caption(
    "Research question: Among freshman applicants from California public "
    "high schools in Fall 2025, how did admission rates vary across "
    "counties and UC campuses?"
)
