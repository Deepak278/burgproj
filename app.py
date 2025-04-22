from flask import Flask, render_template, request, redirect, url_for, session, make_response
import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
MAX_STUDENTS_PER_PROJECT = 20
PROJECTS = [
    "Art Project", "Science Fair", "Drama Performance",
    "Music Band", "Robotics", "Gardening Club",
    "Debate Team", "Math Olympiad", "Creative Writing",
    "Sports Committee", "School Newspaper"
]
CLASSES = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b']

# Data storage
DATA_FILE = 'data/selections.csv'


def initialize_data():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Class', 'Choice1', 'Choice2', 'Choice3', 'AssignedProject'])


def read_selections():
    selections = []
    with open(DATA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            selections.append(row)
    return selections


def write_selection(student_data):
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            student_data['name'],
            student_data['class'],
            student_data['choice1'],
            student_data['choice2'],
            student_data['choice3'],
            ''  # Assigned project initially empty
        ])


def assign_projects():
    selections = read_selections()
    project_groups = {project: [] for project in PROJECTS}

    # Assign students to their first available choice
    for student in selections:
        assigned = False
        for choice in [student['Choice1'], student['Choice2'], student['Choice3']]:
            if len(project_groups[choice]) < MAX_STUDENTS_PER_PROJECT:
                project_groups[choice].append(f"{student['Name']}-{student['Class']}")
                assigned = True
                break

        if not assigned:
            # If all choices are full, assign to first available project
            for project in PROJECTS:
                if len(project_groups[project]) < MAX_STUDENTS_PER_PROJECT:
                    project_groups[project].append(f"{student['Name']}-{student['Class']}")
                    break

    return project_groups


@app.route('/')
def home():
    return render_template('home.html', projects=PROJECTS, classes=CLASSES)


@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        # Save student's choices
        student_data = {
            'name': request.form['name'],
            'class': request.form['class'],
            'choice1': request.form['choice1'],
            'choice2': request.form['choice2'],
            'choice3': request.form['choice3']
        }
        write_selection(student_data)
        return render_template('student.html',
                               message="Thank you! Your project choices have been submitted.",
                               projects=PROJECTS,
                               classes=CLASSES)

    return render_template('student.html', projects=PROJECTS, classes=CLASSES)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == 'admin123':  # Change this password for production
            session['admin'] = True
            return redirect(url_for('admin_view'))
        else:
            return render_template('admin.html', error="Incorrect password")

    return render_template('admin.html')


@app.route('/admin/view')
def admin_view():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    project_groups = assign_projects()
    return render_template('admin_view.html', project_groups=project_groups)


@app.route('/admin/export/csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    project_groups = assign_projects()

    # Create CSV response
    output = []
    for project, students in project_groups.items():
        output.append([project, ", ".join(students)])

    # Generate CSV
    csv_data = "Project,Students\n"
    for row in output:
        csv_data += f'"{row[0]}","{row[1]}"\n'

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=project_assignments.csv"
    response.headers["Content-type"] = "text/csv"
    return response


@app.route('/admin/export/pdf')
def export_pdf():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    project_groups = assign_projects()

    # Create PDF
    filename = "project_assignments.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Prepare data for PDF table
    data = [["Project", "Students"]]
    for project, students in project_groups.items():
        data.append([project, ", ".join(students)])

    # Create table
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    elements.append(table)

    # Build PDF
    doc.build(elements)

    # Return PDF as download
    with open(filename, 'rb') as f:
        response = make_response(f.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    # Clean up
    os.remove(filename)

    return response


if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)