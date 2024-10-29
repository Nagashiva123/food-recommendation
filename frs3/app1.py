from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Load your dataset (adjust the path as necessary)
data = pd.read_csv('updated_food_data_500.csv')  # Ensure to use your actual dataset path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        name = request.form.get('name')
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        health_issue = request.form.get('health_issue')

        # Filter the data based on health issue
        filtered_data = data[data['Health_Issue'] == health_issue]

        # Get top 10 food recommendations
        recommendations = filtered_data.head(10)

        # Prepare data for visualizations
        calories = recommendations['Calories'].tolist()
        proteins = recommendations['Protein'].tolist()
        veg_nonveg_counts = recommendations['Veg_Non'].value_counts()
        restaurant_counts = recommendations['Restaurant'].value_counts()

        # Create visualizations
        pie_fig = px.pie(
            names=['Calories', 'Proteins'],
            values=[sum(calories), sum(proteins)],
            title='Total Calories vs Proteins for Recommended Foods',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        pie_chart_path = 'static/pie_chart.html'
        pio.write_html(pie_fig, file=pie_chart_path, auto_open=False)

        # Create Bar Graph for Restaurant Ratings
        restaurant_ratings = recommendations[['Restaurant', 'Rating']].drop_duplicates()
        bar_fig = px.bar(
            restaurant_ratings,
            x='Restaurant',
            y='Rating',
            title='Restaurant Ratings',
            color='Rating',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        bar_chart_path = 'static/bar_chart.html'
        pio.write_html(bar_fig, file=bar_chart_path, auto_open=False)

        # Create Pie Chart for Veg and Non-Veg Distribution
        veg_nonveg_fig = px.pie(
            names=veg_nonveg_counts.index,
            values=veg_nonveg_counts.values,
            title='Percentage of Veg and Non-Veg in Food Items',
            color_discrete_sequence=['#FFCC99', '#99FFCC']
        )
        veg_nonveg_chart_path = 'static/veg_nonveg_chart.html'
        pio.write_html(veg_nonveg_fig, file=veg_nonveg_chart_path, auto_open=False)

        # New Pie Chart for Restaurant Percentage
        restaurant_fig = px.pie(
            names=restaurant_counts.index,
            values=restaurant_counts.values,
            title='Percentage of Food Items by Restaurant',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        restaurant_chart_path = 'static/restaurant_chart.html'
        pio.write_html(restaurant_fig, file=restaurant_chart_path, auto_open=False)

        # Render results on a new page
        return render_template('results1.html', recommendations=recommendations.to_dict(orient='records'),
                               pie_chart_path=pie_chart_path, bar_chart_path=bar_chart_path,
                               veg_nonveg_chart_path=veg_nonveg_chart_path,
                               restaurant_chart_path=restaurant_chart_path)

    # GET request loads the form with health issue options
    health_issues = data['Health_Issue'].unique()
    return render_template('index1.html', health_issues=health_issues)

if __name__ == '__main__':
    app.run(debug=True)
