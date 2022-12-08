from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################


@app.route('/')
def plants_list():
    """Display the plants list page."""

    plants_data = mongo.db.plants_data.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)


@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        name = request.form['plant_name']
        variety = request.form['variety']
        photo = request.form['photo']
        date = request.form['date_planted']

        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo,
            'date_planted': date
        }

        mongo.db.plants_data.insert_one(new_plant)
        return redirect(url_for('detail', plant_id=new_plant['id']))

    else:
        return render_template('create.html')


@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = mongo.db.plants_data.find_one({'_id': ObjectId(plant_id)})

    search = mongo.db.harvests_data.find({'id': plant_to_show})
    harvests = []
    for data in search:
        harvests.append(data)

    context = {
        'plant': plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)


@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    new_harvest = {
        'quantity': request.form['harvested_amount'],  # e.g. '3 tomatoes'
        'date': request.form['date_planted'],
        'plant_id': plant_id
    }

    mongo.db.harvests_data.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))


@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        name = request.form['plant_name']
        variety = request.form['variety']
        photo = request.form['photo']
        date = request.form['date_planted']
        search_param = {'_id': ObjectId(plant_id)}
        change_param = {'$set': {
            'name': name,
            'variety': variety,
            'photo_url': photo,
            'date_planted': date
        }}
        mongo.db.plants_data.upgrade_one(search_param, change_param)

        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = mongo.db.plants_data.find_one(plant_id)

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)


@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    deleted_plant = mongo.db.plants_data.delete_one(
        {'_id': ObjectId(plant_id)})
    mongo.db.harvests_data.delete_many({'plant_id': plant_id})
    return redirect(url_for('plants_list'))


if __name__ == '__main__':
    app.run(debug=True, port=3000)
