import csv
import random
from faker import Faker

# Initialize faker for random names
fake = Faker()

# Configuration
NUM_STUDENTS = 200
DATA_FILE = 'data/selections.csv'
CLASSES = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b']
PROJECTS = [
    "Art Project", "Science Fair", "Drama Performance",
    "Music Band", "Robotics", "Gardening Club",
    "Debate Team", "Math Olympiad", "Creative Writing",
    "Sports Committee", "School Newspaper"
]


def generate_student_data():
    """Generate a single student's data with random choices"""
    name = fake.first_name() + " " + fake.last_name()
    student_class = random.choice(CLASSES)

    # Get 3 unique project choices in random order
    choices = random.sample(PROJECTS, 3)

    return {
        'Name': name,
        'Class': student_class,
        'Choice1': choices[0],
        'Choice2': choices[1],
        'Choice3': choices[2],
        'AssignedProject': ''  # Will be assigned by the system
    }


def generate_test_data(num_students):
    """Generate test data and write to CSV"""
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Class', 'Choice1', 'Choice2', 'Choice3', 'AssignedProject'])
        writer.writeheader()

        for _ in range(num_students):
            student = generate_student_data()
            writer.writerow(student)

    print(f"Generated {num_students} test student records in {DATA_FILE}")


if __name__ == '__main__':
    generate_test_data(NUM_STUDENTS)