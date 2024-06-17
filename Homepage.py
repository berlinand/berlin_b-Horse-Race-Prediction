import streamlit as st
import easyocr as oc
from PIL import Image as im,ImageEnhance,ImageFilter
import io
import mysql.connector

# Change the connection value in the parameter and database name
connection=mysql.connector.connect(host='localhost',user="root",password="berlin10",database="bizcard")
mycursor=connection.cursor()

# This function extracts text from a given image and returns two lists based on the width of the image.
def reader_file(ab): 
        image_path=("temp.jpg")     
        reader=oc.Reader(['en'])
        read_img = reader.readtext(image_path)
        pil_img=im.open(image_path)
        a=[]
        b=[]
        for x in read_img :  
          if (x[0][0][0])<(pil_img.width/(2*ab))-((100)*ab):
             a.append(x)
          else:
            b.append(x)
        if len(a)<=2:
         a,b=b,a
        return a,b

# This function returns a sharpened image based on a value provided by the user.
def img_sharp(lef,sharp):
    img_sh = ImageEnhance.Sharpness(lef)
    en_img_sh = img_sh.enhance(sharp)
    return en_img_sh

# This function returns a brightenimage based on a value provided by the user.
def img_bright(en_img_sh,bright):
      img_br = ImageEnhance.Brightness(en_img_sh)
      en_img_br = img_br.enhance(bright) 
      return en_img_br

# This function returns a color intensity image based on a value provided by the user.
def img_col_intensity(en_img_br,col_intensity):
    img_col = ImageEnhance.Color(en_img_br)
    en_img_in =img_col.enhance(col_intensity)
    return en_img_in

# This function returns a sharpened image based on a value provided by the user.
def img_smooth(en_img_in,smooth):
    en_img_sm=en_img_in.filter(ImageFilter.GaussianBlur(radius=smooth))
    return en_img_sm

# This function returns a contrast image based on a value provided by the user.
def img_contrast(en_img_sm,contrast):
    img_con = ImageEnhance.Contrast(en_img_sm)
    en_img_con = img_con.enhance(contrast)
    return en_img_con

# This function returns a crop image based on a value provided by the user.
def img_crop(result,lefts, to, righ, botto,ab,ba):
   img=im.open(io.BytesIO(result))
   img=img.resize((img.width*ab,img.height*ba))
   widths=img.width
   heights=img.height
   left = (widths - widths+lefts-righ) // 2
   top = (heights- heights+to) // 2
   right =(widths+ widths-left-righ)  // 2
   bottom = (heights + heights-botto) // 2

   lef = img.crop((left, top, right, bottom))
   return lef,left, top, right, bottom

# This function returns the default value of a slider when the user clicks the default button0
def reset_slider(key):
    sharp=slider_place1.slider(label="Sharpness",min_value=-50.0,max_value=50.0,value=1.0,key=6+key) 
    bright=slider_place2.slider(label="Brightness",min_value=-50.0,max_value=50.0,value=1.0,key=7+key)
    col_intensity=slider_place3.slider(label="Color Intensity",min_value=-50.0,max_value=50.0, value=1.0,key=8+key)
    smooth=slider_place4.slider(label="Smoothness",min_value=-2.0,max_value=2.0, value=0.0,key=9+key)
    contrast=slider_place5.slider(label="Contrast",min_value=-50.0,max_value=50.0,value=1.0,key=10+key)
    lef_cr=slider_place6.slider(label="Left crop",min_value=0,max_value=200,value=0,key=13+key)
    top_cr=slider_place7.slider(label="Top crop",min_value=-0,max_value=200,value=0,key=14+key)
    rig_cr=slider_place8.slider(label="Right crop",min_value=0,max_value=200,value=0,key=15+key)
    bot_cr=slider_place9.slider(label="bottom crop",min_value=0,max_value=200,value=0,key=16+key)
    return sharp,bright,col_intensity,smooth,contrast,lef_cr,top_cr,rig_cr,bot_cr

#This function returns the default values from extracted data accoring to the widget 
def valu(a,b,ab):
     value1=a[0][1]
     value2=a[1][1]
     value3=[]
     value4=[]
     value5=[]
     value6=[]
     value7=[]
     
     for x in range(0,len(a)):
        
        kb=a[x][1].replace('-','').replace('+','')
        kb1=a[x][1]
        kb2=kb1[-6:]
        if kb.isdigit() and len(kb)>7:
           value3.append(a[x][1])
        if kb.find('@')!=-1:
           value4.append(a[x][1])
        if kb.find('www')!=-1 or kb.find("ww")!=-1  or kb.find("WW")!=-1 :
           value5.append(kb)
        if kb.find('.com')!=-1 and  kb.find("@")==-1 or kb.find('.Com')!=-1 and  kb.find("@")==-1 :
           value5.append(kb)
        if kb2.isdigit() and len(kb2)==6:
           c=a[x][0][1][1]
           for y in range(0,len(a)):
             if c-(12*ab)<a[y][0][3][1]<=c+(ab*12):   
               value6.append(a[y][1])
           value6.append(kb1)

     for z in range(0,len(b)):
        ka=b[z][1]
        value7.append(ka)
     if len(value5)==2:
      if value5[0]==value5[1]:
          value5=value5[0]
     return value1,value2,value3,value4,value5,value6,value7

#This function create a mysql table, if table is not there
def tab_sql():
    query1="show tables like '%biscard%'"
    com=mycursor.execute(query1)
    qresult=mycursor.fetchall()
    if len(qresult)==0:
       query2="""create table biscard_details(
          Id int auto_increment primary key,
          Name varchar(255),
          Designation varchar(255),
          mobile_1 varchar(255),
          mobile_2 varchar(255),
          Email varchar(255),
          Website varchar(255),
          Address varchar(500),
         Company_Name varchar(255),
         Original_Image longblob
         
                   )"""
       mycursor.execute(query2)
# This function saves the values in a MySQL table from a form when the submit button is clicked
def save_sql(name,occu,phone1,phone2,mail,web_site,address,company_name,result):
   name= st.session_state.value_1
   occu=st.session_state.value_2
   phone1=st.session_state.value_3
   phone2=st.session_state.value_4
   mail=st.session_state.value_5
   web_site=st.session_state.value_6
   address=st.session_state.value_7
   company_name=st.session_state.value_8


   query3="""insert into biscard_details(Name,Designation,mobile_1,mobile_2,Email,Website,Address,Company_Name,
            Original_Image) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
   val=(name, occu, phone1, phone2, mail, web_site, address, company_name, result)
   com3=mycursor.execute(query3,val)
   connection.commit()

tab_sql()
st.header("BizCardX: Extracting Business Card Data with OCR")
up_file=st.file_uploader(label="Upload the image",type=['png', 'jpg','jpeg'] )

co1,co2=st.columns(2)
ab=co1.number_input(label="width",min_value=1,max_value=50,value=1)
ba=co2.number_input(label="Height",min_value=1,max_value=50,value=1)
de=st.button(label="Original Image")
with st.sidebar: 
 slider_place1=st.empty()
 slider_place2=st.empty()
 slider_place3=st.empty()
 slider_place4=st.empty()
 slider_place5=st.empty()
 slider_place6=st.empty()
 slider_place7=st.empty()
 slider_place8=st.empty() 
 slider_place9=st.empty()

if de==False:
 sharp=slider_place1.slider(label="Sharpness",min_value=-50.0,max_value=50.0,value=1.0,key=1) 
 bright=slider_place2.slider(label="Brightness",min_value=-50.0,max_value=50.0,value=1.0,key=2)
 col_intensity=slider_place3.slider(label="Color Intensity",min_value=-50.0,max_value=50.0, value=1.0,key=3)
 smooth=slider_place4.slider(label="Smoothness",min_value=-2.0,max_value=2.0, value=0.0,key=4)
 contrast=slider_place5.slider(label="Contrast",min_value=-50.0,max_value=50.0,value=1.0,key=5)
 lef_cr=slider_place6.slider(label="Left crop",min_value=0,max_value=200,value=0,key=13)
 top_cr=slider_place7.slider(label="Top crop",min_value=0,max_value=200,value=0,key=14)
 rig_cr=slider_place8.slider(label="Right crop",min_value=0,max_value=200,value=0,key=15)
 bot_cr=slider_place9.slider(label="bottom crop",min_value=0,max_value=200,value=0,key=16)
if de==True:
  sharp=1.0
  bright=1.0
  col_intensity=1.0
  smooth=0.0
  contrast=1.0
  lef_cr=1.0
  rig_cr=1.0
  bot_cr=1.0
  top_cr=1.0
  key=+1
  sharp,bright,col_intensity,smooth,contrast,lef_cr,top_cr,rig_cr,bot_cr=reset_slider(key)
key_num=1
click1=st.button(label="Extract TEXT")


if 'value1' not in st.session_state:
   st.session_state.value_1=None
if 'value2' not in st.session_state:
   st.session_state.value_2=None
if 'value3' not in st.session_state:
   st.session_state.value_3=None
if 'value4' not in st.session_state:
   st.session_state.value_4=None
if 'value5' not in st.session_state:
   st.session_state.value_5=None
if 'value6' not in st.session_state:
   st.session_state.value_6=None
if 'value7' not in st.session_state:
   st.session_state.value_7=None
if 'value8' not in st.session_state:
   st.session_state.value_8=None


if up_file!= None:

  result=up_file.getvalue()

  lef,left, top, right, bottom=img_crop(result,lef_cr,top_cr,rig_cr,bot_cr,ab,ba)
  sh=img_sharp(lef,sharp) 
  br=img_bright(sh,bright)
  inten=img_col_intensity(br,col_intensity)
  sm=img_smooth(inten,smooth)
  con=img_contrast(sm,contrast)
  st.image(con)
  

  if click1==True and up_file!= None:
    with st.spinner('please Wait' ): 
     c=con.convert('RGB')
     c.save('temp.jpg')         
     a,b=reader_file(ab)

  
     value1,value2,value3,value4,value5,value6,value7=valu(a,b,ab)
     value4="".join(value4)
     value5="".join(value5)
     value6=" ".join(value6)
     value7=" ".join(value7)
     st.session_state.value_1=value1
     st.session_state.value_2=value2
     if len(value3)==1:
       st.session_state.value_3=value3[0]
       st.session_state.value_4="NA"
     else:
       st.session_state.value_3=value3[0]
       st.session_state.value_4=value3[1]    
     st.session_state.value_5=value4
     st.session_state.value_6=value5
     st.session_state.value_7=value6
     st.session_state.value_8=value7
     key_num+=1
     with st.form(key=f"form1{key_num}") : 
      co3,co4=st.columns(2)
      co5,co6=st.columns(2)
      co7,co8=st.columns(2)      
      
      name=co3.text_input(label="Cardholder Name",key="value_1")
      
      occu=co4.text_input(label="Designation",key="value_2")

      phone1=co5.text_input(label="Mobile 1",key="value_3")
      phone2=co6.text_input(label="Mobile 2",key="value_4")  
  
      mail=co7.text_input(label="Email",key="value_5")
      web_site=co8.text_input(label="website Link",key="value_6")
      address= st.text_input(label="Address",key="value_7")
      company_name=st.text_input(label="Company Name",key="value_8")
      click2=st.form_submit_button(label="Submit",on_click=save_sql, args=(name,occu,phone1,phone2,mail,web_site,address,company_name,result)) 

