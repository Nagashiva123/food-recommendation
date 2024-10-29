from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('expanded_food_data.csv')

# Fill missing values in Health_Issue
data['Health_Issue'] = data['Health_Issue'].fillna('General')

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
        # 1. Pie chart for calories and proteins
        calories = recommendations['Calories'].tolist()
        proteins = recommendations['Protein'].tolist()
        veg_nonveg_counts = recommendations['Veg_Non'].value_counts()

        # Create pie chart for Calories vs Proteins
        pie_fig = px.pie(
            names=['Calories', 'Proteins'],
            values=[sum(calories), sum(proteins)],
            title='Total Calories vs Proteins for Recommended Foods',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )
        pie_chart_path = 'static/pie_chart.html'
        pio.write_html(pie_fig, file=pie_chart_path, auto_open=False)

        # 2. Bar graph for restaurant ratings
        restaurant_ratings = recommendations[['Restaurant', 'Rating']].drop_duplicates()
        
        # Create bar graph for Restaurant Ratings
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

        # 3. Pie chart for Veg vs Non-Veg percentages
        veg_nonveg_fig = px.pie(
            names=veg_nonveg_counts.index,
            values=veg_nonveg_counts.values,
            title='Percentage of Veg and Non-Veg in Food Items',
            color_discrete_sequence=['#FFCC99', '#99FFCC']
        )
        veg_nonveg_chart_path = 'static/veg_nonveg_chart.html'
        pio.write_html(veg_nonveg_fig, file=veg_nonveg_chart_path, auto_open=False)

        return render_template('index.html', recommendations=recommendations.to_dict(orient='records'),
                               pie_chart_path=pie_chart_path, bar_chart_path=bar_chart_path,
                               veg_nonveg_chart_path=veg_nonveg_chart_path)

    # GET request loads the form with health issue options
    health_issues = data['Health_Issue'].unique()
    return render_template('index.html', health_issues=health_issues)

if __name__ == '__main__':
    app.run(debug=True)
