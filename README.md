The link to my dashboard is:
https://uc-dashboard-construction--lexi-he-cts4bjjdjnhyzk9veslj2g.streamlit.app/

# UC Admissions — Fall 2025

## Research Question

**Among freshman applicants from California public high schools in Fall 2025, how did admission rates vary across counties and UC campuses?**

## Methodology

This project uses the provided UC admissions dataset to examine freshman admission rates during **Fall 2025**.

First, the data was filtered to include only **freshman applicants from California public high schools** during Fall 2025. University wide aggregate records were excluded because the project focuses on individual UC campuses.

The data was then grouped by **county and UC campus**. For each county-campus combination, the total number of applicants and total number of admitted students were calculated.

The admission rate was calculated using:

**Admission Rate = Total Admitted Applicants ÷ Total Applicants × 100**

For example, if 500 students applied and 200 were admitted, the admission rate would be 40%.

## Interactive Visualization

The results are presented through an interactive Streamlit application. Users can select a **California county** and a **UC campus** to explore the corresponding historical admission rate, number of applicants, and number of admitted students.

The application also includes an interactive **3D visualization** in which the height of each county-campus combination represents its admission rate. Users can hover over the visualization to see additional information about applicants, admits, and schools.

A second comparison chart allows users to examine the admission rates of different UC campuses within a selected county.

## Important Note

The admission rates shown in this project represent **historical results from Fall 2025**. They should not be interpreted as a prediction of an individual student's chances of admission.
