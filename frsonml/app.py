from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('food_data.csv')

# Fill missing values in Health_Issue
data['Health_Issue'] = data['Health_Issue'].fillna('General')

# Prepare for OneHotEncoder
features = ['Health_Issue', 'Climate', 'Restaurant', 'Veg_Non']
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')  # Use sparse_output=False
encoded_features = encoder.fit_transform(data[features])

# Calculate cosine similarity matrix
cosine_sim = cosine_similarity(encoded_features)

@app.route('/hello')
def hello():
    return render_template('hello.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user inputs
        name = request.form.get('name')
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        health_issue = request.form.get('health_issue')
        climate = request.form.get('climate')
        restaurant = request.form.get('restaurant')

        # Validate inputs, replace empty strings with default values
        health_issue = health_issue if health_issue else 'General'  # Default to 'General'
        climate = climate if climate else 'Any'  # Default to 'Any'
        restaurant = restaurant if restaurant else 'Any'  # Default to 'Any'

        # Determine Veg/Non-Veg based on weight (for example)
        veg_non = 'Veg' if weight and float(weight) < 60 else 'Non-Veg'  # Example condition for Veg/Non-Veg

        # Create a user input DataFrame for encoding
        user_input = pd.DataFrame({
            'Health_Issue': [health_issue],
            'Climate': [climate],
            'Restaurant': [restaurant],
            'Veg_Non': [veg_non]
        })

        # Encode user input
        user_encoded = encoder.transform(user_input)

        # Calculate cosine similarity scores
        user_similarities = cosine_similarity(user_encoded, encoded_features)

        # Get the indices of the most similar food items
        similar_indices = user_similarities.argsort()[0][-10:][::-1]

        # Get recommendations that match the user's health issue
        recommendations = data.iloc[similar_indices]
        recommendations = recommendations[recommendations['Health_Issue'] == health_issue]

        # If no recommendations match the health issue, fallback to general recommendations
        if recommendations.empty:
            recommendations = data[data['Health_Issue'] == 'General'].iloc[similar_indices]

        # Prepare data for visualizations
        calories = recommendations['Calories'].tolist()
        proteins = recommendations['Protein'].tolist()
        veg_nonveg_counts = recommendations['Veg_Non'].value_counts()
        restaurant_counts = recommendations['Restaurant'].value_counts()
        climate_counts = recommendations['Climate'].value_counts()

        # Create visualizations
        pie_fig_calories_proteins = px.pie(
            names=['Calories', 'Proteins'],
            values=[sum(calories), sum(proteins)],
            title='Total Calories vs Proteins for Recommended Foods',
            color_discrete_sequence=['#FF9999', '#66B3FF']
        )

        # Restaurant percentages pie chart
        restaurant_fig = px.pie(
            names=restaurant_counts.index,
            values=restaurant_counts.values,
            title='Percentage of Food by Restaurant',
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # Climate percentages pie chart
        climate_fig = px.pie(
            names=climate_counts.index,
            values=climate_counts.values,
            title='Percentage of Food by Climate',
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        # Veg/Non-Veg percentages pie chart
        veg_nonveg_fig = px.pie(
            names=veg_nonveg_counts.index,
            values=veg_nonveg_counts.values,
            title='Percentage of Veg and Non-Veg',
            color_discrete_sequence=['#2E8B57', '#A52A2A']
        )

        # Save pie chart figures
        combined_pie_chart_path = 'static/pie_chart_calories_proteins.html'
        pio.write_html(pie_fig_calories_proteins, file=combined_pie_chart_path, auto_open=False)

        restaurant_pie_chart_path = 'static/restaurant_pie_chart.html'
        pio.write_html(restaurant_fig, file=restaurant_pie_chart_path, auto_open=False)

        climate_pie_chart_path = 'static/climate_pie_chart.html'
        pio.write_html(climate_fig, file=climate_pie_chart_path, auto_open=False)

        veg_nonveg_pie_chart_path = 'static/veg_nonveg_pie_chart.html'
        pio.write_html(veg_nonveg_fig, file=veg_nonveg_pie_chart_path, auto_open=False)

        # Climate conditions bar graph
        climate_counts_df = climate_counts.reset_index()
        climate_counts_df.columns = ['Climate', 'Count']
        climate_color_map = {'summer': 'orange', 'winter': 'blue', 'rainy': 'green'}
        climate_bar_fig = px.bar(
            climate_counts_df, x='Climate', y='Count', title='Food Count by Climate Condition',
            labels={'Climate': 'Climate', 'Count': 'Count'}, color='Climate', color_discrete_map=climate_color_map
        )
        climate_bar_chart_path = 'static/climate_bar_chart.html'
        pio.write_html(climate_bar_fig, file=climate_bar_chart_path, auto_open=False)

        # Restaurant conditions bar graph
        restaurant_counts_df = restaurant_counts.reset_index()
        restaurant_counts_df.columns = ['Restaurant', 'Count']
        restaurant_bar_fig = px.bar(
            restaurant_counts_df, x='Restaurant', y='Count', title='Food Count by Restaurant',
            labels={'Restaurant': 'Restaurant', 'Count': 'Count'}, color='Restaurant'
        )
        restaurant_bar_chart_path = 'static/restaurant_bar_chart.html'
        pio.write_html(restaurant_bar_fig, file=restaurant_bar_chart_path, auto_open=False)

        return render_template('results.html', recommendations=recommendations.to_dict(orient='records'),
                               combined_pie_chart_path=combined_pie_chart_path,
                               restaurant_pie_chart_path=restaurant_pie_chart_path,
                               climate_pie_chart_path=climate_pie_chart_path,
                               veg_nonveg_pie_chart_path=veg_nonveg_pie_chart_path,
                               climate_bar_chart_path=climate_bar_chart_path,
                               restaurant_bar_chart_path=restaurant_bar_chart_path)

    health_issues = data['Health_Issue'].unique()
    climates = data['Climate'].dropna().unique()
    restaurants = data['Restaurant'].dropna().unique()
    return render_template('index.html', health_issues=health_issues, climates=climates, restaurants=restaurants)

if __name__ == '__main__':
    app.run(debug=True)
