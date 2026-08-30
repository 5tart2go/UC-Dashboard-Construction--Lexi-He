# UC Admissions — Fall 2025

Interactive Streamlit data visualization for the UC admissions data challenge.

## Research question

Among freshman applicants from California public high schools in Fall 2025, how did admission rates vary across counties and UC campuses?

## Methodology

The app filters the provided data to Fall 2025 and California public high schools, excludes the Universitywide aggregate, groups records by county and UC campus, and calculates:

Admission rate = total admitted applicants / total applicants

The app includes:
- County and UC campus selectors
- Historical admission-rate result
- Applicant/admit counts
- A guessing component
- Interactive 3D county × campus visualization
- Campus comparison chart
- Methodology section

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The CSV file must be in the same folder as `app.py` and named:

`dashboard_data(1).csv`
