
# AI Usage Documentation

**Course:** COP4751 – Advanced Database Management  
**Project:** CareerPath IT  
**Student:** Jonathan Mirtil

## 1. AI Tools Used

**Cursor AI:** I primarily used Cursor AI to generate and organize the application's code, including Flask routes, MySQL database functions, HTML templates, CSS styling, and the Job Match feature.

**ChatGPT:** I also used ChatGPT for troubleshooting issues during development, including resolving Python dependency errors and fixing a CSS styling issue with the Delete buttons.

## 2. Key AI Prompts

### Prompt 1: Application Development

I instructed Cursor AI to build a full-stack web application using Python, Flask, MySQL, HTML, and CSS.

The application needed to include the four required database tables, full CRUD functionality, six required pages, and a working Job Match feature.

### Prompt 2: Job Description Skill Extraction

I requested a feature that allows users to paste a job description and identify technical skills mentioned in it.

The application also needed to allow users to review and correct the extracted skills before saving the job.

### Prompt 3: Skill Gap Analysis

I requested functionality that compares a user's current skills with the requirements of a saved job.

The application needed to calculate a match percentage, identify missing skills, and provide practical recommendations for developing those skills.

### Prompt 4: User Interface

I requested a professional corporate design with a light background, navy-blue navigation, organized forms, and a clean dashboard.

My goal was to create a useful application without unnecessary features.

## 3. What Worked Well

Cursor AI helped generate the initial application structure and organize the project into separate Python, HTML, CSS, and SQL files.

The Flask application was able to connect to MySQL after I configured the database connection and installed the necessary Python packages.

The job description skill extraction feature identified nine qualifications from a sample IT Help Desk job description.

The Job Match feature correctly calculated a 44% match when four of the nine qualifications were entered.

The application also identified missing skills and provided recommendations for improving those skills.

## 4. What I Personally Changed and Tested

I was responsible for configuring the development environment, connecting the database, testing the application, and making corrections when needed.

Some of the tasks I completed included:

- Configuring the Python development environment.
- Setting up the MySQL database connection.
- Creating the `careerpath_it` database using MySQL Workbench.
- Verifying that all four required tables were created.
- Installing the Python dependencies.
- Running the Flask application locally.
- Creating and viewing company and job records.
- Testing job description skill extraction.
- Testing the Job Match percentage calculation.
- Creating and updating job application records.
- Verifying that the dashboard statistics updated correctly.
- Creating and deleting contact records.
- Testing the deletion confirmation feature.
- Correcting the CSS styling for the Delete buttons.

One specific modification I made was updating the `.btn.danger` class in `style.css` so that the Delete button text displayed correctly.

## 5. Lessons Learned

This project helped me better understand how Flask, MySQL, HTML, and CSS work together in a full-stack web application.

I learned how to configure a MySQL database connection and how database tables use foreign keys to connect related information.

I also learned that having the correct Python packages installed is important. When I first tried to run the application, I encountered a missing module error and had to install the required dependencies.

Testing the Job Match feature helped me understand how the application calculates percentages and identifies missing technical skills.

I also learned that AI-generated code still needs to be reviewed and tested. For example, the Delete buttons had a styling issue that needed to be corrected.

Overall, this project gave me more hands-on experience with databases, Python, Flask, and troubleshooting.

## 6. Limitations and Future Improvements

One improvement I would like to make is preventing the application from recommending certifications users already possess.

Another improvement would be separating required skills from preferred qualifications when extracting information from job descriptions.

These improvements would make the Job Match results more accurate and useful.

The current version uses a local skill dictionary and curated recommendations instead of relying on a paid AI API.

## 7. Conclusion

CareerPath IT was developed with AI-assisted coding along with my own configuration, testing, and modifications.

The project helped me gain practical experience working with Flask, MySQL, database relationships, and web application troubleshooting.
