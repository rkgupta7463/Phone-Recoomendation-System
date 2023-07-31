from flask import Flask,render_template,request
import pickle as pkl
import pandas as pd

# init the application
app = Flask(__name__)

##dataframe initilization
df=pd.read_csv("models/dataset.csv")
# print(len(df['name'].unique()))
# print(df.head())

##initilazing the model
similarity=pkl.load(open("models/Similarity_Matrix_1.pkl","rb"))

##Recommedation Function
def recommend_descriptions_photos(phone):
    phone_index = df[df['name'] == phone].index
    if len(phone_index) == 0:
        print("Phone not found in the dataset.")
        return []

    phone_index = phone_index[0]
    distances = similarity[phone_index]
    phoneLists = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_phones = []
    for i in phoneLists:
        recommended_phone_name = df.iloc[i[0]]['name']
        recommended_phone_imgurl = df.iloc[i[0]]['imgURL']
        recommended_phone_price = df.iloc[i[0]]['price']
        recommended_phones.append((recommended_phone_name, recommended_phone_imgurl,recommended_phone_price))

    return recommended_phones


def selected_phone_details(phone_name):
    # Find the index of the phone with the given name in the DataFrame
    phone_index = df[df['name'] == phone_name].index

    if not phone_index.empty:
        # Fetch the details for the phone using the index
        name = df['name'].iloc[phone_index]
        price = df['price'].iloc[phone_index]
        description = df['corpus'].iloc[phone_index]
        imgURL = df['imgURL'].iloc[phone_index]
        rating = df['ratings'].iloc[phone_index]

        

        # Return the details as a dictionary
        phone_details = {
            'name': name.values[0],
            'price': price.values[0],
            'corpus': description.values[0],
            'imgURL': imgURL.values[0],
            'ratings': rating.values[0]
        }
        return phone_details
    
    else:
        # Return None if the phone name is not found in the DataFrame
        return None

# Test the function with the provided phone name
phone_name = "OnePlus Nord CE 2 5G (Gray Mirror, 128 GB)"
# details = selected_phone_details(phone_name)
# if details:
#     print("Phone Name:", details['name'])
#     print("Price:", details['price'])
#     print("Description:", details['corpus'])
#     print("imgURL:", details['imgURL'])
#     print("Rating:", details['ratings'])
# else:
#     print("Phone not found in the DataFrame.")


@app.route('/',methods=['GET','POST'])
def home():
    t50_name=[]
    imurl=[]
    t50price=[]
    rs=[]
    selected_phone_name=None
    r_Name=[]
    r_price=[]
    r_imageURL=[]
    selected_name=None
    selected_img=None
    selected_price=None
    selected_rating=None
    selected_details_phone=None
    selected_corpus=None
    top_50_df=df.sample(40).sort_values(by='price',ascending=False)
    phone_name_uniques=df['name'].unique()
    
    ## fetching the phone name from the front-end
    if request.method=="POST":
        selected_phone_name=request.form.get('phone-name')
        # print(phone_name)
        rs=recommend_descriptions_photos(selected_phone_name)
        
        for n in range(0,10):
            r_Name.append(rs[n][0])
            r_imageURL.append(rs[n][1])
            r_price.append(rs[n][2])

    ##geting the details of selected phone name
    details = selected_phone_details(selected_phone_name)
    if details:
        corpus=details['corpus'].split()
        corpus_f=' '.join(corpus)
        selected_name=details['name']
        selected_price=details['price']
        selected_corpus=corpus_f
        selected_img=details['imgURL']
        selected_rating=details['ratings']
    else:
        print("Phone not found in the DataFrame.")

    ##t50 name , price, imgURL geting 
    for n in top_50_df['name']:
        t50_name.append(n)

    for n in top_50_df['price']:
        t50price.append(n)

    for n in top_50_df['imgURL']:
        imurl.append(n)

    t50_phone = list(zip(t50_name, t50price, imurl))

    recommeded_phone = list(zip(r_Name, r_imageURL, r_price))

    context={
        'pn':phone_name_uniques,
        'selected_phone':selected_phone_name,
        't50n':t50_name,
        't50price':t50price,
        't50im':imurl,
        'phone_t50':t50_phone,
        'recommeded':recommeded_phone,
        'sname':selected_name,
        'sprice':selected_price,
        'simgURL':selected_img,
        'srating':selected_rating,
        'scorpus':selected_corpus
    }
    return render_template('index.html',context=context)
    # return "Hello Phone Recommendations!"

if __name__ == '__main__':
    app.run()