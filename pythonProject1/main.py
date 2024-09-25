from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# Load initial seat configuration
def load_seats():
    with open('seats.json', 'r') as f:
        return json.load(f)

# Save updated seat configuration
def save_seats(coach):
    with open('seats.json', 'w') as f:
        json.dump(coach, f)

@app.route('/')
def index():
    coach = load_seats()
    return render_template('index.html', seats=coach['seats'])

@app.route('/book', methods=['POST'])
def book_seats():
    num_seats = request.json['num_seats']
    booked_seats = []
    coach = load_seats()

    # Booking logic
    for row in coach['seats']:
        available_count = 0
        start_index = -1
        for i in range(len(row['seats'])):
            if row['seats'][i] == 0:  # Seat available
                if available_count == 0:
                    start_index = i
                available_count += 1
                if available_count == num_seats:
                    # Book the seats
                    for j in range(start_index, start_index + num_seats):
                        row['seats'][j] = 1
                    booked_seats = [(row['row'], j + 1) for j in range(start_index, start_index + num_seats)]
                    break
            else:
                available_count = 0
                start_index = -1

        if booked_seats:
            break

    if not booked_seats:
        # If not enough contiguous seats found, search for nearby seats
        for row in coach['seats']:
            available_seats = [i for i in range(len(row['seats'])) if row['seats'][i] == 0]
            if len(available_seats) >= num_seats:
                booked_seats = [(row['row'], seat + 1) for seat in available_seats[:num_seats]]
                for seat in available_seats[:num_seats]:
                    row['seats'][seat] = 1
                break

    # Save updated seat configuration
    save_seats(coach)

    return jsonify(booked_seats)

if __name__ == '__main__':
    app.run(debug=True)
