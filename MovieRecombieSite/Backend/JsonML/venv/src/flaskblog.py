from flask import Flask,request, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from wtforms.validators import ValidationError
from config import mysql
import pandas as pd
import json
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
from scipy import optimize

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user'

mysql.init_app(app)
'''mysql = MySQL()

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user'

mysql.init_app(app)'''

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO login(username, password, email)VALUES(%s, %s, %s)''', (form.username.data, hashed_password, form.email.data))
        mysql.connection.commit()
        cur.close()
        flash('Account created for {}!'.format(form.username.data), 'success')
        return redirect(url_for('home'))
        flash('Some error occured while registering you.')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        if  cur.execute('''SELECT password FROM login WHERE username=%s''',(form.username.data,)):
            db_password = cur.fetchall()
            print(type(db_password), db_password)
            if bcrypt.check_password_hash(db_password[0][0], form.password.data):
                flash('Welcome {}!'.format(form.username.data), 'success')
                return redirect(url_for('home'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



N_FEATURES = 10
LAMBDA = 10
N_RECOMMEND = 10

movie_vector = pd.read_excel("movie_vector.xlsx")
actual_rating = pd.read_excel("actual_rating.xlsx")
#with open('new_user_rating.json') as new_user:
#    json_data = json.load(new_user)

avg_rating = np.nanmean(actual_rating.iloc[:,1:], axis=1)
temp = np.isnan(avg_rating)
avg_rating[temp] = 0

def reg_cost(theta_new2, *tup):
    theta_new = theta_new2.reshape(N_FEATURES, 1)
    new_user_rating, reg_con, movie_vector = tup
    with_reg = 0.5*np.nansum(np.square(np.dot(movie_vector.iloc[:,1:], theta_new)-new_user_rating))
    without_reg = reg_con*0.5*(sum(np.square(theta_new)))
    return with_reg+without_reg

def reg_gradient(theta_new2, *tup):
    theta_new = theta_new2.reshape(N_FEATURES, 1)
    new_user_rating, reg_con, movie_vector = tup
    temp2 = np.dot(movie_vector.iloc[:,1:], theta_new)-new_user_rating
    nan_loc = np.isnan(temp2)
    temp2[nan_loc] = 0
    theta_new_grad = np.dot(temp2.T, movie_vector.iloc[:,1:])+LAMBDA*theta_new.T
    return theta_new_grad.reshape(N_FEATURES)

def train_user(json_data, movie_vector, avg_rating):
    temp = json_data
    theta_new = np.random.rand(N_FEATURES)
    new_user_rating = pd.DataFrame(np.nan, index=movie_vector["movieId"], columns=range(1))
    for item in temp.keys():
        new_user_rating.loc[int(item)] = temp[item]
    new_user_rating = np.array(new_user_rating)-avg_rating.reshape(len(new_user_rating), 1)
    tup = new_user_rating, LAMBDA, movie_vector
    optimal_theta = optimize.fmin_cg(reg_cost, theta_new, fprime=reg_gradient, args=tup, full_output=True)
    return np.dot(movie_vector.iloc[:,1:], optimal_theta[0].reshape(10, 1))+avg_rating.reshape(len(avg_rating), 1)





app=Flask(__name__)
CORS(app)
result = pd.read_csv('./movies.csv',skiprows=1,names=["movieId","movie","genre"])
links_summary = pd.read_csv('./movies_info_spaces.csv')

genres= result["genre"]
genres=list(set(list(genres)))
genre=[]
for i in range(len(genres)):
	genre.extend(genres[i].split("|"))
genres=list(set(list(genre)))
genres.sort()
rows=list(result["movie"])
letter = "a"

all_data= pd.merge(result,links_summary,on="movieId")[["movie","imgLink","summary","genre","movieId"]]
real_data= all_data
all_data=list(real_data.values)
all_data=list(map(list,all_data))
sorted_data=sorted(all_data,key=lambda all_data:all_data[0])

movies_sort =[[] for y in range(27)]
for i in range(len(all_data)):
	pos=ord(all_data[i][0][0].lower())%97 if ord(all_data[i][0][0].lower())%97 < 26 else 26
	movies_sort[pos].append(all_data[i])

import ast
@app.route("/predict",methods=['POST'])
def predict():
	print("WORKING")
	temp = request.get_data();
	temp = temp.decode("ASCII")
	temp = ast.literal_eval(temp)
	new_user_rating = pd.DataFrame(train_user(temp, movie_vector, avg_rating), index=movie_vector["movieId"], columns=["temp_user"])
	recommend_movieId = pd.DataFrame(new_user_rating.sort_values(by="temp_user", ascending=False)[:N_RECOMMEND].index)
	print(recommend_movieId)
	#print(type(request.get_data()));
	#with open('new_user_rating.json', 'w') as json_file:
	#	json.dump(temp, json_file)
	return json.dumps(pd.DataFrame.to_string(recommend_movieId))


@app.route('/')
def hello_world():
	return json.dumps(sorted_data)


@app.route("/alpha/<character>")
def returnCharacter(character):
	page= request.args.get("page");
	page= page if page!=None else 1;
	pos= ord(character.lower())%97
	#movies_sort[pos].sort();
	print(movies_sort[0])
	return json.dumps(movies_sort[pos][0:(int(page)*10)])

@app.route('/search/<search>')
def searchResult(search):
	result=[]
	firstCharacter = search[0];
	pos= ord(firstCharacter.lower())%97
	for i in range(len(movies_sort[pos])):
		if (search.lower() in movies_sort[pos][i][0].lower().decode("utf-8")):
			result.append(movies_sort[pos][i])
	return json.dumps(result)
@app.route('/movieid/<search>')
def MovieSearch(search):
    result=[]
    for i in range(len(all_data)):
        b=int(search) ==int(all_data[i][4])
        if b:
	           return json.dumps(all_data[i])
@app.route('/genre/<search>')
def genreResult(search):
	page= request.args.get("page");
	page= page if page!=None else 1;
	search=str(search).split("&")
	twoway=real_data
	for i in range(len(search)):
		twoway= twoway[twoway["genre"].str.contains(search[i])]

	print(twoway)
	results= twoway.values
	results=list(map(list,results))

	if(len(result)==0):
		return "404"
	else:
		results.sort()
		return json.dumps(results[0:int(page)*10])

@app.route('/apiv1/getgenre')
def genreReturn():
	return json.dumps(genres)
@app.route('/login')
def login():
	return render_template('./login.html',title="login")
@app.route('/register')
def register():
	return render_template('./register.html',title="register")


if __name__ == '__main__':
    app.run(host="127.0.0.1",port=8002,debug=True)
