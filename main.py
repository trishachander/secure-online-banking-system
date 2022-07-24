from curses import keyname
from faulthandler import disable
from re import A
import string
from tkinter import DISABLED
from turtle import position
from certifi import where
import streamlit as st
import pandas as pd
import numpy as np
import time
import Modules.AlertNotification as alerts
import Modules.Admin as Admin
import Modules.Transactions as transac
import random
MONTH_TIME = 60*60*24*30
USD = 0.013
JPY = 1.673
EURO = 0.012

# Security
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()

#admin_data
ADMIN_USERNAME = "ewigsicuro"
ADMIN_PASSWORD = hashlib.sha256(str.encode("admin")).hexdigest()



def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

def randomnumber(N):
	minimum = pow(10, N-1)
	maximum = pow(10, N) - 1
	return random.randint(minimum, maximum)


# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT,accountno TEXT,balance INTEGER,loanamount INTEGER,loantime TEXT,loanstatus TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS transactionstable(username TEXT, transaction_amount INTEGER, transaction_type TEXT, transaction_time TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS personaltable(username TEXT, address TEXT, dob TEXT, name TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS aadhartable(username TEXT, aadhar INTEGER)')
	c.execute('CREATE TABLE IF NOT EXISTS exchangetable(username TEXT,USD TEXT, EURO TEXT, JPY TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS notificationtable(username TEXT, notifications TEXT, status TEXT,time TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS usercomplaints(username TEXT,complaint TEXT, type TEXT,time TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS userpayeetable(username TEXT, payee_name TEXT, payee_bank TEXT, payee_branch TEXT, payee_accno TEXT)')
	c.execute('CREATE TABLE IF NOT EXISTS checkingacctable(username TEXT, cardno INTEGER, balance INTEGER, last_payment TEXT, duedate TEXT)')


def add_userdata(username,password):
	#generate 10 len account number with mix of numbers and letters
	acc_no= ''.join(np.random.choice(list(string.ascii_letters + string.digits),10))
	c.execute('INSERT INTO userstable(username,password,accountno,balance,loanamount,loantime,loanstatus) VALUES (?,?,?,?,?,?,?)',(username,password,acc_no,0,0,"None","Not yet taken"))
	conn.commit()
	c.execute('INSERT INTO personaltable VALUES(?,?,?,?)',(username,"","",username))
	c.execute('INSERT INTO aadhartable VALUES(?,?)',(username,0))
	c.execute('INSERT INTO checkingacctable VALUES(?,?,?,?,?)',(username,randomnumber(10),0,"None","None"))
	alerts.InsertNotifications(username,c,"Hello "+username+", Welcome to Ewig Sicuro Bank.",conn)
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def CheckData(a,b,c,d):
	return len(a)>0 and len(b) > 0 and len(c) > 0 and len(d) > 0


def main():
	"""Erig Sicuro Bank"""

	#st.title("Erig Sicuro Bank")
	st.image("logo.png")
	menu = ["Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")
		if st.button("Profile"):
			st.write("In progress ... ")
	elif choice == "Login":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password',value="password")
		if st.sidebar.checkbox("Login or sign out") and password:
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)
			if username == ADMIN_USERNAME and hashed_pswd == ADMIN_PASSWORD:
				Admin.AdminControl(c,conn)
			else:
				st.subheader("Profile")
				col = st.columns(4)
				if col[0].checkbox("Notifications"):
					st.header("Notifications")
					alerts.RetrieveNotifications(username,c,conn)
					#if len(data[0])!=0:
					#	for i in data:
					#		st.success(i[0])
				if col[1].checkbox("Complaint/Review"):
					st.header("Complaint & Review Section\n")
					opt = ["Review","Complaint"]
					p = st.selectbox("Select the message type: ",opt)
					complaint = st.text_input("Enter the Complaint/Message")
					if st.button("Submit"):
						if len(complaint) > 2:
							Admin.SendComplaint(complaint,username,p,c,conn)
							st.success(p+" submitted.")
						else:
							st.error("Submission Failed")
				if col[2].checkbox("Transaction History"):
					st.header("Transaction History: "+username)
					options = ["All","Last 10 Transactions","Last 5 transactions","Last Transaction"]
					transac_opt = st.selectbox("Select an Option",options)
					c.execute('SELECT * FROM transactionstable WHERE username = ?',(username,))
					trans_opt_res = c.fetchall()
					switch_opt = {options[0]:1000000000,options[1]:10,options[2]:5,options[3]:1}
					trans_opt_res = trans_opt_res[::-1]
					trans_opt_res = trans_opt_res[:min(len(trans_opt_res),switch_opt[transac_opt])]
					#st.write(trans_opt_res)
					for e in trans_opt_res:
						st.write("\n****\n")
						st.write("Date & Time: "+e[3])
						st.write("Amount: "+str(e[1]))
						st.write("Transaction Type: "+e[2])
						st.write("\n******\n")

				c.execute('SELECT password FROM userstable WHERE username = ?',(username,))
				pass_or = c.fetchall()
				#st.write(make_hashes(password),pass_or[0][0])
				result = login_user(username,check_hashes(password,pass_or[0][0]))
				if result:
					#st.write((username))
					c.execute('SELECT * FROM personaltable')# WHERE username = '+username)
					dump = c.fetchall()
					c.execute('SELECT * FROM aadhartable WHERE username = ?',(username,))
					aadhar_data = c.fetchall()
					#st.write(aadhar_data)
					for x in dump:
						if x[0]==username:
							personal_details = x
					st.subheader("Personal Details")
					st.write("Name : ",personal_details[3])
					st.write("Date of Birth : ",personal_details[2])
					st.write("Address : ",personal_details[1])
					if aadhar_data[0][1]!=0:
						st.write("KYC Status: Confirmed")
						st.write("Aadhar Number : ",aadhar_data[0][1])
					else:
						st.write("Aadhar Status : Pending")
					st.write("\n**********\n")
					st.subheader("Account Details")
					#st.write("Logged In as {}".format(username))
					st.write("Account Number: {}".format(result[0][2]))
					st.write("Balance: {}".format(result[0][3]))
					if result[0][4]!=0:
						st.write("Loan Amount: {}".format(result[0][4]))
						st.write("Loan Time: {} Months".format(result[0][5]))
						st.write("Loan Status: {}".format(result[0][6]))
					st.write("\n\n")
					#if st.button("More Details . ."):
					#	st.write("Under Construction")
					st.write("\n********\n")
					if col[3].checkbox("Edit Personal Details"):
						st.header("Edit Details: ")
						new_name = st.text_input("Enter the Name : ",value=personal_details[3])
						new_dob = str(st.text_input("Enter the D.O.B format(DD-MM-YYY)",value=personal_details[2]))
						#d = st.date_input("Hello")
						#st.write(str(d))
						new_Address = st.text_input("Enter the Address : ",value=personal_details[1])
						new_password = st.text_input("Enter the New Password : ")
						#st.write(make_hashes(new_password))
						aadhar_number = st.number_input("Enter your Aadhar Number as  proof for these changes",min_value=0,value=0)
						if aadhar_number!=0:
							c.execute('UPDATE aadhartable SET aadhar = ? WHERE username = ?',(aadhar_number,username))
							c.execute('UPDATE personaltable SET name = ? WHERE username = ?',(new_name,username))
							c.execute('UPDATE personaltable SET dob = ? WHERE username = ?',(new_dob,username))
							c.execute('UPDATE personaltable SET address = ? WHERE username = ?',(new_Address,username))
							#time.sleep(10)
							if len(new_password)>0:
								c.execute('UPDATE userstable SET password = ? WHERE username = ?',(make_hashes(new_password),username))
							conn.commit()
						else:
							st.warning("User details won't be saved without entering the Aadhar Number !")
					# deposit and withdraw buttons
					st.sidebar.header("Menu")
					option = st.sidebar.radio(" ",("Transactions","Loans")) #Exchange Under Construction
					if option=="Transactions":
						st.sidebar.header("Transaction Options")
						opt7 = ["Savings","Checking"]
						res7 = st.sidebar.selectbox("Select Account Type",opt7)
						if st.sidebar.checkbox("Deposit"):
							amount = st.sidebar.number_input("Amount",min_value=0)
							transac.DepositTransaction(username,amount,c,conn,res7)

						if st.sidebar.checkbox("Withdraw"):
							amount = st.sidebar.number_input("Amount",min_value=0)
							# check wether sufficient balance is there or not
							transac.WithdrawTransaction(username,amount,c,conn,res7)

						# transfer money to other user
						if st.sidebar.checkbox("Transfer"):
							payee_options = ["None"]
							c.execute('SELECT * FROM userpayeetable WHERE username = ?',(username,))
							data6 = c.fetchall()
							#st.write(data6)
							for z in data6:
								payee_options.append(z[1])
							st.header("Money Transfer")
							payee_opt_res = st.selectbox("Select a Payee",payee_options)
							account_number = None
							amount = st.number_input("Amount",min_value=0)
							for b in data6:
								if b[1]==payee_opt_res:
									account_number = b[4]

							# check wether sufficient balance is there or not
							if payee_opt_res!="None":
								transac.MoneyTransfer(username,account_number,amount,c,conn)
							st.write("\n*****\n")
							st.subheader("Add a Payee")
							add_payee_name = st.text_input("Enter Name: ")
							add_payee_bank = st.text_input("Enter Bank Name: ")
							add_payee_branch = st.text_input("Enter Branch Name: ")
							ad_payee_account_no = st.text_input("Enter Account Number")
							if st.button("Add Payee") :
								if CheckData(add_payee_name,add_payee_bank,add_payee_branch,ad_payee_account_no):
									c.execute('SELECT * FROM userstable WHERE accountno = ?',(ad_payee_account_no,))
									data5 = c.fetchall()

									if(len(data5)==1):
										c.execute('INSERT INTO userpayeetable VALUES(?,?,?,?,?)',(username,add_payee_name,add_payee_bank,add_payee_branch,ad_payee_account_no))
										conn.commit()
										
									else:
										st.warning("Account Not Found . .")
								else:
									st.warning("Data Input Error . .")
							st.write("\n****\n")
							st.subheader("Remove a Payee")
							rem_payee = st.selectbox("Select a payee to remove",payee_options)
							if st.button("Remove Payee"):
								if rem_payee!="None":
									#payee_options.remove(rem_payee)
									c.execute('DELETE FROM userpayeetable WHERE payee_name = ?',(rem_payee,))
									conn.commit()
									st.write("Deletion Done . .")
						if st.sidebar.checkbox("Credit Card Status"):
							st.header("Credit Card Details")
							c.execute('SELECT * FROM checkingacctable WHERE username = ?',(username,))
							data7 = c.fetchall()
							#st.write(data7)
							data7 = data7[0]
							st.write("Credit Card Number: "+str(data7[1]))
							st.write("Balance: "+str(data7[2]))
							st.write("Last Payment: ",data7[3])
							st.write("Due Date: ",data7[4])
							st.write("\n***\n")

					# loan request
					if option=="Loans":
						st.sidebar.header("Loan Options")
						if st.sidebar.checkbox("Loan Request"):
							loan_amount = st.sidebar.number_input("Loan Amount",min_value=0)
							loan_time = st.sidebar.text_input("Loan Time",value="6")
							if loan_amount > 0:
								c.execute('UPDATE userstable SET balance = balance + ? WHERE username = ?',(loan_amount,username))
								conn.commit()
								c.execute('UPDATE userstable SET loanamount = ?,loantime = ?,loanstatus = ? WHERE username = ?',(loan_amount,loan_time,"Pending",username))
								conn.commit()
								c.execute('INSERT INTO transactionstable VALUES(?,?,?,?)',(username,loan_amount,"CREDIT",str(time.ctime())))
								conn.commit()
								alerts.InsertNotifications(username,c,"Amount of "+str(loan_amount)+" Has been credited to your account.",conn)
								st.success("Loan Requested")
							c.execute('SELECT * FROM userstable WHERE username = ?',(username,))
							data = c.fetchall()
							st.write("Loan Amount: {}".format(data[0][4]))
							st.write("Loan Time: {}".format(data[0][5]))
							st.write("Loan Status: {}".format(data[0][6]))
						
						# pay loan
						if st.sidebar.checkbox("Pay Loan"):
							loan_amount = st.sidebar.number_input("Loan Amount",min_value=0)
							c.execute('SELECT * FROM userstable WHERE username = ?',(username,))
							data = c.fetchall()
							pay_loan = data[0][4]
							if data[0][3] >= loan_amount and loan_amount > 0:
								status = "None"
								if pay_loan-loan_amount==0: status="Paid"
								else: status="Pending"
								c.execute('UPDATE userstable SET loanamount = ?,loanstatus = ? WHERE username = ?',(pay_loan-loan_amount,status,username))
								conn.commit()
								st.success("Loan Paid")
								c.execute('UPDATE userstable SET balance = balance - ? WHERE username = ?',(loan_amount,username))
								conn.commit()
								c.execute('INSERT INTO transactionstable VALUES(?,?,?,?)',(username,loan_amount,"CREDIT",str(time.ctime())))
								conn.commit()
								alerts.InsertNotifications(username,c,"Amount of "+str(loan_amount)+" Has been debited from your account.",conn)
								c.execute('SELECT * FROM userstable WHERE username = ?',(username,))
								data = c.fetchall()
								st.write("Loan Amount: {}".format(data[0][4]))
								st.write("Loan Time: {}".format(data[0][5]))
								st.write("Loan Status: {}".format(data[0][6]))
					if option=="Exchange":
						st.sidebar.header("Currencies")
						st.sidebar.warning("Under Construction . .")
						if st.sidebar.button("INR->USD"):
							dollars = st.sidebar.number_input("Enter the amount of INR you want to convert to USD:")
							c.execute('UPDATE userstable SET balance = balance - ? WHERE username = ?', (dollars,username))
							c.execute('UPDATE exchangetable SET USD = USD + ? WHERE username = ?',(dollars*USD,username))
							conn.commit()
						if st.sidebar.button("INR->EUR"):
							euros = st.sidebar.number_input("Enter the amount of INR you want to convert to EURO:")
							c.execute('UPDATE userstable SET balance = balance - ? WHERE username = ?', (euros,username))
							c.execute('UPDATE exchangetable SET EURO = EURO + ? WHERE username = ?',(euros*EURO,username))
							conn.commit()
						if st.sidebar.button("INR->JPY"):
							yen = st.sidebar.number_input("Enter the amount of INR you want to convert to JPY:")
							c.execute('UPDATE userstable SET balance = balance - ? WHERE username = ?', (yen,username))
							c.execute('UPDATE exchangetable SET JPY = JPY + ? WHERE username = ?',(yen*JPY,username))
							conn.commit()
						else:
							st.warning("Insufficient Balance")
					#print updated balance
					
				else:
					st.warning("Incorrect Username/Password")
		elif not password or not username :
			st.error("Login Error")


	elif choice == "SignUp":
			st.sidebar.subheader("Create New Account")
			new_user = st.sidebar.text_input("Create  Username")
			new_password = st.sidebar.text_input("Enter Password",type='password')
			again_password = st.sidebar.text_input("Re enter the password",type='password')
			
			if again_password == new_password:
				if st.sidebar.button("Signup"):
					create_usertable()
					add_userdata(new_user,make_hashes(new_password))
					st.sidebar.success("You have successfully created a valid Account")
					st.sidebar.info("Go to Login Menu to login")
			else:
				st.sidebar.warning("Passwords Don't match!")


if __name__ == '__main__':
	main()

