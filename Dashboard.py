# ============================================================
# UC ADMISSIONS — FALL 2025
# Interactive admission-rate challenge
# ============================================================

import pandas as pd
import random
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output


# ------------------------------------------------------------
# 1. LOAD THE DATA
# ------------------------------------------------------------

FILE_NAME = "dashboard_data(1).csv"

df = pd.read_csv(FILE_NAME)


# ------------------------------------------------------------
# 2. FILTER THE DATA
#
# Population:
# Freshman applicants from California public high schools
# Time window:
# Fall 2025
# ------------------------------------------------------------

data = df[
    (df["fall_term"] == 2025) &
    (df["school_type"] == "High Schools (Public)") &
    (df["campus"] != "Universitywide")
].copy()


# Remove records where the variables needed for the analysis
# are missing.

data = data.dropna(
    subset=["county", "campus", "applicants", "admits"]
)


# ------------------------------------------------------------
# 3. AGGREGATE BY COUNTY + UC CAMPUS
# ------------------------------------------------------------
#
# We add applicants and admits first, then calculate the rate.
#
# Admission rate =
# total admits / total applicants
#
# This prevents a small school and a large school from
# receiving the same weight.
# ------------------------------------------------------------

summary = (
    data
    .groupby(["county", "campus"], as_index=False)
    .agg(
        applicants=("applicants", "sum"),
        admits=("admits", "sum"),
        schools=("high_school", "nunique")
    )
)

summary["admission_rate"] = (
    summary["admits"] / summary["applicants"]
)


# ------------------------------------------------------------
# 4. OVERALL FALL 2025 RATE
# ------------------------------------------------------------

overall_applicants = summary["applicants"].sum()
overall_admits = summary["admits"].sum()

overall_rate = overall_admits / overall_applicants


# ------------------------------------------------------------
# 5. OPTIONS FOR THE APP
# ------------------------------------------------------------

counties = sorted(summary["county"].unique())
campuses = sorted(summary["campus"].unique())


# ------------------------------------------------------------
# 6. CSS / VISUAL DESIGN
# ------------------------------------------------------------
#
# Simple, flat design rather than lots of cards, gradients,
# emojis, and rounded UI elements.
# ------------------------------------------------------------

display(HTML("""
<style>

body {
    font-family: Arial, Helvetica, sans-serif;
}

.uc-title {
    font-family: Georgia, serif;
    font-size: 36px;
    font-weight: normal;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}

.uc-subtitle {
    color: #555;
    font-size: 15px;
    margin-bottom: 25px;
}

.uc-rule {
    border: none;
    border-top: 2px solid #222;
    margin: 10px 0 25px 0;
}

.section-title {
    font-family: Georgia, serif;
    font-size: 23px;
    margin-top: 15px;
    margin-bottom: 8px;
}

.question {
    font-family: Georgia, serif;
    font-size: 25px;
    line-height: 1.3;
    margin: 18px 0;
}

.big-number {
    font-family: Georgia, serif;
    font-size: 52px;
    font-weight: bold;
    margin: 8px 0;
}

.small-label {
    color: #666;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stat-row {
    display: flex;
    gap: 45px;
    margin: 22px 0;
}

.stat-number {
    font-family: Georgia, serif;
    font-size: 25px;
    font-weight: bold;
}

.explanation {
    border-left: 3px solid #222;
    padding-left: 15px;
    margin: 20px 0;
    color: #444;
    line-height: 1.5;
}

.correct {
    font-size: 20px;
    font-weight: bold;
    margin: 12px 0;
}

.incorrect {
    font-size: 20px;
    font-weight: bold;
    margin: 12px 0;
}

.progress {
    color: #666;
    font-size: 14px;
    margin-bottom: 15px;
}

</style>
"""))


# ------------------------------------------------------------
# 7. TITLE
# ------------------------------------------------------------

display(HTML("""
<div class="uc-title">UC Admissions</div>

<div class="uc-subtitle">
    A Fall 2025 data challenge
</div>

<hr class="uc-rule">

<div class="explanation">
    How well can you estimate the historical freshman
    admission rate for applicants from different California
    counties applying to different UC campuses?
</div>
"""))


# ------------------------------------------------------------
# 8. COUNTY + CAMPUS SELECTION
# ------------------------------------------------------------

county_dropdown = widgets.Dropdown(
    options=counties,
    description="County",
    layout=widgets.Layout(width="420px"),
    style={"description_width": "100px"}
)

campus_dropdown = widgets.Dropdown(
    options=campuses,
    description="UC campus",
    layout=widgets.Layout(width="420px"),
    style={"description_width": "100px"}
)

start_button = widgets.Button(
    description="Start challenge",
    button_style="",
    layout=widgets.Layout(width="180px", height="38px")
)

display(county_dropdown)
display(campus_dropdown)
display(start_button)


# ------------------------------------------------------------
# 9. GAME OUTPUT AREA
# ------------------------------------------------------------

game_output = widgets.Output()

display(game_output)


# ------------------------------------------------------------
# 10. GAME VARIABLES
# ------------------------------------------------------------

score = 0
round_number = 0
total_rounds = 5

current_data = None


# ------------------------------------------------------------
# 11. ADMISSION-RATE CATEGORIES
# ------------------------------------------------------------

rate_ranges = [
    "Under 20%",
    "20–40%",
    "40–60%",
    "60–80%",
    "Over 80%"
]


def get_rate_range(rate):

    rate = rate * 100

    if rate < 20:
        return "Under 20%"

    elif rate < 40:
        return "20–40%"

    elif rate < 60:
        return "40–60%"

    elif rate < 80:
        return "60–80%"

    else:
        return "Over 80%"


# ------------------------------------------------------------
# 12. START THE GAME
# ------------------------------------------------------------

def start_game(button):

    global score
    global round_number

    score = 0
    round_number = 0

    next_round()


# ------------------------------------------------------------
# 13. START A NEW ROUND
# ------------------------------------------------------------

def next_round():

    global round_number
    global current_data

    round_number += 1

    # If all rounds are finished
    if round_number > total_rounds:

        show_final_score()
        return


    # --------------------------------------------------------
    # Use the county + campus selected by the user.
    # --------------------------------------------------------

    selected_county = county_dropdown.value
    selected_campus = campus_dropdown.value

    match = summary[
        (summary["county"] == selected_county) &
        (summary["campus"] == selected_campus)
    ]


    # --------------------------------------------------------
    # If there isn't enough information for that combination,
    # choose a different valid combination.
    # --------------------------------------------------------

    if len(match) == 0:

        valid_combinations = summary[
            ["county", "campus"]
        ].drop_duplicates()

        random_choice = valid_combinations.sample(1).iloc[0]

        selected_county = random_choice["county"]
        selected_campus = random_choice["campus"]

        county_dropdown.value = selected_county
        campus_dropdown.value = selected_campus

        match = summary[
            (summary["county"] == selected_county) &
            (summary["campus"] == selected_campus)
        ]


    current_data = match.iloc[0]


    # --------------------------------------------------------
    # Display the question
    # --------------------------------------------------------

    with game_output:

        clear_output(wait=True)

        display(HTML(f"""

        <div class="progress">
            ROUND {round_number} OF {total_rounds}
        </div>

        <div class="section-title">
            Your estimate
        </div>

        <div class="question">

            Applicants from <b>{current_data["county"]} County</b>
            applied to <b>UC {current_data["campus"]}</b>.

            <br><br>

            What was the historical admission rate?

        </div>

        """))


        # ----------------------------------------------------
        # Guess buttons
        # ----------------------------------------------------

        buttons = []

        for rate_range in rate_ranges:

            button = widgets.Button(
                description=rate_range,
                layout=widgets.Layout(
                    width="150px",
                    height="40px"
                )
            )

            button.on_click(
                lambda b, guess=rate_range:
                check_answer(guess)
            )

            buttons.append(button)


        display(
            widgets.HBox(
                buttons,
                layout=widgets.Layout(
                    justify_content="center"
                )
            )
        )


# ------------------------------------------------------------
# 14. CHECK THE PLAYER'S ANSWER
# ------------------------------------------------------------

def check_answer(guess):

    global score

    actual_rate = current_data["admission_rate"]

    correct_range = get_rate_range(actual_rate)

    if guess == correct_range:

        score += 1
        result_text = "Correct."
        result_class = "correct"

    else:

        result_text = "Not quite."
        result_class = "incorrect"


    # --------------------------------------------------------
    # Difference from overall rate
    # --------------------------------------------------------

    difference = (actual_rate - overall_rate) * 100

    if difference > 0:

        comparison = (
            f"{difference:.1f} percentage points "
            f"above the overall rate"
        )

    elif difference < 0:

        comparison = (
            f"{abs(difference):.1f} percentage points "
            f"below the overall rate"
        )

    else:

        comparison = "equal to the overall rate"


    # --------------------------------------------------------
    # Display answer
    # --------------------------------------------------------

    with game_output:

        clear_output(wait=True)

        display(HTML(f"""

        <div class="progress">
            ROUND {round_number} OF {total_rounds}
        </div>

        <div class="{result_class}">
            {result_text}
        </div>

        <div class="section-title">
            {current_data["county"]} County → UC {current_data["campus"]}
        </div>

        <div class="small-label">
            Historical freshman admission rate
        </div>

        <div class="big-number">
            {actual_rate * 100:.1f}%
        </div>

        <div class="stat-row">

            <div>
                <div class="small-label">Applicants</div>
                <div class="stat-number">
                    {int(current_data["applicants"]):,}
                </div>
            </div>

            <div>
                <div class="small-label">Admitted</div>
                <div class="stat-number">
                    {int(current_data["admits"]):,}
                </div>
            </div>

            <div>
                <div class="small-label">Schools represented</div>
                <div class="stat-number">
                    {int(current_data["schools"]):,}
                </div>
            </div>

        </div>

        <div class="explanation">

            Your guess: <b>{guess}</b><br>
            Correct range: <b>{correct_range}</b><br><br>

            The selected rate was
            <b>{comparison}</b>.

            The overall Fall 2025 rate in this analysis was
            <b>{overall_rate * 100:.1f}%</b>.

        </div>

        """))


        # ----------------------------------------------------
        # Continue button
        # ----------------------------------------------------

        if round_number < total_rounds:

            next_button = widgets.Button(
                description="Next question",
                layout=widgets.Layout(
                    width="160px",
                    height="38px"
                )
            )

            next_button.on_click(
                lambda b: next_round()
            )

            display(next_button)

        else:

            finish_button = widgets.Button(
                description="See final score",
                layout=widgets.Layout(
                    width="160px",
                    height="38px"
                )
            )

            finish_button.on_click(
                lambda b: show_final_score()
            )

            display(finish_button)


# ------------------------------------------------------------
# 15. FINAL SCORE
# ------------------------------------------------------------

def show_final_score():

    with game_output:

        clear_output(wait=True)

        if score == 5:

            message = "You got every admission-rate range right."

        elif score >= 3:

            message = (
                "You had a good read on the differences "
                "across the data."
            )

        else:

            message = (
                "The results show why comparing the data "
                "across counties and campuses can be useful."
            )


        display(HTML(f"""

        <div class="section-title">
            Challenge complete
        </div>

        <div class="big-number">
            {score} / {total_rounds}
        </div>

        <p style="font-size:18px;">
            {message}
        </p>

        <div class="explanation">

            This game used Fall 2025 freshman admissions data
            from California public high schools.

            The admission rate was calculated as:

            <br><br>

            <b>
            total admitted applicants ÷ total applicants
            </b>

            <br><br>

            The game compares these rates by county and
            UC campus.

        </div>

        """))


        # ----------------------------------------------------
        # Button to open the data explorer
        # ----------------------------------------------------

        explore_button = widgets.Button(
            description="Explore the data",
            layout=widgets.Layout(
                width="180px",
                height="38px"
            )
        )

        explore_button.on_click(
            lambda b: show_explorer()
        )

        display(explore_button)


# ------------------------------------------------------------
# 16. DATA EXPLORER
# ------------------------------------------------------------

def show_explorer():

    with game_output:

        clear_output(wait=True)

        display(HTML("""

        <div class="section-title">
            Explore the data
        </div>

        <p>
            Choose a county and campus to see the corresponding
            Fall 2025 freshman admission rate.
        </p>

        """))


        explorer_county = widgets.Dropdown(
            options=counties,
            description="County",
            layout=widgets.Layout(width="420px"),
            style={"description_width": "100px"}
        )


        explorer_campus = widgets.Dropdown(
            options=campuses,
            description="UC campus",
            layout=widgets.Layout(width="420px"),
            style={"description_width": "100px"}
        )


        explore_button = widgets.Button(
            description="Show result",
            layout=widgets.Layout(
                width="160px",
                height="38px"
            )
        )


        explorer_output = widgets.Output()


        display(explorer_county)
        display(explorer_campus)
        display(explore_button)
        display(explorer_output)


        def update_explorer(button):

            with explorer_output:

                clear_output(wait=True)

                result = summary[
                    (summary["county"] == explorer_county.value) &
                    (summary["campus"] == explorer_campus.value)
                ]


                if len(result) == 0:

                    display(HTML("""
                    <p>
                        There is not enough data for this
                        county-campus combination.
                    </p>
                    """))

                    return


                row = result.iloc[0]

                rate = row["admission_rate"] * 100

                difference = (
                    row["admission_rate"] - overall_rate
                ) * 100


                if difference >= 0:

                    comparison = (
                        f"{difference:.1f} percentage points "
                        f"above the overall rate"
                    )

                else:

                    comparison = (
                        f"{abs(difference):.1f} percentage points "
                        f"below the overall rate"
                    )


                display(HTML(f"""

                <hr class="uc-rule">

                <div class="small-label">
                    {row["county"]} County → UC {row["campus"]}
                </div>

                <div class="big-number">
                    {rate:.1f}%
                </div>

                <p>
                    historical freshman admission rate
                </p>

                <div class="stat-row">

                    <div>
                        <div class="small-label">
                            Applicants
                        </div>

                        <div class="stat-number">
                            {int(row["applicants"]):,}
                        </div>
                    </div>


                    <div>
                        <div class="small-label">
                            Admitted
                        </div>

                        <div class="stat-number">
                            {int(row["admits"]):,}
                        </div>
                    </div>


                    <div>
                        <div class="small-label">
                            Schools
                        </div>

                        <div class="stat-number">
                            {int(row["schools"]):,}
                        </div>
                    </div>

                </div>

                <div class="explanation">

                    Compared with the overall rate of
                    <b>{overall_rate * 100:.1f}%</b>,
                    this combination was
                    <b>{comparison}</b>.

                </div>

                """))


        explore_button.on_click(update_explorer)


# ------------------------------------------------------------
# 17. CONNECT START BUTTON
# ------------------------------------------------------------

start_button.on_click(start_game)


# ------------------------------------------------------------
# 18. METHODOLOGY NOTE
# ------------------------------------------------------------

display(HTML("""

<hr class="uc-rule">

<div class="section-title">
    Methodology
</div>

<p style="max-width:800px; line-height:1.6; color:#444;">

The analysis uses Fall 2025 freshman admissions records for
California public high schools. Applicants and admits were
summed within each county and UC campus, and the admission
rate was calculated as total admits divided by total applicants.
The interactive challenge allows users to compare these
historical rates across different county and campus combinations.

</p>

"""))
