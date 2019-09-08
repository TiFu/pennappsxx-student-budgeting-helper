# Student Budget Helper
Link on DevPost: https://devpost.com/software/receiptscannerbot

## Inspiration
A major problem when it comes to finances for students is maintaining their budgets. Saving receipts and budgeting manually can be quite burdensome. Additionally, this process is quite inefficient. That is why we wanted to create a program where people can easily scan their receipts and our program would be able to optimally budget their finance and accurately categorize the items which there buying.

## What it does
Our program functions on three main parts. Firstly, it scans an user's uploaded receipt and analyzes the text for the items bought. The items are then categorized by our program to a certain list in which the program calculates how much money you are spending in each category. Based on the budget that you are trying to maintain, the bot informs the user through telegram about the details of their purchase and how well you are doing related to their budget goals. Overall, this program provides in detailed information about your budget and expenses by simply scanning your receipt.

## How we built it
This program was built using technologies like AWS and Rekognition to develop the backend program which analyzed and categorized the scanned data receipt. A chatbot in the Telegraph was written in Python to provide users details about their budget.

## Challenges we ran into
The main challenge we ran into was translating the receipt's image into text. As Amazon Rekognition is quite sensitive to image quality, we invested a lot of time into preprocessing the images to guarantee the best possible OCR result. Another issue we faced was displaying all the analyzed information through a bot in Telegram. In order to do this, we needed to get the data containing the cost and name of the items from the array of dictionaries. In the end, we were able to select each component and display it as needed.

## Accomplishments that we're proud of
We are proud that in such a short span of time, we were able to meet the goals of our desired programs. As most of this technology was new to most of the members, it was an accomplishment to successfully code the program. Additionally, we used several different technologies that we were exposed to during the workshops and challenges.

## What we learned
We all were able to delve deep into areas out of our comfort zones and see the workings behind apps we have previously used on our phones (Telegram). We were able to not only create a new bot on Telegram but also program it to respond to input relative to the input that the user gave it. Additionally, we were able to use different technologies like AWS Rekognition and RNN and implemented them all together to make one coherent program.
